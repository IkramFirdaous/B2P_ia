# Training Data for NLP Task Extractor

This directory contains training data for custom NER models.

## Entity Labels

The model recognizes the following entity types:

- **TASK_ACTION**: Action verbs indicating tasks (développer, créer, tester, etc.)
- **DEADLINE**: Time expressions indicating deadlines (avant vendredi, cette semaine, etc.)
- **ASSIGNEE**: Person assigned to the task (names)
- **PROJECT**: Project or system names (Alpha, Phoenix, etc.)
- **PRIORITY**: Priority indicators (urgent, important, critique, etc.)

## File Format

Training data should be in JSON format with the following structure:

```json
[
  {
    "text": "Développer l'API REST pour le module de facturation avant vendredi",
    "entities": [
      {"start": 0, "end": 10, "label": "TASK_ACTION"},
      {"start": 48, "end": 62, "label": "DEADLINE"}
    ]
  }
]
```

Where:
- `text`: The full sentence or text containing the task
- `entities`: List of entities with:
  - `start`: Character position where entity starts
  - `end`: Character position where entity ends
  - `label`: Entity type (one of the labels above)

## Creating Training Data

1. Use the template generator:
   ```bash
   python -m app.ml.nlp_task_extractor.training.trainer create-template my_data.json
   ```

2. Manually annotate text:
   - Copy `training_data_example.json` as a starting point
   - Add more examples following the same format
   - Use a tool like [Doccano](https://github.com/doccano/doccano) or [Label Studio](https://labelstud.io/) for annotation

3. Aim for:
   - At least 100 examples for basic model
   - 500+ examples for production-grade model
   - Balanced representation of all entity types
   - Mix of French and English if bilingual support needed

## Training the Model

Once you have training data, train the model:

```bash
cd backend
python -m app.ml.nlp_task_extractor.training.trainer train path/to/training_data.json
```

The trained model will be saved in `backend/app/ml/nlp_task_extractor/models/`

## Tips for Good Training Data

1. **Diverse Examples**: Include various task types, writing styles, and formats
2. **Edge Cases**: Include ambiguous or tricky examples
3. **Context Variety**: Mix short and long sentences
4. **Realistic Data**: Use actual examples from emails and meetings when possible
5. **Consistency**: Be consistent in how you label similar entities
6. **Balance**: Try to have similar amounts of each entity type

## Example Sources

Good sources for training data:
- Project management tool exports (Jira, Asana, etc.)
- Email archives (with proper anonymization)
- Meeting notes and minutes
- Task lists and TODO items
- Sprint planning documents
