# Architecture B2P.AI - Documentation Technique

## Vue d'ensemble

B2P.AI utilise une **architecture en couches** avec un **système multi-agent** pour orchestrer les fonctionnalités IA.

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React + TS)                 │
│  Dashboard | AI Assistant | Tasks | Team | Analytics   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────┴────────────────────────────────────┐
│              API Layer (FastAPI)                        │
│  /api/v1/agent/* | /api/v1/tasks/* | /api/v1/analytics/*│
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│           Multi-Agent Orchestrator                      │
│    (Intelligent routing via keyword matching)           │
└─────┬──────┬──────┬──────┬──────┬───────────────────────┘
      │      │      │      │      │
      ▼      ▼      ▼      ▼      ▼
   ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐
   │TP │  │BD │  │WB │  │TE │  │RG │  Agents
   └─┬─┘  └─┬─┘  └─┬─┘  └─┬─┘  └─┬─┘
     │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼
   ┌──────────────────────────────────┐
   │      Services Layer              │
   │  (Business Logic + DB Access)    │
   └───────────┬──────────────────────┘
               │
   ┌───────────┴──────────────────────┐
   │  Database Layer (PostgreSQL)      │
   │  Models: Task, Employee, Team,    │
   │  BurnoutMetric, Achievement       │
   └───────────────────────────────────┘
```

**Légende** :
- TP = Task Prioritization
- BD = Burnout Detection
- WB = Workload Balancing
- TE = Task Extraction (NLP)
- RG = Recognition (Achievements)

---

## Couches de l'Architecture

### 1. Frontend Layer

**Technologies** : React 18, TypeScript, Material-UI, Axios

**Structure** :
```
frontend/src/
├── pages/           # Page components (routing)
│   ├── Dashboard.tsx
│   ├── AIAssistant.tsx
│   ├── TaskManagement.tsx
│   ├── TeamView.tsx
│   └── Analytics.tsx
├── components/      # Reusable UI components
│   ├── Layout.tsx
│   ├── TaskCard.tsx
│   └── BurnoutAlert.tsx
├── services/        # API client services
│   ├── multiAgentService.ts
│   ├── taskService.ts
│   └── analyticsService.ts
└── types/          # TypeScript type definitions
    ├── task.ts
    └── agent.ts
```

**Flux de données** :
```
User Action → Component → Service (Axios) → API → Service → Component → UI Update
```

**État** : Gestion locale avec `useState` et `useContext` (pas de Redux)

---

### 2. API Layer

**Technologies** : FastAPI, Pydantic

**Structure** :
```
backend/app/api/v1/
├── agent.py         # Multi-agent endpoints ✨
├── tasks.py         # Task CRUD + prioritization
├── analytics.py     # Burnout + workload + achievements
└── employees.py     # Employee management
```

**Pattern** : Dependency Injection pour les sessions DB
```python
@router.post("/tasks")
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)  # ✅ Injection
):
    service = TaskService(db)
    return service.create(task_data)
```

---

### 3. Multi-Agent Orchestrator

**Fichier** : [backend/app/services/multi_agent_system.py](backend/app/services/multi_agent_system.py)

**Concept** : Un système unifié qui route les requêtes vers l'agent approprié.

### Architecture

```python
class Agent(ABC):
    """Classe de base pour tous les agents"""
    async def can_handle(task: str, context: dict) -> float
    async def execute(task: str, context: dict, db: Session) -> AgentResponse

class MultiAgentOrchestrator:
    """Orchestrateur principal"""
    agents: List[Agent]

    async def select_agent(task: str, context: dict) -> Agent
    async def execute(request: AgentRequest, db: Session) -> AgentResponse
```

### Agents Disponibles

| Agent | Mots-clés | Service Utilisé | Nécessite DB |
|-------|-----------|-----------------|--------------|
| **TaskPrioritizationAgent** | prioritize, urgent, important, rank | TaskPrioritizationService | ✅ |
| **BurnoutDetectionAgent** | burnout, stress, tired, wellbeing | BurnoutDetectionService | ✅ |
| **WorkloadBalancingAgent** | balance, workload, fair, distribute | WorkloadBalancingService | ✅ |
| **TaskExtractionAgent** | extract, email, meeting notes | TaskExtractionService | ❌ (NLP only) |
| **RecognitionAgent** | achievement, accomplishment, reward | RecognitionService | ✅ |

### Flux d'exécution

```
1. Requête utilisateur → POST /api/v1/agent/execute
   {
     "task": "What should I work on next?",
     "context": {"employee_id": 1},
     "auto_detect": true
   }

2. Orchestrateur calcule le score de confiance pour chaque agent
   TaskPrioritizationAgent.can_handle() → 0.9
   BurnoutDetectionAgent.can_handle() → 0.0
   ...

3. Sélection de l'agent avec le score le plus élevé (>0.5)
   Agent sélectionné: TaskPrioritizationAgent

4. Exécution avec session DB
   agent.execute(task, context, db)

5. Réponse structurée
   {
     "success": true,
     "agent_used": "Task Prioritization Agent",
     "result": [...prioritized tasks...],
     "message": "Successfully prioritized 5 tasks",
     "suggestions": ["Focus on high-priority tasks first", ...]
   }
```

### Workflows prédéfinis

```python
# Daily Briefing
POST /api/v1/agent/workflow
{
  "workflow_type": "daily_briefing",
  "employee_id": 1
}
# Exécute: Prioritization → Burnout Check → Achievements

# Team Health
{
  "workflow_type": "team_health",
  "team_id": 1
}
# Exécute: Workload Balancing → Team Burnout Analysis
```

---

### 4. Services Layer

**Technologies** : Python, SQLAlchemy, spaCy

**Pattern** : Chaque service encapsule la logique métier d'un domaine.

#### TaskPrioritizationService

**Fichier** : [backend/app/services/task_prioritization_service.py](backend/app/services/task_prioritization_service.py)

**Responsabilités** :
- Calculer le score de priorité des tâches
- Prendre en compte : urgence, deadline, effort, productivité, dépendances

**Algorithme** :
```python
priority_score = (
    0.30 * normalize_urgency(task.urgency) +
    0.25 * calculate_deadline_urgency(task.deadline) +
    0.20 * normalize_effort(task.estimated_effort) +
    0.15 * match_productivity_period(task, employee) +
    0.10 * calculate_dependency_boost(task)
)
```

#### BurnoutDetectionService

**Fichier** : [backend/app/services/burnout_detection_service.py](backend/app/services/burnout_detection_service.py)

**Responsabilités** :
- Calculer le score de risque de burnout
- Générer des recommandations
- Déclencher des interventions automatiques

**Algorithme** :
```python
risk_score = (
    0.30 * normalize_hours_worked() +
    0.25 * cognitive_load +
    0.20 * calculate_social_isolation() +
    0.15 * (1 - sentiment_score) +
    0.10 * (1 - task_completion_rate)
)

# Risk levels
if risk_score >= 0.8: "critical"
elif risk_score >= 0.6: "high"
elif risk_score >= 0.4: "medium"
else: "low"
```

#### WorkloadBalancingService

**Fichier** : [backend/app/services/workload_balancing_service.py](backend/app/services/workload_balancing_service.py)

**Responsabilités** :
- Calculer l'équité de distribution de charge
- Suggérer des rééquilibrages
- Auto-assigner les nouvelles tâches

**Algorithme** :
```python
# Score global par employé
global_score = 0.6 * cumulative_load + 0.4 * critical_score

# Équité d'équipe (coefficient de variation)
equity_score = 1.0 - (std_dev(loads) / mean(loads))

# 1.0 = parfaitement équilibré
# < 0.7 = nécessite rééquilibrage
```

#### TaskExtractionService ✨ (Consolidé)

**Fichier** : [backend/app/services/task_extraction_service.py](backend/app/services/task_extraction_service.py)

**Changement v2.0** : Réduit de **296 lignes → 40 lignes** en utilisant le NLP avancé.

**Responsabilités** :
- Wrapper pour le TaskExtractor NLP
- Conversion TaskEntity → TaskCandidate

**Architecture** :
```python
class TaskExtractionService:
    def __init__(self):
        self.extractor = TaskExtractor()  # NLP engine

    def extract_from_email(email_body, email_subject):
        entities = self.extractor.extract_tasks(text, "email")
        return [self._convert_to_candidate(e) for e in entities]
```

**NLP Engine** : [backend/app/ml/nlp_task_extractor/extractor.py](backend/app/ml/nlp_task_extractor/extractor.py)

**Technologies** :
- **spaCy** : Analyse de dépendances, NER, extraction de syntagmes nominaux
- **Fallback rule-based** : Si spaCy non disponible

**Fonctionnalités** :
1. **Extraction action-objet** via dependency parsing
   ```
   "Préparer le rapport financier" →
   action: "préparer"
   object: "le rapport financier"
   ```

2. **Détection de deadlines** avec patterns regex
   ```
   "avant vendredi" → 2025-01-26 23:59:59
   "dans 3 jours" → 2025-01-26 23:59:59
   "avant le 31/12" → 2025-12-31 23:59:59
   ```

3. **Estimation d'urgence** via mots-clés
   ```
   "urgent" → urgency = 5
   "important" → urgency = 4
   "si possible" → urgency = 2
   ```

4. **Estimation d'effort** basée sur la complexité
   ```
   "développer", "implémenter" → 8h
   "analyser", "préparer" → 4h
   "envoyer", "contacter" → 1h
   ```

5. **Scoring de confiance** (0-1)
   ```
   confidence = base(0.3) +
                action(0.25) +
                object(0.15) +
                deadline(0.15) +
                urgency(0.1) +
                entities(0.1)
   ```

#### RecognitionService

**Fichier** : [backend/app/services/recognition_service.py](backend/app/services/recognition_service.py)

**Responsabilités** :
- Détecter automatiquement les accomplissements
- Calculer l'impact des achievements
- Suggérer des reconnaissances

**Critères de détection** :
- Tâches terminées en avance
- Tâches à haute priorité complétées
- Série de completions consécutives
- Aide apportée à d'autres employés

---

### 5. Database Layer

**Technologies** : PostgreSQL, SQLAlchemy

**Modèles principaux** :

```python
# Employee
class Employee(Base):
    id: UUID
    name: str
    email: str
    team_id: UUID
    role: str
    productivity_periods: JSON  # {"morning": 0.8, "afternoon": 0.9, ...}
    tasks: Relationship[Task]
    burnout_metrics: Relationship[BurnoutMetric]

# Task
class Task(Base):
    id: UUID
    title: str
    urgency: int (1-5)
    priority_score: float (0-1)  # Calculé par l'IA
    deadline: datetime
    estimated_effort: float
    status: Enum(pending, in_progress, completed, ...)
    assigned_to: UUID
    dependencies: JSON  # [task_uuid, ...]

# BurnoutMetric
class BurnoutMetric(Base):
    employee_id: UUID
    date: date
    hours_worked: float
    cognitive_load: float
    social_interactions: int
    task_completion_rate: float
    sentiment_score: float
    risk_score: float  # Calculé

# Achievement
class Achievement(Base):
    employee_id: UUID
    type: Enum(deliverable, innovation, collaboration, ...)
    impact_score: float
    recognized_by_manager: bool
```

**Relations** :
```
Employee 1---* Task
Employee 1---* BurnoutMetric
Employee 1---* Achievement
Team 1---* Employee
Task *---* Task (dependencies)
```

---

## Améliorations v2.0

### 1. Consolidation NLP ✅

**Avant** (v1.0) :
```
task_extraction_service.py (296 lignes)  → Logique dupliquée
ml/nlp_task_extractor/extractor.py (625 lignes) → Non utilisé
```

**Après** (v2.0) :
```
task_extraction_service.py (40 lignes)  → Wrapper simple
ml/nlp_task_extractor/extractor.py (625 lignes) → Utilisé partout
```

**Gain** : -256 lignes, meilleure qualité d'extraction (spaCy)

### 2. Gestion correcte des sessions DB ✅

**Avant** (v1.0) :
```python
class TaskPrioritizationAgent:
    def __init__(self):
        self.service = TaskPrioritizationService()  # ❌ Pas de DB!
```

**Après** (v2.0) :
```python
class TaskPrioritizationAgent:
    async def execute(task, context, db: Session):
        service = TaskPrioritizationService(db)  # ✅ Session injectée
```

### 3. Système Multi-Agent unifié ✅

**Avant** : Endpoints séparés pour chaque fonctionnalité
```
POST /api/v1/tasks/prioritize
POST /api/v1/analytics/burnout
POST /api/v1/analytics/balance
...
```

**Après** : Un endpoint unifié avec routage intelligent
```
POST /api/v1/agent/execute
{
  "task": "natural language query",
  "context": {...},
  "auto_detect": true
}
```

---

## Flux de données complets

### Exemple 1 : Prioriser les tâches d'un employé

```
1. Frontend → POST /api/v1/agent/smart-assist
   query: "What should I work on next?"
   employee_id: 123

2. API Layer → Crée AgentRequest
   {
     task: "What should I work on next?",
     context: {employee_id: 123},
     auto_detect: true
   }

3. Orchestrator → Sélectionne TaskPrioritizationAgent
   (score: 0.9 car "work on" match)

4. Agent → Exécute avec DB
   service = TaskPrioritizationService(db)
   tasks = service.prioritize_employee_tasks(123)

5. Service → Requête DB + calcul
   SELECT * FROM tasks WHERE assigned_to = 123 AND status != 'completed'
   Pour chaque task:
     priority_score = calculate_priority(task, employee)

6. Agent → Retourne AgentResponse
   {
     success: true,
     agent_used: "Task Prioritization Agent",
     result: [task1, task2, task3],
     suggestions: ["Focus on high-priority tasks first"]
   }

7. API → Renvoie JSON au frontend

8. Frontend → Affiche la liste priorisée
```

### Exemple 2 : Extraire des tâches depuis un email

```
1. Frontend → POST /api/v1/agent/execute
   {
     task: "Extract tasks from this email",
     context: {
       text: "Bonjour, merci de préparer le rapport urgent avant demain..."
     }
   }

2. Orchestrator → Sélectionne TaskExtractionAgent
   (score: 0.9 car "extract" + "text" présent)

3. Agent → Exécute (SANS DB)
   service = TaskExtractionService()
   tasks = service.extract_from_email(text)

4. Service → Délègue au NLP engine
   extractor = TaskExtractor()
   entities = extractor.extract_tasks(text, "email")

5. NLP Engine (spaCy) :
   a. Tokenization + POS tagging
   b. Dependency parsing → trouve "préparer" (VERB) + "rapport" (NOUN)
   c. Deadline detection → "avant demain" → 2025-01-24
   d. Urgency detection → "urgent" → urgency = 5
   e. Confidence scoring → 0.85

6. Service → Conversion
   TaskEntity → TaskCandidate (schéma API)

7. Agent → Retourne
   {
     success: true,
     result: [{
       title: "préparer le rapport urgent",
       urgency: 5,
       deadline: "2025-01-24T23:59:59",
       confidence: 0.85
     }]
   }
```

---

## Décisions d'Architecture

### Pourquoi un système multi-agent?

**Avantages** :
1. ✅ Interface unifiée pour toutes les fonctionnalités IA
2. ✅ Extensible (facile d'ajouter de nouveaux agents)
3. ✅ Auto-détection intelligente basée sur le contexte
4. ✅ Workflows composables (daily_briefing = 3 agents)

**Inconvénients** :
1. ❌ Couche d'abstraction supplémentaire
2. ❌ Détection par mots-clés peut être fragile

**Quand l'utiliser** :
- Interfaces conversationnelles (chatbots, assistants)
- Workflows complexes multi-étapes
- Quand l'utilisateur ne sait pas quel service appeler

**Quand utiliser les endpoints directs** :
- Intégrations système-à-système
- Besoins de performances critiques
- Quand on sait exactement quel service on veut

### Pourquoi consoliderhave NLP?

**Raison** : Deux implémentations complètes (920 lignes) faisaient la même chose

**Solution** : Utiliser la meilleure (spaCy) partout, avec fallback rule-based

**Résultat** :
- Code plus maintenable
- Meilleure qualité d'extraction
- Moins de bugs (une seule source de vérité)

### Pourquoi pas Redis/Celery?

**Décision** : Supprimés dans v2.0 (simplification)

**Raisons** :
1. Non utilisés dans le code actuel
2. Complexité inutile pour le MVP
3. PostgreSQL suffit pour les besoins actuels

**Quand les réintroduire** :
- Caching : Quand les requêtes DB deviennent lentes
- Celery : Quand on a des tâches vraiment longues (>30s)

---

## Diagrammes de séquence

### Workflow complet : Daily Briefing

```
User → Frontend → API → Orchestrator → Agents → Services → DB

1. User clicks "Daily Briefing" button

2. Frontend
   POST /api/v1/agent/workflow
   {workflow_type: "daily_briefing", employee_id: 1}

3. API endpoint execute_workflow()
   workflows["daily_briefing"] = [
     AgentRequest(task="Prioritize", agent_type=TASK_PRIORITIZATION),
     AgentRequest(task="Burnout", agent_type=BURNOUT_DETECTION),
     AgentRequest(task="Achievements", agent_type=RECOGNITION)
   ]

4. Pour chaque request:

   4a. TaskPrioritizationAgent.execute(db)
       → TaskPrioritizationService(db)
       → SELECT tasks WHERE assigned_to=1
       → Calculate priority_score
       → RETURN prioritized_tasks

   4b. BurnoutDetectionAgent.execute(db)
       → BurnoutDetectionService(db)
       → SELECT burnout_metrics WHERE employee_id=1 ORDER BY date DESC LIMIT 7
       → Calculate risk_score
       → Generate recommendations
       → RETURN {risk_level, risk_score, recommendations}

   4c. RecognitionAgent.execute(db)
       → RecognitionService(db)
       → SELECT achievements WHERE employee_id=1 AND date > NOW() - 30 days
       → Detect new achievements (completed tasks, milestones)
       → RETURN achievements

5. API combines all responses
   {
     workflow: "daily_briefing",
     results: [response_a, response_b, response_c],
     total: 3,
     successful: 3
   }

6. Frontend displays:
   - Top 5 priority tasks
   - Burnout risk widget (color-coded)
   - Recent achievements timeline
```

---

## Sécurité et Bonnes Pratiques

### 1. Injection SQL

**Protection** : SQLAlchemy ORM (parameterized queries)
```python
# ✅ Bon
db.query(Task).filter(Task.id == task_id).first()

# ❌ Mauvais (n'utilisez JAMAIS)
db.execute(f"SELECT * FROM tasks WHERE id = {task_id}")
```

### 2. Sessions DB

**Pattern** : Dependency Injection
```python
# ✅ Bon
@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    # Session gérée automatiquement par FastAPI
    return TaskService(db).get_all()

# Session fermée automatiquement après la requête
```

### 3. Validation des données

**Protection** : Pydantic schemas
```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    urgency: int = Field(..., ge=1, le=5)
    deadline: Optional[datetime]

    @validator('deadline')
    def deadline_must_be_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('Deadline must be in the future')
        return v
```

### 4. CORS

**Configuration** :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # From .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance

### Optimisations actuelles

1. **Eager loading** : Utilisation de `joinedload` pour éviter N+1 queries
   ```python
   db.query(Employee).options(
       joinedload(Employee.tasks),
       joinedload(Employee.burnout_metrics)
   ).all()
   ```

2. **Indexes DB** :
   ```sql
   CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
   CREATE INDEX idx_burnout_employee_date ON burnout_metrics(employee_id, date);
   ```

3. **Caching NLP** : TaskExtractor a un cache LRU
   ```python
   @lru_cache(maxsize=100)
   def extract_tasks(text: str, source_type: str):
       ...
   ```

### Optimisations futures

1. **Redis caching** : Pour les résultats de priorisation
2. **Pagination** : Limiter les résultats des listes
3. **Background jobs** : Pour les tâches longues (Celery)
4. **DB connection pooling** : SQLAlchemy pool

---

## Tests

### Structure

```
backend/tests/
├── test_services/
│   ├── test_task_prioritization.py
│   ├── test_burnout_detection.py
│   └── test_nlp_extraction.py
├── test_api/
│   ├── test_agent_endpoints.py
│   └── test_task_endpoints.py
└── conftest.py  # Fixtures pytest
```

### Exemple de test

```python
def test_task_prioritization(db_session, sample_employee, sample_tasks):
    service = TaskPrioritizationService(db_session)

    prioritized = service.prioritize_employee_tasks(sample_employee.id)

    # Vérifie que les tâches urgentes sont en premier
    assert prioritized[0].urgency >= prioritized[-1].urgency

    # Vérifie que le score est calculé
    assert all(0 <= task.priority_score <= 1 for task in prioritized)
```

---

## Monitoring et Logs

### Configuration

```python
# backend/app/core/logging.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### Métriques importantes

1. **Temps de réponse API** : Middleware FastAPI
2. **Taux d'erreur** : Exception handlers
3. **Utilisation DB** : SQLAlchemy events
4. **NLP extraction quality** : Confidence scores

---

## Évolution Future

### Phase 1 : Optimisations (1-2 semaines)
- [ ] Déplacer les mocks frontend vers fichiers séparés
- [ ] Simplifier l'algorithme de priorisation (3 facteurs au lieu de 5)
- [ ] Supprimer Redux (non utilisé)
- [ ] Tests unitaires complets

### Phase 2 : Features IA (1-2 mois)
- [ ] Sentiment analysis (Transformers)
- [ ] ML burnout predictor (entraîné sur données historiques)
- [ ] Skill gap analysis
- [ ] Recommandations personnalisées

### Phase 3 : Intégrations (2-3 mois)
- [ ] Email integration (Gmail, Outlook)
- [ ] Calendar sync (Google Calendar, Outlook)
- [ ] Slack/Teams notifications
- [ ] Mobile app (React Native)

### Phase 4 : Production (1 mois)
- [ ] CI/CD pipeline
- [ ] Docker optimization
- [ ] Load balancing
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Security audit

---

**Dernière mise à jour** : 2025-01-23
**Version** : 2.0
**Auteur** : B2P.AI Team
