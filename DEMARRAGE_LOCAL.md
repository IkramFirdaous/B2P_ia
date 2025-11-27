# 🚀 Démarrage Rapide en Local (Sans Docker)

## Prérequis

- Python 3.11+ installé
- Node.js 18+ installé
- Aucun serveur de base de données requis (on utilise SQLite)

---

## ⚡ Installation Express (5 minutes)

### 1️⃣ Backend

```bash
# Aller dans le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Installer les dépendances
pip install -r requirements.txt

# Télécharger le modèle NLP français (spaCy)
python -m spacy download fr_core_news_lg

# Créer la base de données et les données d'exemple
python create_sample_data.py

# Démarrer le serveur
uvicorn app.main:app --reload
```

✅ Le backend est maintenant accessible sur **http://localhost:8000**
📚 Documentation API: **http://localhost:8000/docs**

---

### 2️⃣ Frontend

**Ouvrir un NOUVEAU terminal** et exécuter:

```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm start
```

✅ Le frontend est maintenant accessible sur **http://localhost:3000**

---

## 🔐 Comptes de Test

Vous pouvez vous connecter avec ces comptes:

| Email | Mot de passe | Rôle |
|-------|-------------|------|
| alice@example.com | password123 | Manager |
| bob@example.com | password123 | Employé |
| claire@example.com | password123 | Employé |
| david@example.com | password123 | Employé |
| emma@example.com | password123 | Employé |

---

## 📊 Données Générées

Le script `create_sample_data.py` a créé:

- ✅ **3 équipes** (Développement, Design, Data)
- ✅ **5 employés** avec différents rôles
- ✅ **6 tâches** (urgentes, en cours, terminées)
- ✅ **7 compétences** (techniques et soft skills)
- ✅ **35 métriques de burnout** (7 jours pour 5 employés)
- ✅ **3 accomplissements** reconnus

---

## 🎯 Fonctionnalités à Tester

### 1. Dashboard Principal (`/`)
- Vue d'ensemble des tâches
- Métriques de bien-être
- Accomplissements récents

### 2. Gestion des Tâches (`/tasks`)
- Créer, modifier, supprimer des tâches
- Filtrer par statut, urgence, équipe
- Extraction de tâches depuis du texte (NLP)

### 3. Assistant IA (`/ai-assistant`)
- Système multi-agent
- Questions sur les priorités, le burnout, etc.

### 4. Analytics (`/analytics`)
- Graphiques de burnout
- Tendances de productivité
- Métriques d'équipe

### 5. Vue Équipe (`/team`)
- Vue manager des membres
- Distribution de la charge de travail
- Équité de répartition

---

## 🔧 Commandes Utiles

### Backend

```bash
# Recréer la base de données (⚠️ supprime toutes les données)
cd backend
rm b2p_ai.db  # Supprimer l'ancienne base
python create_sample_data.py  # Recréer avec nouvelles données

# Tests
pytest

# Lancer le serveur en mode production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Tests
npm test

# Build de production
npm run build

# Vérifier le code TypeScript
npx tsc --noEmit
```

---

## 📁 Structure de la Base de Données

Fichier SQLite: `backend/b2p_ai.db`

Tables créées:
- `employees` - Comptes utilisateurs
- `teams` - Équipes
- `employee_teams` - Relation employés ↔ équipes
- `tasks` - Tâches
- `burnout_metrics` - Métriques quotidiennes
- `achievements` - Accomplissements
- `skills` - Liste des compétences
- `employee_skills` - Compétences par employé

---

## ❓ Problèmes Courants

### Le backend ne démarre pas

**Erreur: `ModuleNotFoundError`**
```bash
# Solution: Activer l'environnement virtuel
cd backend
venv\Scripts\activate
```

**Erreur: `No module named 'app'`**
```bash
# Solution: Vérifier que vous êtes dans le bon dossier
cd backend
python -c "import app"  # Devrait fonctionner
```

### Le frontend ne démarre pas

**Erreur: `Module not found`**
```bash
# Solution: Réinstaller les dépendances
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### L'API ne répond pas

1. Vérifier que le backend tourne sur http://localhost:8000
2. Vérifier le fichier `frontend/.env.development`:
   ```
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```

### Erreur CORS

Si vous voyez des erreurs CORS dans la console:
1. Vérifier que le frontend est sur http://localhost:3000
2. Vérifier `backend/.env`:
   ```
   BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
   ```

---

## 🎨 Prochaines Étapes

Une fois que tout fonctionne:

1. **Explorez l'application** avec les comptes de test
2. **Testez l'extraction NLP** - Collez un email en français dans "Extraire des tâches"
3. **Essayez le multi-agent** - Posez des questions à l'assistant IA
4. **Créez vos propres données** - Ajoutez des employés, tâches, équipes
5. **Consultez la documentation complète** - Voir `DOCUMENTATION.md`

---

## 📚 Documentation

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Guide complet
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture technique
- **[MULTI_AGENT_SYSTEM.md](MULTI_AGENT_SYSTEM.md)** - Système multi-agent
- **[API Swagger](http://localhost:8000/docs)** - Documentation interactive

---

## 💡 Astuces

### Visualiser la base de données SQLite

Utilisez [DB Browser for SQLite](https://sqlitebrowser.org/):
1. Télécharger et installer
2. Ouvrir le fichier `backend/b2p_ai.db`
3. Explorer les tables et données

### Ajouter plus de données

Modifiez `backend/create_sample_data.py` et relancez:
```bash
rm backend/b2p_ai.db
python backend/create_sample_data.py
```

### Mode Debug

Backend avec auto-reload:
```bash
uvicorn app.main:app --reload --log-level debug
```

Frontend avec source maps:
```bash
GENERATE_SOURCEMAP=true npm start
```

---

## 🆘 Besoin d'Aide?

- Consultez les logs du backend dans le terminal
- Consultez la console du navigateur (F12) pour les erreurs frontend
- Vérifiez `DOCUMENTATION.md` pour plus de détails
- Les données de test sont dans `create_sample_data.py`

---

**Bon développement! 🚀**
