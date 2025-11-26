# 📧 Email Extraction - Documentation Complète

> **Système d'extraction automatique de tâches depuis Gmail avec IA (Gemini)**

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Configuration rapide](#configuration-rapide)
3. [Configuration Gmail API](#configuration-gmail-api)
4. [Variables d'environnement](#variables-denvironnement)
5. [Utilisation](#utilisation)
6. [Fonctionnalités](#fonctionnalités)
7. [Dépannage](#dépannage)

---

## 🎯 Vue d'ensemble

Le système d'extraction d'emails permet aux employés de:
- **Connecter leur Gmail** via OAuth2 (sécurisé)
- **Extraire automatiquement les tâches** depuis leurs emails professionnels
- **Filtrer les emails promotionnels** (newsletters, pubs) pour ne garder que les vrais emails de travail
- **Obtenir des tâches reformulées** en mode TODO objectif
- **Détecter l'urgence** automatiquement ("urgent", "ASAP", deadlines)
- **Analyser le sentiment** des communications
- **Approuver et créer** des tâches dans le système

### Architecture

```
Frontend (React) → Backend (FastAPI) → Gmail API + Gemini AI → Database (SQLite/PostgreSQL)
```

**Triple filtrage:**
1. **Gmail Query Filter** - Exclut catégories promotions/social/updates
2. **Sender Filter** - Rejette noreply@, marketing@, newsletter@, etc.
3. **AI Content Filter** - Gemini détecte et rejette les contenus promotionnels

---

## ⚡ Configuration Rapide

### 1. Prérequis
- Python 3.11+
- Node.js 18+
- Compte Google (Gmail)

### 2. Installation Backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configuration Gmail API

**Étape 1: Créer un projet Google Cloud**

1. Va sur [Google Cloud Console](https://console.cloud.google.com)
2. Crée un nouveau projet ou sélectionne un existant
3. Note le nom du projet

**Étape 2: Activer Gmail API**

1. Dans le menu latéral, va dans **APIs & Services > Library**
2. Cherche "Gmail API"
3. Clique sur **Enable**

**Étape 3: Configurer l'écran de consentement OAuth**

1. Va dans **APIs & Services > OAuth consent screen**
2. Choisis **External** (ou Internal si workspace Google)
3. Remplis:
   - **App name**: `B2P Email Extraction`
   - **User support email**: ton email
   - **Developer contact**: ton email
4. Clique **Save and Continue**

5. **Scopes** - Ajoute UNIQUEMENT ce scope:
   - Clique **Add or Remove Scopes**
   - Cherche et sélectionne: `https://www.googleapis.com/auth/gmail.readonly`
   - ⚠️ **NE PAS ajouter** `gmail.metadata` - ça cause des erreurs!
   - Clique **Update** puis **Save and Continue**

6. **Test users** - Ajoute ton email Gmail:
   - Clique **Add Users**
   - Entre ton adresse email
   - Clique **Save and Continue**

**Étape 4: Créer des credentials OAuth**

1. Va dans **APIs & Services > Credentials**
2. Clique **Create Credentials > OAuth 2.0 Client ID**
3. Choisis **Web application**
4. Nom: `B2P Email Client`
5. **Authorized redirect URIs** - Ajoute:
   ```
   http://localhost:8000/api/v1/email-extraction/oauth/callback
   ```
6. Clique **Create**
7. **COPIE** le `Client ID` et `Client Secret` (tu en auras besoin)

**Étape 5: Créer une clé Gemini API**

1. Va sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique **Get API Key**
3. Crée une clé et **COPIE-LA**

---

## 🔐 Variables d'environnement

Crée/édite `backend/.env`:

```env
# Gmail OAuth Configuration
GMAIL_CLIENT_ID=YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/email-extraction/oauth/callback

# Gemini AI Configuration
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
GEMINI_MODEL=gemini-pro

# Email Extraction Settings
EMAIL_EXTRACTION_BATCH_SIZE=10
EMAIL_EXTRACTION_MAX_EMAILS=50

# Database (SQLite par défaut pour dev)
DATABASE_URL=sqlite:///./b2p_ai.db

# Backend
SECRET_KEY=your-secret-key-here
API_V1_PREFIX=/api/v1
PROJECT_NAME=B2P Task Management
VERSION=1.0.0
ENVIRONMENT=development

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**⚠️ IMPORTANT**: Remplace `YOUR_CLIENT_ID_HERE`, `YOUR_CLIENT_SECRET_HERE`, et `YOUR_GEMINI_API_KEY_HERE` avec tes vraies valeurs!

---

## 🚀 Utilisation

### Démarrer le Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Tu verras:
```
Starting B2P Task Management v1.0.0
Environment: development
Database URL: sqlite:///./b2p_ai.db
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Démarrer le Frontend

```bash
cd frontend
npm install
npm start
```

Frontend accessible sur: http://localhost:3000

### Connecter Gmail

1. Va sur **http://localhost:3000/email-extraction**
2. Clique **"Connect Gmail"**
3. Sélectionne ton compte Google
4. **Autorise** l'accès (scope: `gmail.readonly` uniquement)
5. Tu seras redirigé avec le message: **"Gmail connected successfully!"**

### Extraire des emails

1. Configure:
   - **Max Emails**: Nombre d'emails à traiter (par défaut: 10)
   - **Unread Only**: Coché = uniquement non lus
2. Clique **"Fetch Emails"**
3. Attends le traitement (5-15 secondes)
4. Tu verras:
   ```
   Processed 5 emails, extracted 8 tasks.
   ```

### Voir et approuver les tâches

**Onglet "Extracted Tasks Dataset":**
- Liste toutes les tâches extraites
- Colonnes: Titre, Urgence, Deadline, Sentiment, Confidence
- Actions:
  - ✅ **Approve** - Crée la tâche dans le système
  - ❌ **Reject** - Supprime la tâche

**Onglet "Email History":**
- Liste tous les emails traités
- Voir sujet, expéditeur, date
- Statut: COMPLETED / PROCESSING / FAILED

### Exporter les données

Clique **"Export CSV"** ou **"Export JSON"** pour télécharger le dataset complet.

---

## ✨ Fonctionnalités

### 🛡️ Triple Filtrage Anti-Spam

**1. Gmail Query Filter**
- Exclut automatiquement:
  - `category:promotions` (newsletters, pubs)
  - `category:social` (Facebook, Twitter, etc.)
  - `category:updates` (notifications automatiques)
- Exclut les expéditeurs:
  - `noreply@`, `no-reply@`, `donotreply@`
  - `marketing@`, `newsletter@`, `notifications@`

**2. Sender Analysis**
- Détecte les emails automatisés:
  - Patterns: `noreply@`, `info@`, `hello@`, `team@`, `bot@`
  - Keywords: "promotion", "offer", "sale", "discount"

**3. AI Content Detection (Gemini)**
- Analyse le contenu de l'email
- Rejette si 2+ mots-clés promotionnels détectés:
  - "unsubscribe", "discount", "buy now", "click here"
  - "découvrez", "profitez", "télécharger", "cliquez ici"
- Retourne **0 tâches** pour les contenus non-professionnels

### 📝 Extraction Intelligente de Tâches

**Reformulation Objective:**
- ❌ "Pourrais-tu réviser le rapport Q4 avant vendredi?"
- ✅ "Réviser le rapport Q4"

**Format imposé:**
- Verbe à l'infinitif + objet
- Court et actionable (5-10 mots)
- Sans formules de politesse

**Détection d'Urgence Automatique:**

| Niveau | Détection | Exemples |
|--------|-----------|----------|
| 5 (CRITICAL) | "immédiatement", "ASAP", "as soon as possible" | "Urgent - ASAP!" |
| 4 (HIGH) | "urgent", "aujourd'hui", "demain", deadline < 2 jours | "avant demain" |
| 3 (MEDIUM) | "cette semaine", deadline 3-7 jours | "avant vendredi" |
| 2 (LOW) | "quand tu peux", deadline > 1 semaine | "pas pressé" |
| 1 (VERY LOW) | Pas de deadline, informationnel | - |

**Détection de Deadline:**
- Analyse du texte pour dates ("vendredi", "lundi", "27 novembre")
- Conversion en format ISO: `2024-11-29T00:00:00`

### 🎭 Analyse de Sentiment

Score de -1 (très négatif) à +1 (très positif):
- **Positive** (+0.3 à +1.0): "merci", "excellent", "bravo", "great"
- **Neutral** (-0.2 à +0.2): Ton professionnel standard
- **Negative** (-1.0 à -0.3): "problème", "urgent", "inquiet", "issue"

### 🌍 Multilingue

Support complet pour:
- **Français**: "peux-tu", "il faut", "réviser", "urgent"
- **Anglais**: "could you", "need to", "review", "urgent"

---

## 🔧 Dépannage

### Erreur: "Missing required parameter: client_id"

**Cause**: `GMAIL_CLIENT_ID` manquant ou vide dans `.env`

**Solution**:
```bash
# Édite backend/.env
GMAIL_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-abcd1234efgh5678
```

Redémarre le backend!

---

### Erreur 403: "Request had insufficient authentication scopes"

**Cause**: Le scope `gmail.readonly` n'est pas correctement configuré

**Solution**:
1. Va dans [Google Cloud Console > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Clique **Edit App**
3. Dans **Scopes**, supprime TOUT sauf: `https://www.googleapis.com/auth/gmail.readonly`
4. **Save**
5. Dans ton navigateur, va sur https://myaccount.google.com/permissions
6. Trouve ton app "B2P Email Extraction"
7. Clique **Remove Access**
8. Reconnecte depuis http://localhost:3000/email-extraction

---

### Erreur: "Not Found" après connexion Gmail

**Cause**: Redirect URI incorrecte dans Google Cloud

**Solution**:
1. Va dans [Credentials](https://console.cloud.google.com/apis/credentials)
2. Clique sur ton OAuth Client
3. Vérifie **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/v1/email-extraction/oauth/callback
   ```
4. Si différent, corrige et **Save**

---

### "0 processed mails" - Aucun email n'est traité

**Causes possibles**:

1. **Tous tes emails sont des newsletters/promos**
   - Le système filtre automatiquement
   - Envoie-toi un vrai email de travail pour tester

2. **Credentials expirés**
   - Déconnecte et reconnecte Gmail

3. **Aucun email non lu**
   - Décoche "Unread Only" ou marque des emails comme non lus

**Test:**
```bash
# Vérifie les credentials dans la DB
cd backend
python -c "from app.core.database import SessionLocal; from app.models.email_credential import EmailCredential; db = SessionLocal(); creds = db.query(EmailCredential).all(); print(f'Credentials: {len(creds)}'); [print(f'  Email: {c.email_address}') for c in creds]"
```

---

### "Pourrais-tu..." n'est pas reformulé

**Cause**: Les anciennes tâches dans la DB

**Solution**:
```bash
# Supprime la vieille DB
cd backend
del b2p_ai.db  # (ou: rm b2p_ai.db sur Linux/Mac)

# Redémarre le backend
python -m uvicorn app.main:app --reload

# Reconnecte Gmail et refetch
```

Les nouvelles tâches seront bien reformulées!

---

### Base de données corrompue

**Solution rapide**:
```bash
cd backend
del b2p_ai.db
# La DB sera recréée automatiquement au redémarrage
```

---

### Erreur Gemini API: "API key not valid"

**Solution**:
1. Va sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crée une nouvelle clé ou copie l'existante
3. Édite `backend/.env`:
   ```env
   GEMINI_API_KEY=AIzaSy...
   ```
4. Redémarre le backend

---

### Le frontend ne charge pas les données

**Vérification**:
```bash
# Test manuel de l'API
curl "http://localhost:8000/api/v1/email-extraction/stats?employee_id=00000000-0000-0000-0000-000000000001"
```

Devrait retourner:
```json
{
  "total_emails_processed": 10,
  "total_tasks_extracted": 15,
  ...
}
```

Si erreur CORS:
```env
# Dans backend/.env
BACKEND_CORS_ORIGINS=http://localhost:3000
```

---

## 📊 Statistiques et Métriques

Le système track automatiquement:
- Nombre total d'emails traités
- Nombre de tâches extraites
- Sentiment moyen des communications
- Tâches en attente d'approbation
- Tâches approuvées et créées

Accessible via:
- Frontend: Dashboard statistics
- API: `GET /api/v1/email-extraction/stats?employee_id={id}`

---

## 🗂️ Structure Base de Données

### `email_credentials`
```sql
id, employee_id, email_provider, email_address, 
access_token, refresh_token, token_expiry
```

### `extracted_emails`
```sql
id, employee_id, email_id, subject, sender, 
received_at, raw_content, extraction_status, extracted_at
```

### `extracted_tasks`
```sql
id, extracted_email_id, employee_id, task_title, 
task_description, deadline, urgency_level, 
priority_score, sentiment_score, confidence_score, 
approved, created_task_id
```

---

## 🔒 Sécurité

- **OAuth2** - Jamais de stockage de mots de passe
- **Scope minimal** - `gmail.readonly` uniquement (lecture seule)
- **Tokens chiffrés** - Stockés en base de données
- **HTTPS recommandé** - En production
- **Refresh automatique** - Des tokens expirés

---

## 🎓 Exemples d'Utilisation

### Email professionnel typique

**Input:**
```
De: jean.martin@company.com
Sujet: Révision rapport Q4

Bonjour,

Pourrais-tu réviser le rapport du quatrième trimestre 
avant vendredi? C'est assez urgent car la réunion 
est lundi matin.

Merci!
Jean
```

**Output (Tâche extraite):**
```json
{
  "title": "Réviser le rapport du quatrième trimestre",
  "urgency": 4,
  "deadline": "2024-11-29T00:00:00",
  "sentiment": "neutral",
  "confidence": 0.95
}
```

### Email avec plusieurs tâches

**Input:**
```
Bonjour l'équipe,

Pour la réunion de lundi:
1. Préparez la présentation client
2. Mettez à jour les chiffres de ventes
3. Vérifiez les contrats signés

Merci!
```

**Output (3 tâches):**
1. "Préparer la présentation client" (urgency: 3)
2. "Mettre à jour les chiffres de ventes" (urgency: 3)
3. "Vérifier les contrats signés" (urgency: 3)

---

## 📞 Support

Pour toute question ou problème:
1. Vérifie cette documentation
2. Consulte les logs backend dans le terminal
3. Vérifie la console navigateur (F12) pour les erreurs frontend

---

## 🎯 Roadmap Futur

- [ ] Support Outlook/Microsoft 365
- [ ] Détection de priorités par projet
- [ ] Extraction de participants/assignés
- [ ] Intégration calendrier (deadlines automatiques)
- [ ] Notifications push nouvelles tâches
- [ ] ML personnalisé par utilisateur

---

**Documentation mise à jour**: 26 novembre 2024  
**Version**: 1.0.0

