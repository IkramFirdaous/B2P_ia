# NLP Task Extractor - Quick Start Guide

Get started with the NLP Task Extractor in 5 minutes!

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Download spaCy Models

**Automatic setup:**
```bash
python scripts/setup_nlp_models.py
```

**Manual setup:**
```bash
# French model (recommended for French text)
python -m spacy download fr_core_news_lg

# English model (recommended for English text)
python -m spacy download en_core_web_lg
```

## Basic Usage

### Example 1: Extract from Email

```python
from app.ml.nlp_task_extractor import TaskExtractor

# Initialize
extractor = TaskExtractor()

# Email text
email_text = """
Bonjour,

Pouvez-vous développer l'API REST pour le module de facturation avant vendredi ?
Il faut aussi tester l'intégration avec le système de paiement.

Merci
"""

# Extract tasks
tasks = extractor.extract_tasks(email_text, source_type="email")

# Display results
for task in tasks:
    print(f"✓ {task.text}")
    print(f"  Urgency: {task.urgency}/5")
    print(f"  Deadline: {task.deadline}")
    print(f"  Confidence: {task.confidence:.0%}")
    print()
```

**Output:**
```
✓ Développer l'API REST pour le module de facturation avant vendredi
  Urgency: 3/5
  Deadline: 2024-12-22 23:59:59
  Confidence: 85%

✓ Tester l'intégration avec le système de paiement
  Urgency: 3/5
  Deadline: None
  Confidence: 78%
```

### Example 2: Extract from Meeting Notes

```python
meeting_notes = """
Meeting Notes - Sprint Planning

Action Items:
1. Jean - Développer la nouvelle feature authentification
2. Marie - Tester l'API REST
3. Pierre - Mettre à jour la documentation technique urgent

Next meeting: Friday
"""

tasks = extractor.extract_tasks(meeting_notes, source_type="meeting")

for task in tasks:
    print(f"Task: {task.text}")
    if task.assignee:
        print(f"  Assigned to: {task.assignee}")
    print()
```

### Example 3: Custom Configuration

```python
from app.ml.nlp_task_extractor import TaskExtractor, NLPConfig

# Create custom config
config = NLPConfig(
    min_confidence=0.7,        # Higher confidence threshold
    primary_language="fr",      # French primary
    enable_caching=True        # Enable caching for speed
)

# Initialize with custom config
extractor = TaskExtractor(config=config)

# Use as normal
tasks = extractor.extract_tasks("Créer les tests unitaires urgent")
```

## Understanding Results

Each extracted task contains:

```python
task.text              # "Développer l'API REST"
task.action            # "développer"
task.object            # "API REST"
task.assignee          # "Jean" (if mentioned)
task.deadline          # datetime(2024, 12, 22, 23, 59, 59)
task.urgency           # 1-5 (1=low, 5=critical)
task.estimated_effort  # hours (e.g., 4.0)
task.confidence        # 0.0-1.0 (e.g., 0.85)
task.entities          # List of all detected entities
```

## Common Use Cases

### Use Case 1: Filter High-Priority Tasks

```python
tasks = extractor.extract_tasks(text)

# Get only urgent tasks
urgent_tasks = [t for t in tasks if t.urgency >= 4]

# Get tasks with deadlines
tasks_with_deadlines = [t for t in tasks if t.deadline is not None]

# Get high-confidence tasks
reliable_tasks = [t for t in tasks if t.confidence >= 0.8]
```

### Use Case 2: Integrate with Database

```python
from app.models.task import Task
from app.core.database import SessionLocal

# Extract tasks
tasks = extractor.extract_tasks(email_text)

# Save to database
db = SessionLocal()
for task_entity in tasks:
    if task_entity.confidence >= 0.7:  # Only save confident extractions
        db_task = Task(
            title=task_entity.text,
            urgency=task_entity.urgency,
            deadline=task_entity.deadline,
            estimated_effort=task_entity.estimated_effort
        )
        db.add(db_task)

db.commit()
```

### Use Case 3: Batch Processing

```python
# Process multiple emails
emails = [
    "Email 1: Développer l'API...",
    "Email 2: Tester la feature...",
    "Email 3: Déployer sur production..."
]

all_tasks = []
for email in emails:
    tasks = extractor.extract_tasks(email)
    all_tasks.extend(tasks)

print(f"Extracted {len(all_tasks)} tasks from {len(emails)} emails")
```

## Supported Date Formats

The extractor understands:

```python
"aujourd'hui" / "today"           → Today
"demain" / "tomorrow"             → Tomorrow
"cette semaine" / "this week"     → End of this week
"la semaine prochaine"            → End of next week
"dans 3 jours" / "in 3 days"      → 3 days from now
"25/12/2024"                      → December 25, 2024
"avant le 15/03"                  → March 15
```

## Supported Urgency Keywords

```python
Critical (5): "urgent", "asap", "immédiat", "critique", "emergency"
High (4):     "important", "prioritaire", "priority"
Normal (3):   "normal", "standard"
Low (2):      "when possible", "si possible"
Later (1):    "someday", "eventually"
```

## Troubleshooting

### Problem: No tasks extracted

**Solutions:**
1. Check if text contains action verbs
2. Lower confidence threshold: `config.min_confidence = 0.5`
3. Check minimum word count: `config.min_task_words = 3`

### Problem: Too many false positives

**Solutions:**
1. Increase confidence threshold: `config.min_confidence = 0.8`
2. Train a custom model with your specific data
3. Filter results by confidence score

### Problem: Wrong language detected

**Solution:**
```python
config = NLPConfig(
    spacy_model="en_core_web_lg",  # For English
    primary_language="en"
)
```

### Problem: Slow performance

**Solutions:**
1. Enable caching: `config.enable_caching = True`
2. Use smaller model: `config.spacy_model = "fr_core_news_sm"`
3. Process in batches instead of one-by-one

## Next Steps

1. **Read the full documentation**: See [README.md](README.md)
2. **Train a custom model**: See [data/README.md](data/README.md)
3. **Run tests**: `pytest backend/tests/test_nlp_extractor.py`
4. **Explore examples**: Check `training/trainer.py` for more examples

## Getting Help

- **Documentation**: See [README.md](README.md)
- **Training Guide**: See [data/README.md](data/README.md)
- **Issues**: Report at project repository
- **spaCy Docs**: https://spacy.io/usage

## Example: Complete Integration

```python
from app.ml.nlp_task_extractor import TaskExtractor, NLPConfig
from datetime import datetime

def process_email(email_body: str, email_subject: str):
    """
    Complete example: Extract and process tasks from email
    """
    # Initialize extractor
    config = NLPConfig(min_confidence=0.7)
    extractor = TaskExtractor(config=config)

    # Combine subject and body
    full_text = f"{email_subject}\n\n{email_body}"

    # Extract tasks
    tasks = extractor.extract_tasks(full_text, source_type="email")

    # Process results
    results = {
        "total_tasks": len(tasks),
        "urgent_tasks": [],
        "tasks_with_deadlines": [],
        "all_tasks": []
    }

    for task in tasks:
        task_info = {
            "text": task.text,
            "urgency": task.urgency,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "confidence": round(task.confidence, 2),
            "estimated_hours": task.estimated_effort
        }

        results["all_tasks"].append(task_info)

        # Flag urgent tasks
        if task.urgency >= 4:
            results["urgent_tasks"].append(task_info)

        # Flag tasks with deadlines
        if task.deadline:
            results["tasks_with_deadlines"].append(task_info)

    return results


# Usage
email = """
Subject: Action Items from Client Meeting

Hi team,

Following up on today's meeting:
- Développer l'API REST urgent
- Préparer la présentation client avant vendredi
- Contacter le support technique

Thanks!
"""

results = process_email(email, "Action Items from Client Meeting")
print(f"Found {results['total_tasks']} tasks")
print(f"Urgent: {len(results['urgent_tasks'])}")
print(f"With deadlines: {len(results['tasks_with_deadlines'])}")
```

Happy extracting!
