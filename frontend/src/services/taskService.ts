/**
 * Task Service - API calls for task management
 */
import { apiClient } from './api';
import { Task, TaskCreate, TaskUpdate, TaskCandidate, ScheduledTask } from '../types/Task';

export const taskService = {
  // Get all tasks
  getTasks: async (filters?: { assigned_to?: string; status?: string }): Promise<Task[]> => {
    const params = new URLSearchParams();
    if (filters?.assigned_to) params.append('assigned_to', filters.assigned_to);
    if (filters?.status) params.append('status', filters.status);

    const response = await apiClient.get(`/tasks?${params.toString()}`);
    return response.data;
  },

  // Get single task
  getTask: async (taskId: string): Promise<Task> => {
    const response = await apiClient.get(`/tasks/${taskId}`);
    return response.data;
  },

  // Create task
  createTask: async (taskData: TaskCreate): Promise<Task> => {
    const response = await apiClient.post('/tasks', taskData);
    return response.data;
  },

  // Update task
  updateTask: async (taskId: string, taskData: TaskUpdate): Promise<Task> => {
    const response = await apiClient.put(`/tasks/${taskId}`, taskData);
    return response.data;
  },

  // Delete task
  deleteTask: async (taskId: string): Promise<void> => {
    await apiClient.delete(`/tasks/${taskId}`);
  },

  // Get prioritized tasks for employee
  getPrioritizedTasks: async (employeeId: string): Promise<Task[]> => {
    const response = await apiClient.get(`/tasks/employee/${employeeId}/prioritized`);
    return response.data;
  },

  // Extract tasks from text
  extractTasks: async (sourceType: string, content: string, createdBy: string): Promise<TaskCandidate[]> => {
    const response = await apiClient.post('/tasks/extract', {
      source_type: sourceType,
      content,
      created_by: createdBy,
    });
    return response.data;
  },

  // Get task scheduling suggestion
  scheduleTask: async (taskId: string, preferredTime?: string): Promise<ScheduledTask> => {
    const response = await apiClient.post(`/tasks/${taskId}/schedule`, {
      preferred_time: preferredTime,
    });
    return response.data;
  },

  // Recalculate priorities
  recalculatePriorities: async (employeeId: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/tasks/employee/${employeeId}/recalculate-priorities`);
    return response.data;
  },
};
