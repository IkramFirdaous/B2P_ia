/**
 * Email Extraction Service - API calls for email extraction
 */
import { apiClient } from './api';
import {
  ExtractedEmail,
  ExtractedTask,
  EmailExtractionStats,
  EmailFetchRequest,
  OAuthUrlResponse,
  ExtractionJobResponse,
} from '../types/EmailExtraction';

export const emailExtractionService = {
  // Check if Gmail is connected
  checkConnection: async (employeeId: string): Promise<{ connected: boolean; email: string | null }> => {
    const response = await apiClient.get('/email-extraction/check-connection', {
      params: { employee_id: employeeId }
    });
    return response.data;
  },

  // OAuth connection
  initiateGmailConnect: async (employeeId: string): Promise<OAuthUrlResponse> => {
    const response = await apiClient.post('/email-extraction/connect', null, {
      params: { employee_id: employeeId }
    });
    return response.data;
  },

  // Fetch and process emails
  fetchEmails: async (request: EmailFetchRequest): Promise<ExtractionJobResponse> => {
    const response = await apiClient.post('/email-extraction/fetch', request);
    return response.data;
  },

  // Get extracted emails
  getExtractedEmails: async (
    employeeId: string,
    skip: number = 0,
    limit: number = 50,
    status?: string
  ): Promise<ExtractedEmail[]> => {
    const params: any = { employee_id: employeeId, skip, limit };
    if (status) params.status = status;
    
    const response = await apiClient.get('/email-extraction/extractions', { params });
    return response.data;
  },

  // Get single extraction
  getExtractedEmail: async (extractionId: string): Promise<ExtractedEmail> => {
    const response = await apiClient.get(`/email-extraction/extractions/${extractionId}`);
    return response.data;
  },

  // Get extracted tasks (dataset)
  getExtractedTasks: async (
    employeeId: string,
    approved?: boolean,
    skip: number = 0,
    limit: number = 100
  ): Promise<ExtractedTask[]> => {
    const params: any = { employee_id: employeeId, skip, limit };
    if (approved !== undefined) params.approved = approved;
    
    const response = await apiClient.get('/email-extraction/tasks', { params });
    return response.data;
  },

  // Approve task
  approveTask: async (extractedTaskId: string, assignedTo?: string): Promise<any> => {
    const response = await apiClient.post(
      `/email-extraction/approve/${extractedTaskId}`,
      { extracted_task_id: extractedTaskId, assigned_to: assignedTo }
    );
    return response.data;
  },

  // Reject task
  rejectTask: async (extractedTaskId: string): Promise<any> => {
    const response = await apiClient.delete(`/email-extraction/tasks/${extractedTaskId}`);
    return response.data;
  },

  // Get statistics
  getStats: async (employeeId: string): Promise<EmailExtractionStats> => {
    const response = await apiClient.get('/email-extraction/stats', {
      params: { employee_id: employeeId }
    });
    return response.data;
  },

  // Export dataset
  exportDataset: async (employeeId: string, format: 'json' | 'csv' = 'json'): Promise<any> => {
    const response = await apiClient.get('/email-extraction/dataset/export', {
      params: { employee_id: employeeId, format },
      responseType: format === 'csv' ? 'blob' : 'json'
    });
    
    if (format === 'csv') {
      // Download CSV file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `email_extraction_dataset_${employeeId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      return { success: true };
    }
    
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<any> => {
    const response = await apiClient.get('/email-extraction/health');
    return response.data;
  }
};

