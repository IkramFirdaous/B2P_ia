/**
 * OAuth Callback Handler Page
 * Receives token from backend after successful Gmail OAuth
 */
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';

export default function AuthCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');

    if (token) {
      // Store token and trigger auth context update
      localStorage.setItem('auth_token', token);
      
      // Call global callback handler (set by AuthContext)
      if ((window as any).handleAuthCallback) {
        (window as any).handleAuthCallback(token);
      }

      // Redirect to dashboard
      setTimeout(() => {
        navigate('/');
      }, 500);
    } else {
      // No token - redirect to login with error
      navigate('/login?error=Authentication failed');
    }
  }, [navigate, searchParams]);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <CircularProgress size={60} sx={{ color: 'white', mb: 3 }} />
      <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
        Completing authentication...
      </Typography>
    </Box>
  );
}

