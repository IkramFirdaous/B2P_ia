# Guide de Synchronisation Backend ↔ Frontend - B2P.AI

## Vue d'ensemble

Ce guide documente la synchronisation complète entre le backend et le frontend de B2P.AI, incluant toutes les fonctionnalités implémentées pour la gestion des employés, des équipes et des tâches.

---

## 1. Authentification et Utilisateur Connecté

### Backend → Frontend

**Route API**: `POST /api/v1/auth/login`

**Flux de données**:
1. L'utilisateur se connecte avec email/password
2. Le backend valide les credentials et retourne un JWT token
3. Le token est stocké dans le AuthContext
4. Les informations de l'utilisateur (nom, email, rôle, team_id) sont récupérées et stockées

**Affichage Frontend**:
- **Layout.tsx** affiche maintenant le vrai nom de l'utilisateur connecté
- L'avatar montre les initiales du nom (ex: "Alice Martin" → "AM")
- Le menu dropdown affiche nom, email et rôle
- Le bouton "Logout" déconnecte l'utilisateur

**Code clé**:
```typescript
// frontend/src/components/Layout.tsx
const { user, logout } = useAuth();

<Avatar onClick={handleMenuOpen}>
  {user?.name ? getInitials(user.name) : 'U'}
</Avatar>

<MenuItem disabled>
  <Box>
    <Typography variant="body2" fontWeight={600}>{user?.name}</Typography>
    <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
  </Box>
</MenuItem>
```

**Fichiers modifiés**:
- [frontend/src/components/Layout.tsx](frontend/src/components/Layout.tsx)
- [frontend/src/contexts/AuthContext.tsx](frontend/src/contexts/AuthContext.tsx)

---

## 2. Gestion des Employés

### 2.1 Affichage des Employés (Backend → Frontend)

**Route API**: `GET /api/v1/employees`

**Flux de données**:
1. Le frontend appelle l'API avec le token JWT
2. Le backend retourne la liste complète des employés
3. Chaque employé contient: `id`, `name`, `email`, `role`, `team_id`
4. Le frontend affiche les employés dans un tableau

**Page Frontend**: [Employees.tsx](frontend/src/pages/Employees.tsx)

**Fonctionnalités**:
- ✅ Affichage de tous les employés en temps réel
- ✅ Informations affichées: Nom, Email, Rôle, Équipe
- ✅ Indicateur de chargement pendant le fetch
- ✅ Gestion des erreurs avec messages explicites
- ✅ Bouton "Refresh" pour actualiser les données

**Code clé**:
```typescript
const fetchEmployees = async () => {
  if (!token) return;
  try {
    setLoading(true);
    const response = await axios.get(`${API_URL}/employees`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setEmployees(response.data);
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to load employees');
  } finally {
    setLoading(false);
  }
};
```

### 2.2 Modification des Employés (Frontend → Backend)

**Route API**: `PUT /api/v1/employees/{employee_id}`

**Flux de données**:
1. L'utilisateur clique sur "Edit" pour un employé
2. Un dialog s'ouvre avec les informations pré-remplies
3. L'utilisateur modifie les champs (nom, email, rôle, équipe)
4. Au clic sur "Save", le frontend envoie les données au backend
5. Le backend met à jour la base de données
6. Le frontend rafraîchit la liste des employés
7. Un message de succès s'affiche

**Code clé**:
```typescript
const handleSaveEmployee = async () => {
  if (!token || !selectedEmployee) return;
  try {
    setLoading(true);
    await axios.put(
      `${API_URL}/employees/${selectedEmployee.id}`,
      {
        name: selectedEmployee.name,
        email: selectedEmployee.email,
        role: selectedEmployee.role,
        team_id: selectedEmployee.team_id || null,
      },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setSuccessMessage('Employee updated successfully!');
    setOpenEditDialog(false);
    await fetchEmployees();  // Rafraîchit la liste
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to update employee');
  } finally {
    setLoading(false);
  }
};
```

**Fichier**: [frontend/src/pages/Employees.tsx](frontend/src/pages/Employees.tsx)

---

## 3. Gestion des Équipes

### 3.1 Affichage des Équipes (Backend → Frontend)

**Route API**: `GET /api/v1/teams`

**Flux de données**:
1. Le frontend appelle l'API pour récupérer toutes les équipes
2. Le backend retourne la liste des équipes avec: `id`, `name`, `description`
3. Les équipes sont affichées dans les dropdowns de sélection

**Code clé**:
```typescript
const fetchTeams = async () => {
  if (!token) return;
  try {
    const response = await axios.get(`${API_URL}/teams`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setTeams(response.data);
  } catch (err: any) {
    console.error('Failed to fetch teams:', err);
  }
};
```

### 3.2 Assignation d'Employés aux Équipes (Frontend → Backend)

**Route API**: `PUT /api/v1/employees/{employee_id}`

**Flux de données**:
1. Dans la page Employees, l'utilisateur clique "Edit"
2. Il sélectionne une équipe dans le dropdown "Team"
3. Au clic sur "Save", le `team_id` est envoyé au backend
4. Le backend met à jour l'employé avec le nouveau `team_id`
5. La liste se rafraîchit et affiche la nouvelle équipe

**Code dans le dialog**:
```typescript
<FormControl fullWidth>
  <InputLabel>Team</InputLabel>
  <Select
    value={selectedEmployee?.team_id || ''}
    label="Team"
    onChange={(e) =>
      setSelectedEmployee({
        ...selectedEmployee!,
        team_id: e.target.value || null,
      })
    }
  >
    <MenuItem value="">
      <em>No Team</em>
    </MenuItem>
    {teams.map((team) => (
      <MenuItem key={team.id} value={team.id}>
        {team.name}
      </MenuItem>
    ))}
  </Select>
</FormControl>
```

**Fichier**: [frontend/src/pages/Employees.tsx](frontend/src/pages/Employees.tsx)

### 3.3 Visualisation de l'Équipe (Backend → Frontend)

**Route API**: `GET /api/v1/teams/{team_id}/members`

**Flux de données**:
1. Le frontend récupère le `team_id` de l'utilisateur connecté
2. Il appelle l'API pour obtenir tous les membres de l'équipe
3. Pour chaque membre, il récupère également:
   - Leurs tâches actives
   - Leurs tâches complétées
   - Leur score de charge de travail
   - Leur risque de burnout
4. Toutes ces données sont affichées sur la page Team View

**Page Frontend**: [TeamView.tsx](frontend/src/pages/TeamView.tsx)

**Code clé**:
```typescript
const fetchTeamData = async () => {
  if (!token || !user?.team_id) {
    setError('Vous devez faire partie d\'une équipe pour voir cette page');
    return;
  }

  try {
    setLoading(true);
    const response = await axios.get(`${API_URL}/teams/${user.team_id}/members`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const members = response.data;

    // Pour chaque membre, récupérer ses tâches
    const membersWithData = await Promise.all(
      members.map(async (member: any) => {
        const tasksRes = await axios.get(`${API_URL}/tasks`, {
          headers: { Authorization: `Bearer ${token}` },
          params: { assigned_to: member.id }
        });

        const tasks = tasksRes.data;
        const activeTasks = tasks.filter((t: any) =>
          t.status === 'pending' || t.status === 'in_progress'
        ).length;

        const workloadScore = tasks
          .filter((t: any) => t.status === 'pending' || t.status === 'in_progress')
          .reduce((sum: number, t: any) => sum + (t.estimated_effort || 0), 0);

        return {
          id: member.id,
          name: member.name,
          role: member.role || 'Team Member',
          activeTasks,
          workloadScore,
          // ... autres métriques
        };
      })
    );

    setTeamMembers(membersWithData);
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Impossible de charger les données');
  } finally {
    setLoading(false);
  }
};
```

---

## 4. Gestion des Tâches

### 4.1 Affichage des Tâches (Backend → Frontend)

**Route API**: `GET /api/v1/tasks`

**Flux de données**:
1. Le frontend appelle l'API avec `assigned_to: user.id`
2. Le backend retourne toutes les tâches assignées à cet utilisateur
3. Les tâches sont filtrées par statut (All, In Progress, Pending, Completed)
4. Chaque tâche affiche: titre, description, urgence, effort estimé, statut, priorité

**Auto-refresh**:
- La liste des tâches se rafraîchit automatiquement toutes les 30 secondes
- Cela permet de voir les tâches créées par email en temps quasi-réel

**Code clé**:
```typescript
// Auto-refresh every 30 seconds
useEffect(() => {
  const intervalId = setInterval(() => {
    if (token && user && !loading) {
      fetchTasks();
    }
  }, 30000); // 30 seconds

  return () => clearInterval(intervalId);
}, [token, user, loading]);

const fetchTasks = async () => {
  if (!token || !user) return;
  try {
    setLoading(true);
    const response = await axios.get(`${API_URL}/tasks`, {
      headers: { Authorization: `Bearer ${token}` },
      params: { assigned_to: user.id }
    });
    setTasks(response.data);
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to load tasks');
  } finally {
    setLoading(false);
  }
};
```

**Fichier**: [frontend/src/pages/TaskManagement.tsx](frontend/src/pages/TaskManagement.tsx#L74-L83)

### 4.2 Création de Tâches (Frontend → Backend)

**Route API**: `POST /api/v1/tasks`

**Flux de données**:
1. L'utilisateur clique sur "New Task"
2. Il remplit le formulaire:
   - Titre (obligatoire)
   - Description
   - Niveau d'urgence (1-5)
   - Effort estimé (heures)
   - **Assignation à un employé** (nouveau!)
3. Au clic sur "Create Task", le frontend envoie toutes les données au backend
4. Le backend crée la tâche dans la base de données
5. Le frontend rafraîchit la liste des tâches
6. Un message de succès s'affiche

**Assignation automatique**:
- Si aucun employé n'est sélectionné, la tâche est assignée à l'utilisateur connecté
- Sinon, elle est assignée à l'employé sélectionné

**Code clé**:
```typescript
const handleCreateTask = async () => {
  if (!token || !user) return;

  try {
    setLoading(true);
    await axios.post(
      `${API_URL}/tasks`,
      {
        title: newTask.title,
        description: newTask.description,
        urgency: newTask.urgency,
        estimated_effort: newTask.estimated_effort,
        created_by: user.id,
        assigned_to: newTask.assigned_to || user.id,  // Employé sélectionné ou utilisateur actuel
        status: 'pending',
        source: 'manual',
      },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    setSuccessMessage('Task created successfully!');
    setOpenDialog(false);
    setNewTask({ title: '', description: '', urgency: 3, estimated_effort: 0, assigned_to: '' });
    await fetchTasks();  // Rafraîchit la liste
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to create task');
  } finally {
    setLoading(false);
  }
};
```

**Dropdown d'assignation**:
```typescript
<FormControl fullWidth>
  <InputLabel>Assign To</InputLabel>
  <Select
    value={newTask.assigned_to}
    label="Assign To"
    onChange={(e) => setNewTask({ ...newTask, assigned_to: e.target.value })}
  >
    <MenuItem value={user?.id || ''}>
      <em>Myself ({user?.name})</em>
    </MenuItem>
    {employees
      .filter(emp => emp.id !== user?.id)
      .map((employee) => (
        <MenuItem key={employee.id} value={employee.id}>
          {employee.name} - {employee.role}
        </MenuItem>
      ))}
  </Select>
</FormControl>
```

**Fichier**: [frontend/src/pages/TaskManagement.tsx](frontend/src/pages/TaskManagement.tsx#L137-L171)

### 4.3 Changement de Statut des Tâches (Frontend → Backend)

**Route API**: `PUT /api/v1/tasks/{task_id}`

**Flux de données**:
1. L'utilisateur clique sur le menu "⋮" d'une tâche
2. Un menu dropdown s'affiche avec les options de statut:
   - Pending
   - In Progress
   - Completed
   - Blocked
3. L'utilisateur sélectionne un nouveau statut
4. Le frontend envoie le nouveau statut au backend
5. Le backend met à jour la tâche dans la base de données
6. Le frontend rafraîchit la liste des tâches
7. Un message de succès s'affiche
8. La tâche se déplace vers l'onglet correspondant à son nouveau statut

**Code dans TaskCard.tsx**:
```typescript
const handleStatusChange = async (newStatus: TaskStatus, event: React.MouseEvent) => {
  event.stopPropagation();
  handleMenuClose();

  if (onStatusChange && task.id) {
    setUpdating(true);
    try {
      await onStatusChange(task.id, newStatus);
    } catch (error) {
      console.error('Failed to update task status:', error);
    } finally {
      setUpdating(false);
    }
  }
};

// Menu avec les options de statut
<Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => handleMenuClose()}>
  <MenuItem disabled>Change Status</MenuItem>
  {statusOptions.map((option) => (
    <MenuItem
      key={option.value}
      onClick={(e) => handleStatusChange(option.value, e)}
      disabled={task.status === option.value}
    >
      <ListItemIcon>{option.icon}</ListItemIcon>
      <ListItemText>{option.label}</ListItemText>
    </MenuItem>
  ))}
</Menu>
```

**Code dans TaskManagement.tsx**:
```typescript
const handleStatusChange = async (taskId: string, newStatus: TaskStatus) => {
  if (!token) return;

  try {
    await axios.put(
      `${API_URL}/tasks/${taskId}`,
      { status: newStatus },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    setSuccessMessage(`Task status updated to ${newStatus.replace('_', ' ')}`);
    await fetchTasks();  // Rafraîchit la liste pour montrer le changement
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to update task status');
    throw err;
  }
};
```

**Fichiers**:
- [frontend/src/components/TaskCard.tsx](frontend/src/components/TaskCard.tsx#L54-L84)
- [frontend/src/pages/TaskManagement.tsx](frontend/src/pages/TaskManagement.tsx#L203-L224)

### 4.4 Réception de Tâches par Email (Backend → Frontend)

**Worker Backend**: `backend/app/workers/email_worker.py`

**Flux de données**:
1. Le worker email vérifie la boîte mail toutes les 60 secondes
2. Quand un email avec une tâche arrive:
   - Le système extrait: titre, description, urgence, deadline
   - Il identifie l'employé par son email
   - Il crée automatiquement la tâche avec `source: "email"`
   - La tâche est assignée à l'employé correspondant
3. Le frontend rafraîchit automatiquement toutes les 30 secondes
4. La nouvelle tâche apparaît dans la liste (délai max: ~90 secondes)

**Indicateur visuel**:
- Les tâches manuelles ont `source: "manual"`
- Les tâches email ont `source: "email"`

**Configuration requise**:
```env
# backend/.env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-app

IMAP_HOST=imap.gmail.com
IMAP_PORT=993
```

**Démarrage du worker**:
```bash
cd backend
python -m app.workers.email_worker
```

---

## 5. Résumé de la Synchronisation

### Flux de Données Complets

#### Backend → Frontend (Lecture)

| Donnée | Route API | Page Frontend | Fréquence |
|--------|-----------|---------------|-----------|
| Utilisateur connecté | `POST /auth/login` | Layout.tsx | À la connexion |
| Liste des employés | `GET /employees` | Employees.tsx | Au chargement + Refresh manuel |
| Liste des équipes | `GET /teams` | Employees.tsx | Au chargement |
| Membres d'une équipe | `GET /teams/{id}/members` | TeamView.tsx | Au chargement + Refresh manuel |
| Tâches de l'utilisateur | `GET /tasks?assigned_to={id}` | TaskManagement.tsx | Au chargement + Auto toutes les 30s |

#### Frontend → Backend (Écriture)

| Action | Route API | Page Frontend | Synchronisation |
|--------|-----------|---------------|-----------------|
| Créer une tâche | `POST /tasks` | TaskManagement.tsx | Refresh immédiat après création |
| Modifier le statut d'une tâche | `PUT /tasks/{id}` | TaskCard.tsx | Refresh immédiat après modification |
| Modifier un employé | `PUT /employees/{id}` | Employees.tsx | Refresh immédiat après modification |
| Assigner un employé à une équipe | `PUT /employees/{id}` | Employees.tsx | Refresh immédiat après assignation |

### Mécanismes de Synchronisation

1. **Refresh manuel**: Bouton "Refresh" disponible sur les pages clés
2. **Auto-refresh**: Liste des tâches toutes les 30 secondes
3. **Refresh après action**: Après chaque création/modification, la liste se rafraîchit
4. **Messages de confirmation**: Succès/Erreur affichés pour chaque action

---

## 6. Tests de Bout en Bout

### Scénario 1: Créer et Assigner une Tâche

1. **Login** → http://localhost:3000/login
2. **Aller sur Task Management**
3. **Cliquer "New Task"**
4. **Remplir**:
   - Titre: "Développer nouvelle fonctionnalité"
   - Description: "Implémenter le système de notifications"
   - Urgence: 4
   - Effort: 8 heures
   - Assign To: "Bob Dupont - Developer"
5. **Cliquer "Create Task"**
6. **Vérifier**: Message de succès + tâche apparaît (si assignée à vous)
7. **Se connecter avec Bob** → La tâche apparaît dans sa liste

### Scénario 2: Changer le Statut d'une Tâche

1. **Aller sur Task Management**
2. **Voir une tâche avec statut "Pending"**
3. **Cliquer sur le menu "⋮"**
4. **Sélectionner "In Progress"**
5. **Vérifier**: Message de succès + tâche se déplace vers l'onglet "In Progress"
6. **Rafraîchir la page** → Le statut est toujours "In Progress" (persisté en DB)

### Scénario 3: Assigner un Employé à une Équipe

1. **Aller sur Employees**
2. **Cliquer "Edit" pour un employé**
3. **Sélectionner une équipe dans le dropdown "Team"**
4. **Cliquer "Save"**
5. **Vérifier**: Message de succès + colonne "Team" affiche le nom de l'équipe
6. **Aller sur Team View** (en tant que membre de cette équipe) → L'employé apparaît

### Scénario 4: Recevoir une Tâche par Email

1. **Démarrer le worker email**: `python -m app.workers.email_worker`
2. **Envoyer un email** à l'adresse configurée avec:
   ```
   Sujet: Nouvelle tâche urgente
   Corps: Réparer le bug critique dans le module de paiement.
          Deadline: 2025-12-01
   ```
3. **Attendre max 90 secondes**
4. **Vérifier Task Management** → La tâche apparaît avec `source: "email"`

---

## 7. Dépannage

### Problème: Tâches créées n'apparaissent pas

**Cause possible**: Le `assigned_to` est mal configuré

**Solution**:
- Vérifiez que le dropdown "Assign To" est sélectionné
- Si vide, la tâche est assignée à vous par défaut
- Rafraîchissez la page manuellement

### Problème: Erreur "You must be part of a team"

**Cause**: L'utilisateur n'a pas de `team_id`

**Solution**:
```sql
-- Vérifier
SELECT id, name, email, team_id FROM employees WHERE email = 'votre-email';

-- Assigner
UPDATE employees SET team_id = 'id-de-votre-equipe' WHERE email = 'votre-email';
```

Ou utilisez la page Employees pour assigner une équipe via l'interface.

### Problème: Changement de statut ne fonctionne pas

**Cause possible**: Problème de permissions JWT

**Solution**:
- Déconnectez-vous et reconnectez-vous
- Vérifiez que le token JWT est valide
- Vérifiez les logs backend pour voir l'erreur exacte

### Problème: Employés ne s'affichent pas

**Cause possible**: Routes API non disponibles

**Solution**:
1. Vérifiez que le backend tourne: http://localhost:8000/docs
2. Testez l'endpoint: `GET /api/v1/employees` avec votre token
3. Exécutez le seed script: `python backend/scripts/seed_data.py`

---

## 8. Fichiers Clés

### Frontend

| Fichier | Responsabilité |
|---------|----------------|
| [App.tsx](frontend/src/App.tsx) | Routes et configuration |
| [Layout.tsx](frontend/src/components/Layout.tsx) | Navigation + affichage utilisateur |
| [TaskManagement.tsx](frontend/src/pages/TaskManagement.tsx) | CRUD tâches + assignation |
| [TaskCard.tsx](frontend/src/components/TaskCard.tsx) | Affichage tâche + changement statut |
| [Employees.tsx](frontend/src/pages/Employees.tsx) | CRUD employés + assignation équipes |
| [TeamView.tsx](frontend/src/pages/TeamView.tsx) | Visualisation équipe |
| [AuthContext.tsx](frontend/src/contexts/AuthContext.tsx) | Gestion authentification |

### Backend

| Fichier | Responsabilité |
|---------|----------------|
| [backend/app/api/v1/auth.py](backend/app/api/v1/auth.py) | Authentification JWT |
| [backend/app/api/v1/employees.py](backend/app/api/v1/employees.py) | CRUD employés |
| [backend/app/api/v1/teams.py](backend/app/api/v1/teams.py) | CRUD équipes |
| [backend/app/api/v1/tasks.py](backend/app/api/v1/tasks.py) | CRUD tâches |
| [backend/app/workers/email_worker.py](backend/app/workers/email_worker.py) | Intégration email |

---

## 9. Résumé des Fonctionnalités Implémentées

| Fonctionnalité | Statut | Backend Route | Frontend Page |
|----------------|--------|---------------|---------------|
| ✅ Authentification JWT | Implémenté | `POST /auth/login` | Login.tsx |
| ✅ Affichage utilisateur connecté | Implémenté | N/A | Layout.tsx |
| ✅ Liste des employés | Implémenté | `GET /employees` | Employees.tsx |
| ✅ Modification employés | Implémenté | `PUT /employees/{id}` | Employees.tsx |
| ✅ Assignation employés aux équipes | Implémenté | `PUT /employees/{id}` | Employees.tsx |
| ✅ Visualisation équipe | Implémenté | `GET /teams/{id}/members` | TeamView.tsx |
| ✅ Création tâches | Implémenté | `POST /tasks` | TaskManagement.tsx |
| ✅ Assignation tâches aux employés | Implémenté | `POST /tasks` | TaskManagement.tsx |
| ✅ Changement statut tâches | Implémenté | `PUT /tasks/{id}` | TaskCard.tsx |
| ✅ Auto-refresh tâches | Implémenté | `GET /tasks` | TaskManagement.tsx |
| ✅ Intégration email | Implémenté | Worker | email_worker.py |

**Toutes les fonctionnalités demandées sont implémentées et fonctionnelles!** 🎉

---

## 10. Prochaines Étapes Possibles

1. **Notifications en temps réel** avec WebSockets
2. **Drag & drop** pour changer le statut des tâches
3. **Tableau Kanban** pour visualiser les tâches
4. **Graphiques de productivité** dans Analytics
5. **Filtres avancés** pour les tâches
6. **Historique des modifications** pour audit
7. **Permissions granulaires** par rôle
8. **Export de données** en CSV/Excel

---

**Documentation créée le**: 2025-11-26
**Version**: 1.0
**Auteur**: Claude Code - B2P.AI Development Team
