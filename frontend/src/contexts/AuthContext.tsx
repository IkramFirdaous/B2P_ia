/**
 * Authentication Context - Global OAuth Gmail Authentication
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '../services/authService';

interface User {
  employee_id: string;
  email: string;
  name?: string;
  picture?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (token in localStorage)
    const storedToken = localStorage.getItem('auth_token');
    
    if (storedToken) {
      setToken(storedToken);
      loadUserInfo(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const loadUserInfo = async (authToken: string) => {
    try {
      const userInfo = await authService.getCurrentUser(authToken);
      setUser(userInfo);
    } catch (error) {
      console.error('Failed to load user info:', error);
      // Token might be expired
      localStorage.removeItem('auth_token');
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async () => {
    try {
      // Redirect to backend OAuth endpoint
      const authUrl = await authService.getLoginUrl();
      window.location.href = authUrl;
    } catch (error) {
      console.error('Login failed:', error);
      alert('Failed to initiate login. Please try again.');
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await authService.logout(token);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
      window.location.href = '/login';
    }
  };

  const handleAuthCallback = (authToken: string) => {
    localStorage.setItem('auth_token', authToken);
    setToken(authToken);
    loadUserInfo(authToken);
  };

  // Expose callback handler for auth callback page
  (window as any).handleAuthCallback = handleAuthCallback;

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated: !!user && !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

