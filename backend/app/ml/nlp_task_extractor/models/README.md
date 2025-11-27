# Trained Models Directory

This directory stores custom-trained NLP models for task extraction.

## Structure

After training, this directory will contain:

```
models/
├── custom_ner/              # Custom NER model
│   ├── config.cfg           # spaCy model configuration
│   ├── meta.json            # Model metadata
│   ├── ner/                 # NER component
│   │   ├── cfg
│   │   ├── model
│   │   └── moves
│   ├── tokenizer
│   ├── vocab/
│   └── metadata.json        # Training metadata
└── README.md                # This file
```

## Training a Model

To train a custom model:

```bash
cd backend
python -m app.ml.nlp_task_extractor.training.trainer train data/training_data.json
```

The trained model will be saved in `models/custom_ner/` by default.

## Using a Trained Model

```python
from pathlib import Path
from app.ml.nlp_task_extractor import TaskExtractor, NLPConfig

# Configure to use custom model
config = NLPConfig(
    custom_ner_model=Path("app/ml/nlp_task_extractor/models/custom_ner")
)

# Initialize extractor
extractor = TaskExtractor(config=config)

# Use normally
tasks = extractor.extract_tasks("Développer l'API REST")
```

## Model Metadata

Each trained model includes a `metadata.json` file with:

```json
{
  "base_model": "fr_core_news_lg",
  "labels": ["TASK_ACTION", "DEADLINE", "ASSIGNEE", "PROJECT", "PRIORITY"],
  "model_version": "1.0.0"
}
```

## Model Versioning

When training new versions:

1. Save with version number:
   ```python
   trainer.save_model(Path("models/custom_ner_v2"))
   ```

2. Update configuration to use new version:
   ```python
   config = NLPConfig(custom_ner_model=Path("models/custom_ner_v2"))
   ```

3. Keep old versions for rollback if needed

## Model Size

Trained models typically range from:
- **Small models**: 10-50 MB
- **Large models**: 100-500 MB

The size depends on:
- Base model size
- Vocabulary size
- Number of entity labels
- Training data size

## Best Practices

1. **Version Control**: Don't commit large models to git
   - Add `models/*.pkl` to `.gitignore`
   - Use Git LFS for model versioning if needed

2. **Model Registry**: For production, use a model registry:
   - MLflow
   - Weights & Biases
   - AWS S3 / Azure Blob Storage

3. **Testing**: Always test new models before deploying:
   ```bash
   python -m app.ml.nlp_task_extractor.training.trainer test models/custom_ner "Test text"
   ```

4. **Documentation**: Document model changes:
   - Training data used
   - Performance metrics
   - Known limitations

## Troubleshooting

### Model Not Loading

**Error**: `Can't find model 'custom_ner'`

**Solution**: Check that the model directory exists and contains required files:
```bash
ls -R models/custom_ner/
```

### Model Performance Issues

If extraction quality is poor:

1. **More training data**: Add more annotated examples
2. **Balance labels**: Ensure all entity types are represented
3. **Retrain**: Use more iterations (n_iter=50 or higher)
4. **Check base model**: Ensure compatible language model

### Memory Issues

Large models can use significant memory:

1. **Use smaller base model**: Train from `fr_core_news_sm` instead of `lg`
2. **Reduce batch size**: Lower batch_size during training
3. **Disable unused pipes**: Only load necessary components

## Model Comparison

Compare model performance:

```python
from app.ml.nlp_task_extractor.training import TaskNERTrainer

# Load models
trainer_v1 = TaskNERTrainer()
trainer_v1.load_model(Path("models/custom_ner_v1"))

trainer_v2 = TaskNERTrainer()
trainer_v2.load_model(Path("models/custom_ner_v2"))

# Test on same text
test_text = "Développer l'API REST avant vendredi"

result_v1 = trainer_v1.test_model(test_text)
result_v2 = trainer_v2.test_model(test_text)

print("V1 entities:", result_v1["entities"])
print("V2 entities:", result_v2["entities"])
```

## Example: Production Model Management

```python
import shutil
from pathlib import Path
from datetime import datetime

def deploy_model(model_dir: Path, version: str):
    """
    Deploy a trained model to production
    """
    # Backup current production model
    prod_model = Path("models/production")
    if prod_model.exists():
        backup_dir = Path(f"models/backups/production_{datetime.now():%Y%m%d_%H%M%S}")
        shutil.copytree(prod_model, backup_dir)
        print(f"Backed up to {backup_dir}")

    # Deploy new model
    if prod_model.exists():
        shutil.rmtree(prod_model)
    shutil.copytree(model_dir, prod_model)

    # Update version file
    with open(prod_model / "version.txt", "w") as f:
        f.write(version)

    print(f"Deployed {version} to production")


# Usage
deploy_model(Path("models/custom_ner_v2"), "2.0.0")
```

## Resources

- [spaCy Model Training](https://spacy.io/usage/training)
- [Custom NER](https://spacy.io/usage/training#ner)
- [Model Packaging](https://spacy.io/usage/training#models-generating)
