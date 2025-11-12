/**
 * Analytics Service - API calls for burnout and analytics
 */
import { apiClient } from './api';
import {
  BurnoutMetric,
  BurnoutRiskResponse,
  TeamEquityResponse,
  ActivityTrackingRequest,
  Achievement,
  AchievementSummary,
} from '../types/Analytics';

export const analyticsService = {
  // Burnout Detection
  getBurnoutRisk: async (employeeId: string): Promise<BurnoutRiskResponse> => {
    const response = await apiClient.get(`/analytics/burnout/${employeeId}`);
    return response.data;
  },

  trackActivity: async (data: ActivityTrackingRequest): Promise<BurnoutMetric> => {
    const response = await apiClient.post('/analytics/track-activity', data);
    return response.data;
  },

  getBurnoutMetrics: async (employeeId: string, days: number = 30): Promise<BurnoutMetric[]> => {
    const response = await apiClient.get(`/analytics/burnout/${employeeId}/metrics?days=${days}`);
    return response.data;
  },

  triggerInterventions: async (employeeId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/analytics/burnout/${employeeId}/intervene`);
    return response.data;
  },

  // Workload Balancing
  getTeamEquity: async (teamId: string): Promise<TeamEquityResponse> => {
    const response = await apiClient.get(`/analytics/team/${teamId}/equity`);
    return response.data;
  },

  redistributeTasks: async (teamId: string, autoAssign: boolean = false): Promise<any> => {
    const response = await apiClient.post(`/analytics/team/${teamId}/redistribute?auto_assign=${autoAssign}`);
    return response.data;
  },

  // Achievements
  getAchievements: async (employeeId: string, days: number = 30): Promise<Achievement[]> => {
    const response = await apiClient.get(`/analytics/achievements/${employeeId}?days=${days}`);
    return response.data;
  },

  getAchievementSummary: async (employeeId: string, days: number = 30): Promise<AchievementSummary> => {
    const response = await apiClient.get(`/analytics/achievements/${employeeId}/summary?days=${days}`);
    return response.data;
  },

  detectAchievements: async (employeeId: string): Promise<{ detected_achievements: number; achievements: Achievement[] }> => {
    const response = await apiClient.post(`/analytics/employees/${employeeId}/detect-achievements`);
    return response.data;
  },

  getUnrecognizedAchievements: async (teamId: string, days: number = 7): Promise<any[]> => {
    const response = await apiClient.get(`/analytics/team/${teamId}/unrecognized?days=${days}`);
    return response.data;
  },

  addRecognition: async (achievementId: string, recognitionNote: string): Promise<Achievement> => {
    const response = await apiClient.post(`/analytics/achievements/${achievementId}/recognize`, {
      achievement_id: achievementId,
      recognition_note: recognitionNote,
    });
    return response.data;
  },
};
