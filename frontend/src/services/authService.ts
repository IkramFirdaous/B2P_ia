/**
 * Authentication Service - API calls for OAuth Gmail login
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface User {
  employee_id: string;
  email: string;
  name?: string;
  picture?: string;
}

class AuthService {
  /**
   * Get Gmail OAuth login URL
   */
  async getLoginUrl(): Promise<string> {
    const response = await axios.get(`${API_BASE_URL}/auth/login/gmail`);
    return response.data.auth_url;
  }

  /**
   * Get current user information
   */
  async getCurrentUser(token: string): Promise<User> {
    const response = await axios.get(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  }

  /**
   * Logout (invalidate session)
   */
  async logout(token: string): Promise<void> {
    await axios.post(
      `${API_BASE_URL}/auth/logout`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  }

  /**
   * Refresh JWT token
   */
  async refreshToken(token: string): Promise<string> {
    const response = await axios.post(
      `${API_BASE_URL}/auth/refresh`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data.access_token;
  }
}

export const authService = new AuthService();

