"""
Model Trainer - Train custom NER and classification models for task extraction
"""
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

try:
    import spacy
    from spacy.training import Example
    from spacy.util import minibatch, compounding
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


class TaskNERTrainer:
    """
    Trainer for custom Named Entity Recognition model for task extraction

    This trainer helps create custom NER models that can identify:
    - TASK_ACTION: Action verbs in tasks
    - DEADLINE: Deadline expressions
    - ASSIGNEE: Person assigned to task
    - PROJECT: Project names
    - PRIORITY: Priority/urgency indicators
    """

    def __init__(
        self,
        base_model: str = "fr_core_news_lg",
        output_dir: Optional[Path] = None
    ):
        """
        Initialize the trainer

        Args:
            base_model: Base spaCy model to fine-tune
            output_dir: Directory to save trained model
        """
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy is required for training. Install with: pip install spacy")

        self.base_model = base_model
        self.output_dir = output_dir or Path("models/custom_ner")
        self.nlp = None

    def prepare_training_data(
        self,
        data_file: Path
    ) -> Tuple[List[Example], List[Example]]:
        """
        Load and prepare training data from JSON file

        Expected JSON format:
        [
            {
                "text": "Développer l'API REST avant vendredi",
                "entities": [
                    {"start": 0, "end": 10, "label": "TASK_ACTION"},
                    {"start": 26, "end": 34, "label": "DEADLINE"}
                ]
            },
            ...
        ]

        Args:
            data_file: Path to training data JSON file

        Returns:
            Tuple of (training_examples, validation_examples)
        """
        if not data_file.exists():
            raise FileNotFoundError(f"Training data not found: {data_file}")

        with open(data_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # Load base model
        self.nlp = spacy.load(self.base_model)

        # Add NER if not present
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner")
        else:
            ner = self.nlp.get_pipe("ner")

        # Add entity labels
        labels = set()
        for item in raw_data:
            for entity in item.get("entities", []):
                labels.add(entity["label"])

        for label in labels:
            ner.add_label(label)

        logger.info(f"Added {len(labels)} entity labels: {labels}")

        # Convert to spaCy format
        examples = []
        for item in raw_data:
            doc = self.nlp.make_doc(item["text"])
            entities = []

            for ent in item.get("entities", []):
                span = doc.char_span(
                    ent["start"],
                    ent["end"],
                    label=ent["label"],
                    alignment_mode="contract"
                )
                if span:
                    entities.append(span)

            doc.ents = entities
            example = Example.from_dict(doc, {"entities": [(e.start_char, e.end_char, e.label_) for e in entities]})
            examples.append(example)

        # Split into train/validation (80/20)
        random.shuffle(examples)
        split_idx = int(len(examples) * 0.8)
        train_examples = examples[:split_idx]
        val_examples = examples[split_idx:]

        logger.info(f"Prepared {len(train_examples)} training examples and {len(val_examples)} validation examples")

        return train_examples, val_examples

    def train(
        self,
        train_examples: List[Example],
        val_examples: List[Example],
        n_iter: int = 30,
        dropout: float = 0.2,
        batch_size: int = 8
    ) -> Dict[str, float]:
        """
        Train the NER model

        Args:
            train_examples: Training examples
            val_examples: Validation examples
            n_iter: Number of training iterations
            dropout: Dropout rate
            batch_size: Batch size

        Returns:
            Dictionary with training metrics
        """
        if not self.nlp:
            raise ValueError("Model not initialized. Call prepare_training_data first.")

        # Get the NER component
        ner = self.nlp.get_pipe("ner")

        # Disable other pipes during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.resume_training()

            best_val_score = 0.0
            metrics = {
                "final_loss": 0.0,
                "best_val_score": 0.0,
                "iterations": n_iter
            }

            logger.info(f"Starting training for {n_iter} iterations...")

            for iteration in range(n_iter):
                random.shuffle(train_examples)
                losses = {}

                # Batch the examples
                batches = minibatch(train_examples, size=compounding(4.0, batch_size, 1.001))

                for batch in batches:
                    self.nlp.update(
                        batch,
                        drop=dropout,
                        losses=losses,
                        sgd=optimizer
                    )

                # Evaluate on validation set
                if val_examples and (iteration + 1) % 5 == 0:
                    val_score = self._evaluate(val_examples)
                    logger.info(
                        f"Iteration {iteration + 1}/{n_iter} - "
                        f"Loss: {losses.get('ner', 0):.4f}, "
                        f"Val Score: {val_score:.4f}"
                    )

                    if val_score > best_val_score:
                        best_val_score = val_score
                        metrics["best_val_score"] = best_val_score

                metrics["final_loss"] = losses.get('ner', 0)

            logger.info(f"Training completed. Best validation score: {best_val_score:.4f}")

        return metrics

    def _evaluate(self, examples: List[Example]) -> float:
        """
        Evaluate model on examples

        Args:
            examples: Validation examples

        Returns:
            F1 score
        """
        from spacy.scorer import Scorer

        scorer = Scorer()

        for example in examples:
            pred = self.nlp(example.reference.text)
            example.predicted = pred
            scorer.score([example])

        scores = scorer.scores
        return scores.get("ents_f", 0.0)

    def save_model(self, output_dir: Optional[Path] = None):
        """
        Save trained model to disk

        Args:
            output_dir: Directory to save model. If None, uses self.output_dir
        """
        if not self.nlp:
            raise ValueError("No model to save. Train a model first.")

        output_path = output_dir or self.output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        self.nlp.to_disk(output_path)
        logger.info(f"Model saved to {output_path}")

        # Save metadata
        metadata = {
            "base_model": self.base_model,
            "labels": list(self.nlp.get_pipe("ner").labels),
            "model_version": "1.0.0"
        }

        metadata_file = output_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Metadata saved to {metadata_file}")

    def load_model(self, model_dir: Path):
        """
        Load a trained model from disk

        Args:
            model_dir: Directory containing the model
        """
        if not model_dir.exists():
            raise FileNotFoundError(f"Model not found: {model_dir}")

        self.nlp = spacy.load(model_dir)
        logger.info(f"Model loaded from {model_dir}")

    def test_model(self, text: str) -> Dict:
        """
        Test the model on a text sample

        Args:
            text: Text to analyze

        Returns:
            Dictionary with extracted entities
        """
        if not self.nlp:
            raise ValueError("No model loaded. Load or train a model first.")

        doc = self.nlp(text)

        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })

        return {
            "text": text,
            "entities": entities
        }


def create_training_data_template(output_file: Path):
    """
    Create a template JSON file for training data

    Args:
        output_file: Path to save the template
    """
    template = [
        {
            "text": "Développer l'API REST pour le module de facturation avant vendredi",
            "entities": [
                {"start": 0, "end": 10, "label": "TASK_ACTION"},
                {"start": 48, "end": 62, "label": "DEADLINE"}
            ]
        },
        {
            "text": "Jean doit préparer la présentation pour la réunion client urgent",
            "entities": [
                {"start": 0, "end": 4, "label": "ASSIGNEE"},
                {"start": 10, "end": 18, "label": "TASK_ACTION"},
                {"start": 59, "end": 65, "label": "PRIORITY"}
            ]
        },
        {
            "text": "Tester les nouvelles fonctionnalités du projet Alpha",
            "entities": [
                {"start": 0, "end": 6, "label": "TASK_ACTION"},
                {"start": 44, "end": 53, "label": "PROJECT"}
            ]
        },
        {
            "text": "Envoyer le rapport mensuel à Marie avant la fin du mois",
            "entities": [
                {"start": 0, "end": 7, "label": "TASK_ACTION"},
                {"start": 29, "end": 34, "label": "ASSIGNEE"},
                {"start": 35, "end": 56, "label": "DEADLINE"}
            ]
        },
        {
            "text": "Organiser une réunion de planification sprint cette semaine",
            "entities": [
                {"start": 0, "end": 9, "label": "TASK_ACTION"},
                {"start": 47, "end": 60, "label": "DEADLINE"}
            ]
        }
    ]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"Training data template created: {output_file}")
    print("\nEntity labels used:")
    print("  - TASK_ACTION: Action verbs (développer, préparer, tester, etc.)")
    print("  - DEADLINE: Deadline expressions (avant vendredi, cette semaine, etc.)")
    print("  - ASSIGNEE: Person assigned to the task")
    print("  - PROJECT: Project names")
    print("  - PRIORITY: Priority indicators (urgent, important, etc.)")
    print("\nAdd more examples following this format to improve model accuracy.")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python trainer.py create-template <output_file>")
        print("  python trainer.py train <training_data_file>")
        print("  python trainer.py test <model_dir> '<text>'")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-template":
        output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("training_data.json")
        create_training_data_template(output_file)

    elif command == "train":
        if len(sys.argv) < 3:
            print("Error: training data file required")
            sys.exit(1)

        data_file = Path(sys.argv[2])
        trainer = TaskNERTrainer()

        print("Preparing training data...")
        train_examples, val_examples = trainer.prepare_training_data(data_file)

        print("Training model...")
        metrics = trainer.train(train_examples, val_examples)

        print(f"\nTraining complete!")
        print(f"  Final loss: {metrics['final_loss']:.4f}")
        print(f"  Best validation score: {metrics['best_val_score']:.4f}")

        print("\nSaving model...")
        trainer.save_model()
        print("Done!")

    elif command == "test":
        if len(sys.argv) < 4:
            print("Error: model directory and test text required")
            sys.exit(1)

        model_dir = Path(sys.argv[2])
        test_text = sys.argv[3]

        trainer = TaskNERTrainer()
        trainer.load_model(model_dir)

        print(f"\nTesting text: {test_text}\n")
        result = trainer.test_model(test_text)

        print("Extracted entities:")
        for ent in result["entities"]:
            print(f"  - {ent['text']:30s} [{ent['label']}]")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
