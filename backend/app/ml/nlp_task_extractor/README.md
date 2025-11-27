# NLP Task Extractor

Advanced Natural Language Processing module for extracting tasks from unstructured text (emails, meeting notes, chat messages, etc.).

## Features

- **Task Extraction**: Automatically identify tasks from natural language text
- **Named Entity Recognition**: Extract task components (action, object, assignee, deadline, priority)
- **Deadline Parsing**: Understand and parse various deadline formats
- **Urgency Detection**: Automatically detect task urgency/priority
- **Effort Estimation**: Estimate task effort based on description
- **Confidence Scoring**: Each extracted task includes a confidence score
- **Multilingual Support**: Works with French and English text
- **Custom Model Training**: Train custom NER models for your specific domain
- **Caching**: Built-in caching for improved performance

## Architecture

```
nlp_task_extractor/
├── __init__.py              # Module initialization
├── config.py                # Configuration classes
├── extractor.py             # Main TaskExtractor class
├── training/                # Model training utilities
│   ├── __init__.py
│   └── trainer.py           # TaskNERTrainer for custom models
├── data/                    # Training and test data
│   ├── README.md
│   └── training_data_example.json
└── models/                  # Trained models (created after training)
```

## Quick Start

### Installation

1. Install required packages:
```bash
cd backend
pip install -r requirements.txt
```

2. Download spaCy models:
```bash
python scripts/setup_nlp_models.py
```

Or manually:
```bash
python -m spacy download fr_core_news_lg
python -m spacy download en_core_web_lg
```

### Basic Usage

```python
from app.ml.nlp_task_extractor import TaskExtractor

# Initialize extractor
extractor = TaskExtractor()

# Extract tasks from text
text = """
Bonjour,

Pouvez-vous développer l'API REST pour le module de facturation avant vendredi ?
Il faut aussi contacter le client pour la réunion.

Merci
"""

tasks = extractor.extract_tasks(text, source_type="email")

# Process extracted tasks
for task in tasks:
    print(f"Task: {task.text}")
    print(f"  Action: {task.action}")
    print(f"  Deadline: {task.deadline}")
    print(f"  Urgency: {task.urgency}")
    print(f"  Confidence: {task.confidence:.2f}")
    print()
```

### Custom Configuration

```python
from app.ml.nlp_task_extractor import TaskExtractor, NLPConfig

# Create custom configuration
config = NLPConfig(
    spacy_model="fr_core_news_lg",
    min_confidence=0.7,
    enable_caching=True,
    cache_size=200
)

# Initialize with custom config
extractor = TaskExtractor(config=config)
```

## Configuration Options

The `NLPConfig` class provides extensive configuration options:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `spacy_model` | `"fr_core_news_lg"` | spaCy model to use |
| `primary_language` | `"fr"` | Primary language (fr or en) |
| `min_confidence` | `0.6` | Minimum confidence score (0-1) |
| `max_task_length` | `200` | Maximum task title length |
| `min_task_words` | `4` | Minimum words for valid task |
| `enable_caching` | `True` | Enable result caching |
| `cache_size` | `100` | Maximum cache entries |

See [config.py](config.py) for all available options.

## Task Entity Structure

Extracted tasks are returned as `TaskEntity` objects with the following attributes:

```python
@dataclass
class TaskEntity:
    text: str                          # Task description
    action: Optional[str]              # Main action verb
    object: Optional[str]              # Object of the action
    assignee: Optional[str]            # Person assigned
    deadline: Optional[datetime]       # Parsed deadline
    urgency: int                       # Urgency level (1-5)
    estimated_effort: Optional[float]  # Estimated hours
    confidence: float                  # Confidence score (0-1)
    source_sentence: str               # Original sentence
    entities: List[Dict]               # Extracted entities
```

## Training Custom Models

### 1. Prepare Training Data

Create a JSON file with annotated examples:

```json
[
  {
    "text": "Développer l'API REST avant vendredi",
    "entities": [
      {"start": 0, "end": 10, "label": "TASK_ACTION"},
      {"start": 26, "end": 40, "label": "DEADLINE"}
    ]
  }
]
```

Entity labels:
- `TASK_ACTION`: Action verbs
- `DEADLINE`: Deadline expressions
- `ASSIGNEE`: Person names
- `PROJECT`: Project names
- `PRIORITY`: Priority indicators

### 2. Train the Model

```bash
python -m app.ml.nlp_task_extractor.training.trainer train data/my_training_data.json
```

Or programmatically:

```python
from pathlib import Path
from app.ml.nlp_task_extractor.training import TaskNERTrainer

# Initialize trainer
trainer = TaskNERTrainer(
    base_model="fr_core_news_lg",
    output_dir=Path("models/custom_ner")
)

# Prepare data
train_examples, val_examples = trainer.prepare_training_data(
    Path("data/training_data.json")
)

# Train
metrics = trainer.train(train_examples, val_examples, n_iter=30)

# Save model
trainer.save_model()
```

### 3. Use Custom Model

```python
from app.ml.nlp_task_extractor import TaskExtractor, NLPConfig

config = NLPConfig(
    custom_ner_model=Path("models/custom_ner")
)

extractor = TaskExtractor(config=config)
```

## Advanced Features

### Deadline Detection

The extractor understands various deadline formats:

```python
# Relative dates
"aujourd'hui" / "today"           → Today
"demain" / "tomorrow"             → Tomorrow
"cette semaine" / "this week"     → End of current week
"la semaine prochaine"            → End of next week
"dans 3 jours" / "in 3 days"      → 3 days from now

# Absolute dates
"25/12/2024"                      → December 25, 2024
"avant le 15/03"                  → March 15 (current year)
"by 2024-12-31"                   → December 31, 2024
```

### Urgency Detection

Automatically detects urgency levels (1-5):

```python
Level 5 (Critical): "urgent", "asap", "immédiat", "critique", "emergency"
Level 4 (High):     "important", "prioritaire", "priority", "soon"
Level 3 (Normal):   "normal", "standard"
Level 2 (Low):      "when possible", "si possible", "low priority"
Level 1 (Later):    "someday", "eventually", "un jour"
```

### Effort Estimation

Estimates task effort in hours based on keywords and complexity:

- **Complex tasks** (8h): "développer", "implement", "migrate", "refactor"
- **Medium tasks** (4h): "analyser", "prepare", "research", "design"
- **Simple tasks** (1h): "send", "contact", "check", "validate"

### Caching

Built-in caching improves performance for repeated extractions:

```python
# Enable caching (enabled by default)
config = NLPConfig(
    enable_caching=True,
    cache_size=100
)

extractor = TaskExtractor(config=config)

# Clear cache when needed
extractor.clear_cache()

# Get cache statistics
stats = extractor.get_stats()
print(f"Cache size: {stats['cache_size']}")
```

## API Reference

### TaskExtractor

Main class for task extraction.

#### Methods

**`__init__(config: Optional[NLPConfig] = None)`**

Initialize the extractor.

**`extract_tasks(text: str, source_type: str = "email") -> List[TaskEntity]`**

Extract tasks from text.

- `text`: Input text to analyze
- `source_type`: Type of source ("email", "meeting", "chat", etc.)
- Returns: List of TaskEntity objects

**`clear_cache()`**

Clear the extraction cache.

**`get_stats() -> Dict`**

Get extractor statistics.

### TaskNERTrainer

Trainer for custom NER models.

#### Methods

**`prepare_training_data(data_file: Path) -> Tuple[List[Example], List[Example]]`**

Load and prepare training data.

**`train(train_examples, val_examples, n_iter=30) -> Dict[str, float]`**

Train the NER model.

**`save_model(output_dir: Optional[Path] = None)`**

Save trained model to disk.

**`load_model(model_dir: Path)`**

Load a trained model.

**`test_model(text: str) -> Dict`**

Test model on sample text.

## Testing

Run the test suite:

```bash
# Run all tests
pytest backend/tests/test_nlp_extractor.py -v

# Run specific test class
pytest backend/tests/test_nlp_extractor.py::TestTaskExtractor -v

# Run with coverage
pytest backend/tests/test_nlp_extractor.py --cov=app.ml.nlp_task_extractor
```

## Performance Considerations

### Model Selection

- **Large models** (`fr_core_news_lg`, `en_core_web_lg`):
  - Better accuracy
  - Slower processing (~100-200ms per text)
  - Recommended for production

- **Small models** (`fr_core_news_sm`, `en_core_web_sm`):
  - Lower accuracy
  - Faster processing (~50-100ms per text)
  - Good for development/testing

### Optimization Tips

1. **Enable caching** for repeated extractions
2. **Batch processing** for multiple texts:
   ```python
   texts = ["task 1", "task 2", "task 3"]
   all_tasks = [extractor.extract_tasks(t) for t in texts]
   ```
3. **Use appropriate model size** based on your needs
4. **Adjust confidence threshold** to balance precision/recall

## Troubleshooting

### Model Not Found Error

```
OSError: Can't find model 'fr_core_news_lg'
```

**Solution**: Download the model:
```bash
python -m spacy download fr_core_news_lg
```

### Low Extraction Quality

1. **Increase training data**: Add more annotated examples
2. **Adjust confidence threshold**: Lower `min_confidence`
3. **Train custom model**: For domain-specific vocabulary
4. **Check language setting**: Ensure correct language is configured

### Memory Issues

1. **Use smaller models**: Switch to `_sm` models
2. **Reduce cache size**: Set `cache_size` to lower value
3. **Disable caching**: Set `enable_caching=False`
4. **Process in batches**: Don't load all texts at once

## Integration with B2P.AI

The NLP Task Extractor integrates with the main B2P.AI system through the `TaskExtractionService`:

```python
# In app/services/task_extraction_service.py
from app.ml.nlp_task_extractor import TaskExtractor

class TaskExtractionService:
    def __init__(self):
        self.nlp_extractor = TaskExtractor()

    def extract_from_email(self, email_body: str, email_subject: str = ""):
        full_text = f"{email_subject}\n\n{email_body}"
        tasks = self.nlp_extractor.extract_tasks(full_text, source_type="email")
        return self._convert_to_task_candidates(tasks)
```

## Contributing

When contributing to the NLP module:

1. **Add tests** for new features
2. **Update documentation** for API changes
3. **Maintain backward compatibility** when possible
4. **Follow code style**: Run `black` and `flake8`
5. **Add training examples** for new entity types

## References

- [spaCy Documentation](https://spacy.io/usage)
- [spaCy Training](https://spacy.io/usage/training)
- [Named Entity Recognition](https://spacy.io/usage/linguistic-features#named-entities)
- [Dependency Parsing](https://spacy.io/usage/linguistic-features#dependency-parse)

## License

MIT License - See main project LICENSE file.
