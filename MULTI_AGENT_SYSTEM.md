# Multi-Agent System Documentation

## Overview

Le projet B2P.AI a été transformé en un **système multi-agent unifié** qui orchestre intelligemment toutes les fonctionnalités IA via une seule API. Au lieu de coder chaque feature séparément, le système route automatiquement vos demandes vers l'agent approprié.

## Architecture

### Agents Disponibles

1. **Task Prioritization Agent**
   - Prioritise les tâches basées sur l'urgence, deadlines, effort, et productivité
   - Mots-clés: "prioritize", "priority", "urgent", "important", "order"

2. **Burnout Detection Agent**
   - Surveille et prédit les risques de burnout
   - Mots-clés: "burnout", "stress", "wellbeing", "health", "tired"

3. **Workload Balancing Agent**
   - Balance la charge de travail équitablement dans les équipes
   - Mots-clés: "balance", "distribute", "workload", "equitable", "fair"

4. **Task Extraction Agent**
   - Extrait les tâches depuis emails, notes de réunion, et documents
   - Mots-clés: "extract", "parse", "analyze text", "find tasks"

5. **Recognition Agent**
   - Détecte et reconnaît automatiquement les accomplissements
   - Mots-clés: "recognition", "achievement", "accomplishment", "milestone"

## API Endpoints

### 1. Execute Agent Task (Principal)

```http
POST /api/v1/agent/execute
```

**Body:**
```json
{
  "task": "What should I work on next?",
  "context": {
    "employee_id": 1
  },
  "auto_detect": true
}
```

**Response:**
```json
{
  "success": true,
  "agent_used": "Task Prioritization Agent",
  "result": {...},
  "message": "Successfully prioritized 10 tasks",
  "suggestions": [
    "Focus on high-priority tasks first",
    "Consider delegating low-priority tasks"
  ]
}
```

### 2. Smart Assist (Interface Simplifiée)

```http
POST /api/v1/agent/smart-assist?query=Am I at risk of burnout?&employee_id=1
```

Interface simplifiée qui construit automatiquement le contexte.

### 3. Get Available Agents

```http
GET /api/v1/agent/available
```

Retourne la liste de tous les agents disponibles avec leurs descriptions.

### 4. Get Examples

```http
GET /api/v1/agent/examples
```

Obtient des exemples de requêtes pour chaque type d'agent.

### 5. Batch Execute

```http
POST /api/v1/agent/batch
```

**Body:**
```json
[
  {
    "task": "Prioritize my tasks",
    "context": {"employee_id": 1}
  },
  {
    "task": "Check burnout risk",
    "context": {"employee_id": 1}
  }
]
```

Exécute plusieurs requêtes en lot.

### 6. Execute Workflow (Workflows Pré-définis)

```http
POST /api/v1/agent/workflow?workflow_type=daily_briefing&employee_id=1
```

**Workflows Disponibles:**
- `daily_briefing`: Priorités + Burnout + Achievements
- `team_health`: Balance équipe + Risques burnout

## Utilisation Frontend

### Interface AI Assistant

Naviguez vers `/ai-assistant` pour accéder à l'interface conversationnelle du multi-agent.

**Features:**
- Chat interface naturelle
- Quick actions pour les tâches courantes
- Auto-détection intelligente de l'agent approprié
- Suggestions contextuelles
- Support multi-contexte (employee_id, team_id, text)

### Exemples de Requêtes

```javascript
import { multiAgentService } from './services/multiAgentService';

// Exemple 1: Prioritisation simple
const response = await multiAgentService.smartAssist(
  "What should I work on next?",
  employeeId
);

// Exemple 2: Check burnout
const burnoutCheck = await multiAgentService.executeTask({
  task: "Am I stressed?",
  context: { employee_id: 1 },
  auto_detect: true
});

// Exemple 3: Workflow complet
const dailyBriefing = await multiAgentService.executeWorkflow(
  "daily_briefing",
  employeeId
);

// Exemple 4: Extraction de tâches
const extracted = await multiAgentService.executeTask({
  task: "Extract tasks from this email",
  context: {
    text: "Please review the PR and update the docs by Friday."
  }
});
```

## Architecture Backend

### Orchestrateur (`MultiAgentOrchestrator`)

L'orchestrateur est le cerveau du système:

```python
from app.services.multi_agent_system import orchestrator, AgentRequest

# Détection automatique
request = AgentRequest(
    task="Balance team workload",
    context={"team_id": 1},
    auto_detect=True
)

response = await orchestrator.execute(request)
```

### Système de Scoring

Chaque agent retourne un score de confiance (0-1) pour déterminer s'il peut gérer la requête. L'orchestrateur sélectionne l'agent avec le score le plus élevé.

### Extension du Système

Pour ajouter un nouvel agent:

1. Créer une classe héritant de `Agent`:

```python
class MyCustomAgent(Agent):
    def __init__(self):
        super().__init__(
            name="My Custom Agent",
            description="Does something awesome"
        )
        self.service = MyCustomService()

    async def can_handle(self, task: str, context: Dict) -> float:
        keywords = ["custom", "awesome"]
        task_lower = task.lower()
        return max([0.9 if k in task_lower else 0.0 for k in keywords] + [0.0])

    async def execute(self, task: str, context: Dict) -> AgentResponse:
        result = self.service.do_something(context)
        return AgentResponse(
            success=True,
            agent_used=self.name,
            result=result,
            message="Success!",
            suggestions=["Try this", "Try that"]
        )
```

2. Ajouter au `MultiAgentOrchestrator`:

```python
class MultiAgentOrchestrator:
    def __init__(self):
        self.agents = [
            TaskPrioritizationAgent(),
            BurnoutDetectionAgent(),
            # ... autres agents
            MyCustomAgent()  # Nouveau agent
        ]
```

## Avantages du Système Multi-Agent

1. **Une seule API**: Plus besoin de gérer plusieurs endpoints
2. **Auto-détection**: Le système route automatiquement vers le bon agent
3. **Extensible**: Ajoutez facilement de nouveaux agents
4. **Intelligent**: Suggestions contextuelles et workflows composés
5. **Maintenable**: Code organisé et découplé
6. **Scalable**: Agents indépendants et parallélisables

## Design Frontend Amélioré

### Thème Moderne

- Gradient backgrounds (Purple/Blue)
- Ombres douces et élégantes
- Animations smooth (hover effects, transitions)
- Typographie Inter avec poids variables
- Cards avec hover effects (lift & shadow)
- Boutons avec gradients
- Bordures arrondies (16px)

### Composants Clés

1. **AIAssistant.tsx**: Interface chat avec le multi-agent
2. **multiAgentService.ts**: Service API TypeScript
3. **App.tsx**: Thème Material-UI amélioré
4. **Layout.tsx**: Navigation avec AI Assistant

## Configuration

### Backend

Le système est automatiquement disponible dès que le backend démarre. Aucune configuration supplémentaire n'est nécessaire.

### Frontend

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Testing

### Test du Multi-Agent System

```bash
# Démarrer le backend
cd backend
uvicorn app.main:app --reload

# Démarrer le frontend
cd frontend
npm start

# Accéder à l'interface
http://localhost:3000/ai-assistant
```

### Test via API directement

```bash
# Get available agents
curl http://localhost:8000/api/v1/agent/available

# Execute a task
curl -X POST http://localhost:8000/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Prioritize my tasks",
    "context": {"employee_id": 1},
    "auto_detect": true
  }'

# Smart assist
curl -X POST "http://localhost:8000/api/v1/agent/smart-assist?query=Am%20I%20stressed?&employee_id=1"

# Workflow
curl -X POST "http://localhost:8000/api/v1/agent/workflow?workflow_type=daily_briefing&employee_id=1"
```

## Swagger Documentation

Visitez `http://localhost:8000/docs` pour la documentation interactive complète de l'API multi-agent.

## Prochaines Étapes

1. Ajouter plus d'agents spécialisés
2. Implémenter le machine learning pour améliorer la détection
3. Ajouter des agents conversationnels avec mémoire
4. Intégration avec services externes (Slack, Email, Calendar)
5. Système de feedback pour améliorer les agents

---

**Made with AI for better workplace wellbeing**
