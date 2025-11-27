# 🚀 Quick Start - OAuth Authentication

## TL;DR - Get Running in 5 Minutes

### 1. Update Google Cloud Console (2 min)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **Credentials** → Edit your OAuth 2.0 Client
3. Add redirect URI: `http://localhost:8000/api/v1/auth/callback`
4. Click **Save**

### 2. Update Backend `.env` (1 min)

```bash
cd backend
```

Edit `.env` and add/update:

```env
# Generate a random secret key (32+ characters)
SECRET_KEY=change-this-to-a-random-32-character-string-abc123xyz

# Your Gmail credentials (already have these)
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret

# New redirect URI for global auth
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000

# JWT token expires in 7 days
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 3. Reset Database (30 sec)

```bash
cd backend
rm b2p_ai.db
```

### 4. Start Backend (30 sec)

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Wait for: `✅ Database initialized successfully`

### 5. Start Frontend (30 sec)

```bash
cd frontend
npm start
```

### 6. Test It! (1 min)

1. Open browser: `http://localhost:3000`
2. You'll be redirected to **Login page**
3. Click **"Sign in with Gmail"**
4. Authorize with Google
5. You're in! 🎉

## What Changed?

### Before
- No authentication
- Separate Gmail connection in Email Extraction page
- Manual OAuth flow per feature

### After
- **Single sign-on** with Gmail
- **One authentication** for entire platform
- **Automatic email extraction** access
- **User menu** with logout
- **Protected routes** - must be logged in

## Key Features

✅ **Global Authentication** - Log in once, access everything
✅ **JWT Sessions** - Secure, stateless authentication
✅ **Auto Email Credentials** - No separate Gmail connection needed
✅ **User Profile** - See your email in top-right corner
✅ **Logout** - Click avatar → Logout

## Troubleshooting

### "Could not validate credentials"
→ Check `SECRET_KEY` in `.env` (must be set)

### "OAuth redirect URI mismatch"
→ Verify Google Cloud Console has: `http://localhost:8000/api/v1/auth/callback`

### "Session expired"
→ Just log in again (token expires after 7 days)

### Email extraction not working
→ Make sure you're logged in (you should see your email in top-right)

## Testing Checklist

- [ ] Can access login page
- [ ] Can click "Sign in with Gmail"
- [ ] Google OAuth consent screen appears
- [ ] After authorization, redirected to dashboard
- [ ] Can see email in top-right corner
- [ ] Can navigate to Email Extraction
- [ ] Can click "Fetch Emails" (no separate connection needed)
- [ ] Can see extracted tasks
- [ ] Can click avatar → see user menu
- [ ] Can logout
- [ ] After logout, redirected to login page

## Need Help?

Check backend terminal for errors:
```bash
# Should see:
INFO:     Application startup complete
✅ Database initialized successfully
```

Check frontend console (F12):
```javascript
// Should NOT see:
"401 Unauthorized"
"Could not validate credentials"
```

---

**Ready to go!** 🚀

