# JWT Authentication - Guide de Test

## Vue d'ensemble

Ce guide vous aidera à tester le système d'authentification JWT complet implémenté dans B2P.AI, incluant :
- Authentification backend avec FastAPI
- Interface frontend avec React
- Protection des routes
- Gestion des tokens JWT

## Prérequis

### 1. Installation des dépendances

#### Backend
```bash
cd backend
pip install -r requirements.txt
```

Les packages JWT suivants seront installés :
- `python-jose[cryptography]` - Pour la gestion des JWT
- `passlib[bcrypt]` - Pour le hashage des mots de passe

#### Frontend
```bash
cd frontend
npm install
```

### 2. Configuration de la base de données

#### Option A: Utiliser le script de seed (Recommandé pour les tests)

Le script de seed va créer des données de test complètes :

```bash
cd backend
python scripts/seed_data.py
```

**Important :**
- Tous les employés créés auront le mot de passe par défaut : `password123`
- Vous pouvez vous connecter avec n'importe quel email créé (ex: `alice.martin@b2p.ai`)

Employés créés par le script :
- alice.martin@b2p.ai - Senior Backend Developer
- bob.dupont@b2p.ai - Frontend Developer
- claire.bernard@b2p.ai - DevOps Engineer
- david.leroy@b2p.ai - Full Stack Developer
- emma.petit@b2p.ai - UI/UX Developer
- francois.moreau@b2p.ai - Backend Developer
- julie.roux@b2p.ai - Frontend Developer
- thomas.garcia@b2p.ai - Site Reliability Engineer

#### Option B: Créer un utilisateur manuellement

Si vous avez déjà une base de données avec des employés mais sans password_hash :

```bash
cd backend
python scripts/migrate_add_password_hash.py
```

Ce script va :
1. Ajouter la colonne `password_hash` si elle n'existe pas
2. Définir le mot de passe par défaut `password123` pour tous les employés existants

## Démarrage de l'application

### 1. Démarrer le backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le backend sera accessible à : http://localhost:8000

### 2. Démarrer le frontend

Dans un nouveau terminal :

```bash
cd frontend
npm start
```

Le frontend sera accessible à : http://localhost:3000

## Tests d'authentification

### Test 1: Page de connexion (Login)

1. Ouvrez http://localhost:3000
2. Vous devriez être automatiquement redirigé vers `/login` car vous n'êtes pas authentifié
3. Utilisez les credentials suivants :
   - **Email :** `alice.martin@b2p.ai`
   - **Mot de passe :** `password123`
4. Cliquez sur "Se connecter"

**Résultat attendu :**
- Redirection automatique vers le Dashboard (`/`)
- Vous voyez la barre de navigation avec le menu
- Le nom de l'utilisateur apparaît dans l'en-tête

### Test 2: Inscription (Register)

1. Sur la page de login, cliquez sur "S'inscrire"
2. Remplissez le formulaire :
   - **Nom :** Votre nom
   - **Email :** Un email unique (ex: `test@b2p.ai`)
   - **Mot de passe :** Au moins 6 caractères
   - **Rôle :** Choisissez un rôle (Developer, Designer, etc.)
   - **Team ID (optionnel) :** Laissez vide ou utilisez un UUID d'équipe existant
3. Cliquez sur "S'inscrire"

**Résultat attendu :**
- Redirection automatique vers le Dashboard
- Vous êtes connecté avec le nouvel utilisateur

### Test 3: Protection des routes

1. Déconnectez-vous (bouton Déconnexion dans le menu)
2. Essayez d'accéder directement à :
   - http://localhost:3000/tasks
   - http://localhost:3000/team
   - http://localhost:3000/analytics
   - http://localhost:3000/ai-assistant

**Résultat attendu :**
- Redirection automatique vers `/login` pour toutes ces routes
- Message indiquant que vous devez vous connecter

### Test 4: Persistance de la session

1. Connectez-vous avec un utilisateur
2. Actualisez la page (F5)
3. Fermez et rouvrez le navigateur
4. Retournez sur http://localhost:3000

**Résultat attendu :**
- Vous restez connecté après actualisation
- Le token JWT est stocké dans `localStorage`
- Vous restez connecté même après fermeture du navigateur

### Test 5: Expiration du token

Le token JWT expire après 30 jours par défaut (configurable dans `backend/app/core/config.py`).

Pour tester l'expiration :
1. Modifiez `ACCESS_TOKEN_EXPIRE_MINUTES = 1` dans `backend/app/core/config.py`
2. Redémarrez le backend
3. Connectez-vous
4. Attendez 1 minute
5. Essayez d'effectuer une action (ex: aller sur /tasks)

**Résultat attendu :**
- Redirection vers `/login` car le token a expiré
- Message d'erreur 401 Unauthorized

### Test 6: Changement de mot de passe

1. Connectez-vous
2. Utilisez l'API Swagger pour tester le changement de mot de passe :
   - Allez sur http://localhost:8000/docs
   - Trouvez l'endpoint `POST /api/v1/auth/change-password`
   - Cliquez sur "Try it out"
   - Remplissez :
     ```json
     {
       "current_password": "password123",
       "new_password": "newpassword456"
     }
     ```
   - Ajoutez le header `Authorization: Bearer <votre_token>`
3. Déconnectez-vous
4. Reconnectez-vous avec le nouveau mot de passe

**Résultat attendu :**
- Le changement de mot de passe réussit
- Vous ne pouvez plus vous connecter avec l'ancien mot de passe
- La connexion avec le nouveau mot de passe fonctionne

## Tests API (Backend uniquement)

### Test via Swagger UI

1. Ouvrez http://localhost:8000/docs
2. Testez les endpoints suivants :

#### A. Register
- Endpoint : `POST /api/v1/auth/register`
- Body :
  ```json
  {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "password123",
    "role": "Developer"
  }
  ```

#### B. Login
- Endpoint : `POST /api/v1/auth/login`
- Body :
  ```json
  {
    "email": "testuser@example.com",
    "password": "password123"
  }
  ```
- **Copiez le `access_token` de la réponse**

#### C. Get Current User
- Endpoint : `GET /api/v1/auth/me`
- Cliquez sur le cadenas en haut à droite
- Entrez : `Bearer <votre_access_token>`
- Cliquez sur "Authorize"
- Testez l'endpoint

**Résultat attendu :**
- Vous obtenez les informations de l'utilisateur connecté

### Test via cURL

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Curl Test",
    "email": "curl@test.com",
    "password": "password123",
    "role": "Developer"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "curl@test.com",
    "password": "password123"
  }'

# Get current user (remplacez TOKEN par le token obtenu)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"
```

## Vérification de la sécurité

### Test 1: Vérifier le hashage des mots de passe

1. Connectez-vous à votre base de données PostgreSQL
2. Exécutez :
   ```sql
   SELECT email, password_hash FROM employees LIMIT 5;
   ```

**Résultat attendu :**
- Les mots de passe sont hashés (commence par `$2b$`)
- Les hash sont différents même si les mots de passe sont identiques
- Exemple : `$2b$12$KIXxJ7VvJ5kZ1qY2Z3ZqVeX...`

### Test 2: Tentative d'accès sans token

```bash
curl -X GET http://localhost:8000/api/v1/tasks
```

**Résultat attendu :**
- Code 401 Unauthorized
- Message : "Not authenticated"

### Test 3: Tentative avec un token invalide

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer invalid_token_here"
```

**Résultat attendu :**
- Code 401 Unauthorized
- Message d'erreur JWT invalide

## Dépannage

### Problème : "No module named 'jose'"

```bash
cd backend
pip install python-jose[cryptography] passlib[bcrypt]
```

### Problème : "Column 'password_hash' does not exist"

```bash
cd backend
python scripts/migrate_add_password_hash.py
```

### Problème : Frontend ne démarre pas

Vérifiez que le fichier `.env` existe dans `frontend/` :

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Problème : Token non reconnu

1. Vérifiez que `SECRET_KEY` est défini dans `backend/.env`
2. Si vous changez la `SECRET_KEY`, tous les tokens existants deviennent invalides
3. Déconnectez-vous et reconnectez-vous

### Problème : CORS errors

Le backend doit autoriser le frontend. Vérifiez dans `backend/app/main.py` :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Structure des fichiers créés/modifiés

### Backend
```
backend/
├── app/
│   ├── core/
│   │   └── auth.py                    # Utilitaires JWT et hashage
│   ├── schemas/
│   │   └── auth_schema.py             # Schémas Pydantic pour auth
│   ├── api/v1/
│   │   └── auth.py                    # Endpoints d'authentification
│   └── models/
│       └── employee.py                # Modèle avec password_hash
└── scripts/
    ├── migrate_add_password_hash.py   # Script de migration
    └── seed_data.py                   # Données de test (modifié)
```

### Frontend
```
frontend/
├── src/
│   ├── contexts/
│   │   └── AuthContext.tsx            # Context React pour auth
│   ├── pages/
│   │   ├── Login.tsx                  # Page de connexion
│   │   └── Register.tsx               # Page d'inscription
│   ├── components/
│   │   └── PrivateRoute.tsx           # Protection des routes
│   ├── utils/
│   │   └── axios.ts                   # Instance axios avec intercepteurs
│   └── App.tsx                        # Routes et AuthProvider
```

## Prochaines étapes

1. **Production :**
   - Changer `SECRET_KEY` en production
   - Utiliser HTTPS uniquement
   - Configurer des tokens de courte durée avec refresh tokens
   - Implémenter une blacklist de tokens

2. **Améliorer la sécurité :**
   - Ajouter la vérification d'email
   - Implémenter la réinitialisation de mot de passe
   - Ajouter l'authentification à deux facteurs (2FA)
   - Limiter les tentatives de connexion (rate limiting)

3. **Monitoring :**
   - Logger les connexions/déconnexions
   - Alertes sur activités suspectes
   - Dashboard d'analyse de sécurité

## Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs du backend dans le terminal
2. Vérifiez la console du navigateur (F12)
3. Consultez la documentation FastAPI : https://fastapi.tiangolo.com/
4. Consultez la documentation JWT : https://jwt.io/

---

**Bon testing !** 🚀
