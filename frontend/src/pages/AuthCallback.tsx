import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, CircularProgress, Typography, Alert, Container } from '@mui/material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      // Get token from URL
      const token = searchParams.get('token');

      if (!token) {
        setError('No authentication token received');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      try {
        // Store token
        localStorage.setItem('token', token);

        // Fetch user info
        const response = await axios.get(`${API_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        // Store user info if needed
        console.log('User authenticated:', response.data);

        // Redirect to home
        navigate('/');
      } catch (err: any) {
        console.error('Auth callback error:', err);
        setError('Authentication failed. Please try again.');
        localStorage.removeItem('token');
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

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
        <Box
          sx={{
            textAlign: 'center',
            backgroundColor: 'white',
            borderRadius: 4,
            p: 6,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          }}
        >
          {error ? (
            <>
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
              <Typography variant="body2" color="text.secondary">
                Redirecting to login...
              </Typography>
            </>
          ) : (
            <>
              <CircularProgress size={60} sx={{ mb: 3 }} />
              <Typography variant="h5" gutterBottom>
                Completing Sign-In
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Please wait while we authenticate you...
              </Typography>
            </>
          )}
        </Box>
      </Container>
    </Box>
  );
};

export default AuthCallback;
