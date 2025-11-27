# 🔐 OAuth Gmail Authentication - Setup Guide

## Overview

B2P.AI now uses **global Gmail OAuth authentication** for the entire platform. Users authenticate once at login, and this single session grants access to all features, including email extraction.

## Architecture

### Backend Components

1. **`backend/app/models/user_session.py`** - Stores authenticated user sessions
2. **`backend/app/core/security.py`** - JWT token management and authentication middleware
3. **`backend/app/api/v1/auth.py`** - Authentication endpoints (login, callback, logout)
4. **`backend/app/services/gmail_service.py`** - Gmail API integration (updated with new methods)

### Frontend Components

1. **`frontend/src/contexts/AuthContext.tsx`** - Global authentication state management
2. **`frontend/src/services/authService.ts`** - API calls for authentication
3. **`frontend/src/pages/Login.tsx`** - Login page with Gmail OAuth button
4. **`frontend/src/pages/AuthCallback.tsx`** - OAuth callback handler
5. **`frontend/src/components/ProtectedRoute.tsx`** - Route protection wrapper
6. **`frontend/src/components/Layout.tsx`** - Updated with user menu and logout
7. **`frontend/src/pages/EmailExtraction.tsx`** - Simplified (no separate Gmail connection needed)

## Setup Instructions

### 1. Update Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services > Credentials**
4. Edit your OAuth 2.0 Client ID
5. Add the new redirect URI: `http://localhost:8000/api/v1/auth/callback`
6. Keep the old one for backward compatibility: `http://localhost:8000/api/v1/email-extraction/oauth/callback`

### 2. Update Backend Environment Variables

Edit `backend/.env`:

```env
# Security & JWT
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Gmail API
GMAIL_CLIENT_ID=your-gmail-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000
```

**Important**: Generate a strong `SECRET_KEY` (at least 32 characters) for JWT signing.

### 3. Initialize Database

The new `user_sessions` table needs to be created:

```bash
cd backend
# Delete old database to recreate with new schema
rm b2p_ai.db
# Restart backend - tables will be auto-created
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Start the Application

**Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm start
```

## How It Works

### Authentication Flow

1. **User visits the app** → Redirected to `/login` (if not authenticated)
2. **User clicks "Sign in with Gmail"** → Frontend calls `/api/v1/auth/login/gmail`
3. **Backend generates OAuth URL** → User redirected to Google consent screen
4. **User grants permissions** → Google redirects to `/api/v1/auth/callback?code=...`
5. **Backend exchanges code for tokens** → Creates/updates `UserSession` and `EmailCredential`
6. **Backend generates JWT token** → Redirects to frontend `/auth/callback?token=...`
7. **Frontend stores JWT** → `AuthContext` loads user info → User logged in

### Session Management

- **JWT Token**: Stored in `localStorage`, expires after 7 days (10080 minutes)
- **User Session**: Stored in database, linked to Gmail OAuth tokens
- **Email Credentials**: Automatically stored for email extraction feature

### Protected Routes

All routes except `/login` and `/auth/callback` are protected:

```typescript
// In App.tsx
<ProtectedRoute>
  <Layout>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/email-extraction" element={<EmailExtraction />} />
      {/* ... other routes */}
    </Routes>
  </Layout>
</ProtectedRoute>
```

### Email Extraction Integration

The Email Extraction page now uses the global authentication:

- **No separate Gmail connection needed** - User is already authenticated
- **Credentials automatically available** - Stored during login
- **Seamless experience** - Just click "Fetch Emails" and it works

## API Endpoints

### Authentication

- `GET /api/v1/auth/login/gmail` - Initiate Gmail OAuth login
- `GET /api/v1/auth/callback` - OAuth callback handler (creates session + JWT)
- `GET /api/v1/auth/me` - Get current user info (requires JWT)
- `POST /api/v1/auth/logout` - Logout (invalidate session)
- `POST /api/v1/auth/refresh` - Refresh JWT token

### Email Extraction (now uses global auth)

- `POST /api/v1/email-extraction/fetch` - Fetch and process emails
- `GET /api/v1/email-extraction/extractions` - List extracted emails
- `GET /api/v1/email-extraction/tasks` - List extracted tasks
- `GET /api/v1/email-extraction/stats` - Get extraction statistics
- `POST /api/v1/email-extraction/tasks/{id}/approve` - Approve task
- `POST /api/v1/email-extraction/tasks/{id}/reject` - Reject task

## User Experience

### Before (Old System)

1. User opens app → Sees dashboard (no auth)
2. User goes to Email Extraction → Clicks "Connect Gmail"
3. User authenticates with Google → Returns to Email Extraction
4. User can now fetch emails

### After (New System)

1. User opens app → Redirected to Login page
2. User clicks "Sign in with Gmail" → Authenticates once
3. User is logged in → Can access all features
4. User goes to Email Extraction → Already connected, just click "Fetch Emails"

## Security Features

- **JWT-based authentication** - Stateless, scalable
- **Session management** - Track active sessions in database
- **Token expiration** - Automatic logout after 7 days
- **Secure token storage** - OAuth tokens encrypted in database
- **Protected routes** - Unauthorized users redirected to login
- **CORS protection** - Only allowed origins can access API

## Troubleshooting

### "Could not validate credentials" error

- Check if `SECRET_KEY` is set in `.env`
- Verify JWT token is being sent in `Authorization: Bearer <token>` header
- Check if session exists and is active in `user_sessions` table

### "Session expired or invalid" error

- User needs to log in again
- Check if `is_active` is `True` in `user_sessions` table
- Verify token hasn't expired (check `exp` claim in JWT)

### Email extraction not working

- Verify user is authenticated (check `AuthContext`)
- Check if `email_credentials` table has entry for user's `employee_id`
- Ensure Gmail OAuth tokens are valid and not expired

### OAuth redirect URI mismatch

- Verify `GMAIL_REDIRECT_URI` in `.env` matches Google Cloud Console
- Should be: `http://localhost:8000/api/v1/auth/callback`
- Check for trailing slashes (should NOT have one)

## Database Schema

### `user_sessions` table

```sql
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    picture TEXT,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);
```

### `email_credentials` table (existing)

```sql
CREATE TABLE email_credentials (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    email_provider TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry DATETIME,
    email_address TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

## Next Steps

1. **Test the authentication flow** - Log in, navigate, log out
2. **Test email extraction** - Fetch emails without separate connection
3. **Add more OAuth providers** - Microsoft, Outlook (future)
4. **Implement token refresh** - Auto-refresh before expiration
5. **Add user profile page** - View/edit user settings
6. **Add admin panel** - Manage users and sessions

## Support

For issues or questions:
- Check backend logs: `python -m uvicorn app.main:app --reload --port 8000`
- Check frontend console: Browser DevTools → Console
- Verify database: `sqlite3 backend/b2p_ai.db` → `.tables` → `SELECT * FROM user_sessions;`

---

**Status**: ✅ Implementation Complete
**Last Updated**: November 27, 2024

