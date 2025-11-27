/**
 * Email Extraction Service - API calls for email extraction system
 */
import { apiClient } from './api';
import {
  EmailFetchRequest,
  TaskApprovalRequest,
  ExtractedEmail,
  ExtractedTask,
  EmailProcessingResponse,
  ExtractionStats,
  TaskApprovalResponse,
  PaginatedTasks,
  PaginatedEmails,
  TaskDatasetExport,
  TaskFilters,
  EmailFilters,
} from '../types/EmailExtraction';

export const emailExtractionService = {
  /**
   * ⭐ MAIN ACTION - Fetch and process emails from Gmail
   */
  fetchAndProcessEmails: async (
    request: EmailFetchRequest
  ): Promise<EmailProcessingResponse> => {
    const response = await apiClient.post('/email-extraction/fetch', request);
    return response.data;
  },

  /**
   * Get extraction statistics for dashboard
   */
  getStats: async (): Promise<ExtractionStats> => {
    const response = await apiClient.get('/email-extraction/stats');
    return response.data;
  },

  /**
   * Get extracted tasks for review (paginated)
   */
  getTasks: async (
    page: number = 1,
    pageSize: number = 20,
    filters?: TaskFilters
  ): Promise<PaginatedTasks> => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());

    if (filters?.approved !== undefined) {
      params.append('approved', filters.approved.toString());
    }

    if (filters?.min_urgency !== undefined) {
      params.append('min_urgency', filters.min_urgency.toString());
    }

    const response = await apiClient.get(
      `/email-extraction/tasks?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Approve an extracted task
   */
  approveTask: async (
    taskId: string,
    request: TaskApprovalRequest = { create_task: true }
  ): Promise<TaskApprovalResponse> => {
    const response = await apiClient.post(
      `/email-extraction/tasks/${taskId}/approve`,
      request
    );
    return response.data;
  },

  /**
   * Reject and delete an extracted task
   */
  rejectTask: async (taskId: string): Promise<void> => {
    await apiClient.delete(`/email-extraction/tasks/${taskId}`);
  },

  /**
   * Get email processing history (paginated)
   */
  getEmails: async (
    page: number = 1,
    pageSize: number = 20,
    filters?: EmailFilters
  ): Promise<PaginatedEmails> => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());

    if (filters?.status) {
      params.append('status_filter', filters.status);
    }

    const response = await apiClient.get(
      `/email-extraction/emails?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Export task dataset for analysis/ML
   */
  exportDataset: async (approvedOnly: boolean = true): Promise<TaskDatasetExport[]> => {
    const params = new URLSearchParams();
    params.append('approved_only', approvedOnly.toString());

    const response = await apiClient.get(
      `/email-extraction/dataset/export?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Helper: Download dataset as CSV
   */
  downloadDatasetAsCSV: async (approvedOnly: boolean = true): Promise<void> => {
    const dataset = await emailExtractionService.exportDataset(approvedOnly);

    // Convert to CSV
    const headers = [
      'Task ID',
      'Title',
      'Description',
      'Deadline',
      'Urgency',
      'Priority',
      'Sentiment Score',
      'Sentiment',
      'Confidence',
      'Email Subject',
      'Email Sender',
      'Email Date',
      'Approved',
      'Created At',
    ];

    const csvRows = [
      headers.join(','),
      ...dataset.map((item) =>
        [
          item.task_id,
          `"${item.task_title.replace(/"/g, '""')}"`,
          `"${item.task_description.replace(/"/g, '""')}"`,
          item.deadline || '',
          item.urgency_level,
          item.priority_score,
          item.sentiment_score || '',
          item.sentiment_label || '',
          item.confidence_score,
          `"${item.email_subject.replace(/"/g, '""')}"`,
          `"${item.email_sender.replace(/"/g, '""')}"`,
          item.email_received_at,
          item.approved,
          item.created_at,
        ].join(',')
      ),
    ];

    const csvContent = csvRows.join('\n');

    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute(
      'download',
      `task_dataset_${new Date().toISOString().split('T')[0]}.csv`
    );
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },
};
