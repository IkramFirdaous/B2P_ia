/**
 * Login Page - Gmail OAuth Authentication
 */
import { Box, Button, Typography, Card, CardContent, Container } from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    // If already authenticated, redirect to dashboard
    if (isAuthenticated) {
      navigate('/');
    }

    // Check for error in URL params
    const error = searchParams.get('error');
    if (error) {
      alert(`Login failed: ${error}`);
    }
  }, [isAuthenticated, navigate, searchParams]);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Card
          sx={{
            borderRadius: 4,
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          }}
        >
          <CardContent sx={{ p: 6, textAlign: 'center' }}>
            <Typography
              variant="h3"
              gutterBottom
              sx={{
                fontWeight: 800,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2,
              }}
            >
              B2P.AI
            </Typography>

            <Typography variant="h6" color="text.secondary" gutterBottom sx={{ mb: 4 }}>
              AI-Powered Task Management & Burnout Prevention
            </Typography>

            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              Sign in with your Gmail account to access the platform
            </Typography>

            <Button
              variant="contained"
              size="large"
              startIcon={<GoogleIcon />}
              onClick={login}
              sx={{
                py: 1.5,
                px: 4,
                fontSize: '1.1rem',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5568d3 0%, #64408a 100%)',
                  boxShadow: '0 8px 24px rgba(102, 126, 234, 0.4)',
                },
              }}
            >
              Sign in with Gmail
            </Button>

            <Typography variant="caption" color="text.secondary" sx={{ mt: 4, display: 'block' }}>
              By signing in, you agree to our Terms of Service and Privacy Policy
            </Typography>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}

