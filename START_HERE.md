# 🚀 START HERE - Authentification OAuth Gmail

## Ce qui a changé

✅ **Authentification globale avec Gmail OAuth**
- Tu te connectes **une seule fois** avec Gmail
- Accès automatique à toutes les fonctionnalités (y compris extraction d'emails)
- Plus besoin de connecter Gmail séparément dans la page Email Extraction

## Démarrage en 3 étapes

### 1. Configuration Google Cloud (2 min)

1. Va sur [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **Credentials** → Modifier OAuth 2.0 Client
3. Ajoute: `http://localhost:8000/api/v1/auth/callback`
4. **Enregistrer**

### 2. Configuration Backend (2 min)

```bash
# Génère une clé secrète
cd backend
python generate_secret_key.py
```

Copie la clé générée et ajoute-la dans `backend/.env`:

```env
SECRET_KEY=<colle-la-clé-ici>
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback
```

Réinitialise la base de données:

```bash
rm b2p_ai.db
```

### 3. Démarrer (1 min)

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

## C'est tout ! 🎉

Ouvre `http://localhost:3000` → Tu verras la page de connexion → Clique "Sign in with Gmail" → C'est parti !

## Problèmes ?

- **"Could not validate credentials"** → Vérifie `SECRET_KEY` dans `.env`
- **"OAuth redirect URI mismatch"** → Vérifie Google Cloud Console
- **Autres problèmes** → Lis `README_OAUTH_FR.md` (guide complet en français)

## Documentation

- `README_OAUTH_FR.md` - Guide complet en français
- `QUICK_START_OAUTH.md` - Guide rapide en anglais
- `OAUTH_AUTHENTICATION_SETUP.md` - Guide technique détaillé

---

**Prêt à tester !** 🚀

