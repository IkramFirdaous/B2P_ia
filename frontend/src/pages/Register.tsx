import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  MenuItem
} from '@mui/material';
// import { useAuth } from '../contexts/AuthContext';

const Register: React.FC = () => {
  // const navigate = useNavigate();
  // const { register } = useAuth();  // TODO: Add register function to AuthContext if needed
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'Developer'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const roles = [
    'Developer',
    'Designer',
    'Manager',
    'Product Owner',
    'QA Engineer',
    'DevOps Engineer',
    'Data Scientist'
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      // TODO: Implement classic registration or use OAuth only
      setError('Classic registration is disabled. Please use "Sign in with Gmail" instead.');
      // await register(formData.name, formData.email, formData.password, formData.role);
      // navigate('/');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        py: 4
      }}
    >
      <Container maxWidth="sm">
        <Card sx={{ borderRadius: 4, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom align="center" fontWeight="bold">
              B2P.AI
            </Typography>
            <Typography variant="h6" gutterBottom align="center" color="text.secondary" mb={3}>
              Create your account
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Full Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                margin="normal"
                required
                autoFocus
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                margin="normal"
                required
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Role"
                name="role"
                select
                value={formData.role}
                onChange={handleChange}
                margin="normal"
                required
                disabled={loading}
              >
                {roles.map((role) => (
                  <MenuItem key={role} value={role}>
                    {role}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                fullWidth
                label="Password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                margin="normal"
                required
                disabled={loading}
                helperText="Minimum 6 characters"
              />
              <TextField
                fullWidth
                label="Confirm Password"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                margin="normal"
                required
                disabled={loading}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{ mt: 3, mb: 2, py: 1.5 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Sign Up'}
              </Button>
            </form>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Already have an account?{' '}
                <Link to="/login" style={{ textDecoration: 'none', color: '#667eea', fontWeight: 600 }}>
                  Sign in
                </Link>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Register;
