# Plan d'Implémentation - Architecture Complète du Système

## Vue d'Ensemble

Ce document décrit le plan d'implémentation pour transformer le système actuel en une architecture complète avec support multi-équipes et métriques de bien-être.

---

## 1. Analyse de l'État Actuel

### Base de Données Actuelle

#### Employee Model ✅ Partiellement Prêt
```python
class Employee(BaseModel):
    name = Column(String(255))
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    team_id = Column(UUID, ForeignKey("teams.id"))  # ❌ Un seul team
    role = Column(String(100))
    productivity_periods = Column(JSON)  # ✅ Déjà présent
```

**Problème**: Un employé ne peut appartenir qu'à UNE seule équipe (relation one-to-many)
**Requis**: Un employé peut appartenir à PLUSIEURS équipes (relation many-to-many)

#### Task Model ✅ Partiellement Prêt
```python
class Task(BaseModel):
    title = Column(String(500))
    description = Column(Text)
    assigned_to = Column(UUID, ForeignKey("employees.id"))
    created_by = Column(UUID, ForeignKey("employees.id"))
    urgency = Column(Integer)  # 1-5 scale ✅
    deadline = Column(DateTime)  # ✅
    estimated_effort = Column(Float)  # ✅
    status = Column(Enum(TaskStatus))  # ✅
    priority_score = Column(Float)  # ✅ AI-calculated
    source = Column(Enum(TaskSource))  # ⚠️ Manque ASSIGNED
    # ❌ Manque: difficulty (1-5)
    # ❌ Manque: team_id
```

**Sources actuelles**: EMAIL, MEETING, MANUAL, CALENDAR
**Requis**: Ajouter ASSIGNED

#### BurnoutMetric Model ✅ Excellent
```python
class BurnoutMetric(BaseModel):
    employee_id = Column(UUID, ForeignKey("employees.id"))
    date = Column(Date)
    hours_worked = Column(Float)
    cognitive_load = Column(Float)  # 0-1 scale
    task_completion_rate = Column(Float)
    risk_score = Column(Float)  # 0-1 scale ✅
```

**Statut**: Déjà bien structuré pour les métriques de bien-être

---

## 2. Changements Requis

### 2.1 Schema Database

#### A. Créer Table de Jonction Employee-Team

**Nouvelle table**: `employee_teams`

```python
class EmployeeTeam(BaseModel):
    """Association table for many-to-many Employee-Team relationship"""
    __tablename__ = "employee_teams"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    joined_at = Column(DateTime, default=func.now())
    is_primary = Column(Boolean, default=False)  # Équipe principale

    # Unique constraint: un employé ne peut pas rejoindre la même équipe deux fois
    __table_args__ = (UniqueConstraint('employee_id', 'team_id'),)
```

#### B. Mettre à Jour Employee Model

```python
class Employee(BaseModel):
    # ... champs existants ...

    # ❌ SUPPRIMER: team_id = Column(UUID, ForeignKey("teams.id"))

    # ✅ AJOUTER: Relation many-to-many
    teams = relationship(
        "Team",
        secondary="employee_teams",
        back_populates="members"
    )
```

#### C. Mettre à Jour Team Model

```python
class Team(BaseModel):
    # ... champs existants ...

    # ❌ SUPPRIMER: members = relationship("Employee", back_populates="team")

    # ✅ AJOUTER: Relation many-to-many
    members = relationship(
        "Employee",
        secondary="employee_teams",
        back_populates="teams"
    )
    tasks = relationship("Task", back_populates="team")
```

#### D. Mettre à Jour Task Model

```python
class TaskSource(str, enum.Enum):
    EMAIL = "email"
    MEETING = "meeting"
    MANUAL = "manual"
    CALENDAR = "calendar"
    ASSIGNED = "assigned"  # ✅ AJOUTER

class Task(BaseModel):
    # ... champs existants ...

    # ✅ AJOUTER
    difficulty = Column(Integer, nullable=False, default=3)  # 1-5 scale
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)

    # ✅ AJOUTER relation
    team = relationship("Team", back_populates="tasks")
```

### 2.2 Migration Alembic

**Fichier**: `backend/alembic/versions/xxx_add_multi_team_support.py`

```python
def upgrade():
    # 1. Créer table employee_teams
    op.create_table(
        'employee_teams',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('employee_id', UUID(), nullable=False),
        sa.Column('team_id', UUID(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'team_id')
    )

    # 2. Migrer données existantes (team_id → employee_teams)
    connection = op.get_bind()
    employees = connection.execute(
        "SELECT id, team_id FROM employees WHERE team_id IS NOT NULL"
    ).fetchall()

    for emp_id, team_id in employees:
        connection.execute(
            "INSERT INTO employee_teams (id, employee_id, team_id, is_primary) "
            "VALUES (gen_random_uuid(), %s, %s, true)",
            (emp_id, team_id)
        )

    # 3. Supprimer colonne team_id de employees
    op.drop_column('employees', 'team_id')

    # 4. Ajouter difficulty et team_id à tasks
    op.add_column('tasks', sa.Column('difficulty', sa.Integer(), default=3))
    op.add_column('tasks', sa.Column('team_id', UUID(), nullable=True))
    op.create_foreign_key(None, 'tasks', 'teams', ['team_id'], ['id'])

    # 5. Ajouter ASSIGNED à TaskSource enum
    op.execute("ALTER TYPE tasksource ADD VALUE 'assigned'")

def downgrade():
    # Reverser les changements...
```

---

## 3. Services Backend

### 3.1 Wellbeing Calculation Service

**Fichier**: `backend/app/services/wellbeing_service.py`

```python
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Task, Employee, BurnoutMetric

class WellbeingService:
    """Calculate employee wellbeing metrics based on tasks"""

    @staticmethod
    def calculate_workload_score(employee_id: str, db: Session) -> float:
        """
        Calculate total workload score
        Based on: sum of (difficulty * urgency) for active tasks
        """
        tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_(['pending', 'in_progress'])
        ).all()

        total_score = 0.0
        for task in tasks:
            difficulty = task.difficulty or 3
            urgency = task.urgency or 3
            effort = task.estimated_effort or 1.0

            # Workload formula: difficulty × urgency × effort
            total_score += (difficulty / 5.0) * (urgency / 5.0) * effort

        return total_score

    @staticmethod
    def calculate_stress_level(employee_id: str, db: Session) -> float:
        """
        Calculate stress level (0-1 scale)
        Based on: urgency + deadline overlap
        """
        now = datetime.now()
        week_ahead = now + timedelta(days=7)

        tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_(['pending', 'in_progress'])
        ).all()

        urgent_tasks = [t for t in tasks if t.urgency >= 4]
        deadline_tasks = [
            t for t in tasks
            if t.deadline and now <= t.deadline <= week_ahead
        ]

        # Stress formula
        urgency_stress = len(urgent_tasks) * 0.2
        deadline_stress = len(deadline_tasks) * 0.15

        total_stress = min(1.0, urgency_stress + deadline_stress)
        return total_stress

    @staticmethod
    def calculate_overlap_risk(employee_id: str, db: Session) -> Dict:
        """
        Detect tasks with overlapping deadlines
        Returns: { "overlap_count": int, "conflicts": List[...] }
        """
        tasks = db.query(Task).filter(
            Task.assigned_to == employee_id,
            Task.status.in_(['pending', 'in_progress']),
            Task.deadline.isnot(None)
        ).order_by(Task.deadline).all()

        conflicts = []
        for i, task1 in enumerate(tasks):
            for task2 in tasks[i+1:]:
                # Check if deadlines are within 24 hours
                time_diff = abs((task1.deadline - task2.deadline).total_seconds())
                if time_diff < 86400:  # 24 hours
                    conflicts.append({
                        "task1": {"id": task1.id, "title": task1.title},
                        "task2": {"id": task2.id, "title": task2.title},
                        "deadline": task1.deadline.isoformat()
                    })

        return {
            "overlap_count": len(conflicts),
            "conflicts": conflicts
        }

    @staticmethod
    def calculate_burnout_risk(employee_id: str, db: Session) -> float:
        """
        Calculate overall burnout risk (0-1 scale)
        Combines: workload + stress + cognitive load
        """
        workload = WellbeingService.calculate_workload_score(employee_id, db)
        stress = WellbeingService.calculate_stress_level(employee_id, db)

        # Get recent cognitive load from burnout metrics
        recent_metric = db.query(BurnoutMetric).filter(
            BurnoutMetric.employee_id == employee_id
        ).order_by(BurnoutMetric.date.desc()).first()

        cognitive_load = recent_metric.cognitive_load if recent_metric else 0.5

        # Burnout formula: weighted average
        burnout_risk = (
            workload * 0.4 +
            stress * 0.35 +
            cognitive_load * 0.25
        )

        return min(1.0, burnout_risk)

    @staticmethod
    def get_wellbeing_summary(employee_id: str, db: Session) -> Dict:
        """
        Get complete wellbeing summary for an employee
        """
        return {
            "workload_score": WellbeingService.calculate_workload_score(employee_id, db),
            "stress_level": WellbeingService.calculate_stress_level(employee_id, db),
            "burnout_risk": WellbeingService.calculate_burnout_risk(employee_id, db),
            "overlap_analysis": WellbeingService.calculate_overlap_risk(employee_id, db),
            "calculated_at": datetime.now().isoformat()
        }
```

### 3.2 Nouveaux Endpoints API

**Fichier**: `backend/app/api/v1/wellbeing.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.services.wellbeing_service import WellbeingService

router = APIRouter(prefix="/wellbeing", tags=["wellbeing"])

@router.get("/summary")
def get_wellbeing_summary(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete wellbeing summary for current user"""
    return WellbeingService.get_wellbeing_summary(current_user.id, db)

@router.get("/workload")
def get_workload_score(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current workload score"""
    return {
        "workload_score": WellbeingService.calculate_workload_score(current_user.id, db)
    }

@router.get("/overlap-risks")
def get_overlap_risks(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks with overlapping deadlines"""
    return WellbeingService.calculate_overlap_risk(current_user.id, db)
```

**Fichier**: `backend/app/api/v1/employees.py` (Mise à jour)

```python
@router.get("/{employee_id}/teams")
def get_employee_teams(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all teams for an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return [
        {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "member_count": len(team.members)
        }
        for team in employee.teams
    ]

@router.post("/{employee_id}/teams/{team_id}")
def add_employee_to_team(
    employee_id: str,
    team_id: str,
    is_primary: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add employee to a team"""
    # Vérifier si l'association existe déjà
    existing = db.query(EmployeeTeam).filter(
        EmployeeTeam.employee_id == employee_id,
        EmployeeTeam.team_id == team_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Employee already in this team")

    # Créer l'association
    employee_team = EmployeeTeam(
        employee_id=employee_id,
        team_id=team_id,
        is_primary=is_primary
    )
    db.add(employee_team)
    db.commit()

    return {"message": "Employee added to team successfully"}
```

**Fichier**: `backend/app/api/v1/tasks.py` (Mise à jour)

```python
@router.get("/")
def get_tasks(
    assigned_to: Optional[str] = None,
    team_id: Optional[str] = None,
    source: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get tasks with multiple filters"""
    query = db.query(Task)

    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    if team_id:
        query = query.filter(Task.team_id == team_id)

    if source:
        query = query.filter(Task.source == source)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.all()
    return tasks

@router.post("/")
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new task"""
    task = Task(
        title=task_data.title,
        description=task_data.description,
        assigned_to=task_data.assigned_to,
        created_by=current_user.id,
        urgency=task_data.urgency,
        difficulty=task_data.difficulty,  # ✅ NOUVEAU
        team_id=task_data.team_id,  # ✅ NOUVEAU
        deadline=task_data.deadline,
        estimated_effort=task_data.estimated_effort,
        source=task_data.source,
        status=TaskStatus.PENDING
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return task
```

---

## 4. Changements Frontend

### 4.1 Mise à Jour TaskCard avec Badges de Source

**Fichier**: `frontend/src/components/TaskCard.tsx`

```typescript
import { Mail, PersonAdd, EditNote, CalendarMonth, Group } from '@mui/icons-material';

const sourceIcons = {
  email: <Mail fontSize="small" />,
  assigned: <PersonAdd fontSize="small" />,
  manual: <EditNote fontSize="small" />,
  meeting: <Group fontSize="small" />,
  calendar: <CalendarMonth fontSize="small" />,
};

const sourceColors = {
  email: '#4A90E2',
  assigned: '#F5A623',
  manual: '#7ED321',
  meeting: '#BD10E0',
  calendar: '#50E3C2',
};

// Dans le JSX:
<Chip
  icon={sourceIcons[task.source]}
  label={task.source.toUpperCase()}
  size="small"
  sx={{
    backgroundColor: sourceColors[task.source],
    color: 'white',
    fontWeight: 600,
  }}
/>

{/* Indicateur de difficulté */}
<Chip
  label={`Difficulty: ${task.difficulty}/5`}
  size="small"
  variant="outlined"
  sx={{
    borderColor: getDifficultyColor(task.difficulty),
    color: getDifficultyColor(task.difficulty),
  }}
/>
```

### 4.2 Dashboard Analytics avec Métriques Wellbeing

**Fichier**: `frontend/src/pages/Analytics.tsx`

```typescript
const Analytics = () => {
  const [wellbeingData, setWellbeingData] = useState(null);
  const [overlapRisks, setOverlapRisks] = useState([]);

  useEffect(() => {
    fetchWellbeingData();
    fetchOverlapRisks();
  }, []);

  const fetchWellbeingData = async () => {
    const response = await axios.get(`${API_URL}/wellbeing/summary`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setWellbeingData(response.data);
  };

  return (
    <Box>
      {/* Wellbeing Metrics Cards */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Workload Score</Typography>
              <Typography variant="h3">
                {wellbeingData?.workload_score.toFixed(1)}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={wellbeingData?.workload_score * 10}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Stress Level</Typography>
              <Typography variant="h3" color={getStressColor(wellbeingData?.stress_level)}>
                {(wellbeingData?.stress_level * 100).toFixed(0)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Burnout Risk</Typography>
              <Typography variant="h3" color={getRiskColor(wellbeingData?.burnout_risk)}>
                {(wellbeingData?.burnout_risk * 100).toFixed(0)}%
              </Typography>
              {wellbeingData?.burnout_risk > 0.6 && (
                <Alert severity="error">High burnout risk detected!</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Task Overlaps</Typography>
              <Typography variant="h3">
                {wellbeingData?.overlap_analysis?.overlap_count || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Conflicting deadlines
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Overlap Conflicts List */}
      {overlapRisks.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              ⚠️ Deadline Conflicts Detected
            </Typography>
            <List>
              {overlapRisks.map((conflict, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={`${conflict.task1.title} ↔ ${conflict.task2.title}`}
                    secondary={`Both due on ${new Date(conflict.deadline).toLocaleDateString()}`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};
```

### 4.3 Multi-Team Support

**Fichier**: `frontend/src/pages/TaskManagement.tsx`

```typescript
const [teams, setTeams] = useState([]);
const [selectedTeam, setSelectedTeam] = useState('all');

const fetchUserTeams = async () => {
  const response = await axios.get(`${API_URL}/employees/${user.id}/teams`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  setTeams(response.data);
};

// Dans le JSX - Sélecteur d'équipe:
<FormControl>
  <InputLabel>Filter by Team</InputLabel>
  <Select value={selectedTeam} onChange={(e) => setSelectedTeam(e.target.value)}>
    <MenuItem value="all">All Teams</MenuItem>
    {teams.map(team => (
      <MenuItem key={team.id} value={team.id}>
        {team.name} ({team.member_count} members)
      </MenuItem>
    ))}
  </Select>
</FormControl>

// Fetch tasks filtered by team
const fetchTasks = async () => {
  const params = { assigned_to: user.id };
  if (selectedTeam !== 'all') {
    params.team_id = selectedTeam;
  }

  const response = await axios.get(`${API_URL}/tasks`, {
    headers: { Authorization: `Bearer ${token}` },
    params
  });
  setTasks(response.data);
};
```

---

## 5. Ordre d'Implémentation

### Phase 1: Database & Models (Backend)
1. ✅ Créer modèle `EmployeeTeam` (junction table)
2. ✅ Mettre à jour `Employee` model (many-to-many teams)
3. ✅ Mettre à jour `Team` model (many-to-many members)
4. ✅ Ajouter `difficulty` et `team_id` au `Task` model
5. ✅ Ajouter `ASSIGNED` au `TaskSource` enum
6. ✅ Créer migration Alembic
7. ✅ Exécuter migration sur DB

### Phase 2: Services Backend
1. ✅ Créer `WellbeingService` avec toutes les méthodes de calcul
2. ✅ Créer endpoints `/wellbeing/*`
3. ✅ Mettre à jour endpoints `/employees/{id}/teams`
4. ✅ Mettre à jour endpoint `/tasks` avec filtres multiples
5. ✅ Tester tous les endpoints avec Postman/Swagger

### Phase 3: Frontend Components
1. ✅ Ajouter badges de source dans `TaskCard`
2. ✅ Ajouter indicateurs de difficulté dans `TaskCard`
3. ✅ Créer sélecteur multi-teams dans `TaskManagement`
4. ✅ Mettre à jour formulaire de création de tâche (ajouter difficulty, team)
5. ✅ Créer dashboard Analytics avec métriques wellbeing
6. ✅ Ajouter alertes pour overlaps et burnout risk

### Phase 4: Tests & Documentation
1. ✅ Tests unitaires pour `WellbeingService`
2. ✅ Tests d'intégration pour endpoints API
3. ✅ Tests E2E pour workflows complets
4. ✅ Mettre à jour `SYNCHRONISATION_GUIDE.md`
5. ✅ Créer guide utilisateur pour wellbeing features

---

## 6. Points d'Attention

### ⚠️ Migration de Données
- Tous les employés existants doivent être migrés de `team_id` vers `employee_teams`
- Marquer leur équipe actuelle comme `is_primary = true`

### ⚠️ Rétrocompatibilité
- L'API doit supporter les anciens clients pendant une période de transition
- Ajouter des warnings pour les endpoints deprecated

### ⚠️ Performance
- Calcul des métriques wellbeing peut être coûteux
- Envisager cache Redis pour métriques (TTL: 5 minutes)
- Index sur `employee_teams(employee_id, team_id)`

### ⚠️ Sécurité
- Vérifier permissions: un employé ne peut voir que SES métriques
- Les managers peuvent voir les métriques de leur équipe

---

## 7. Critères de Succès

✅ Un employé peut appartenir à plusieurs équipes
✅ Toutes les tâches ont une source visible (MANUAL/ASSIGNED/EMAIL/etc.)
✅ Les métriques de bien-être sont calculées et affichées
✅ Les conflits de deadlines sont détectés et signalés
✅ Le dashboard Analytics montre workload, stress, burnout risk
✅ Les filtres multi-teams fonctionnent correctement
✅ La synchronisation backend ↔ frontend est complète

---

**Document créé le**: 2025-11-26
**Version**: 1.0
**Statut**: Prêt pour implémentation
