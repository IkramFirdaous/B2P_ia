/**
 * Email Extraction TypeScript types
 */

export interface ExtractedTask {
  id: string;
  extracted_email_id: string;
  employee_id: string;
  task_title: string;
  task_description?: string;
  deadline?: string;
  urgency_level?: number;
  priority_score?: number;
  sentiment_score?: number;
  sentiment_label?: string;
  confidence_score?: number;
  approved: boolean;
  reviewed_at?: string;
  created_task_id?: string;
  created_at: string;
}

export interface ExtractedEmail {
  id: string;
  employee_id: string;
  email_id: string;
  subject?: string;
  sender: string;
  received_at: string;
  extraction_status: 'pending' | 'processing' | 'completed' | 'failed';
  extraction_error?: string;
  extracted_at?: string;
  created_at: string;
  extracted_tasks: ExtractedTask[];
}

export interface EmailExtractionStats {
  total_emails_processed: number;
  total_tasks_extracted: number;
  average_sentiment: number;
  average_confidence: number;
  pending_approvals: number;
  approved_tasks: number;
}

export interface EmailFetchRequest {
  employee_id: string;
  max_emails: number;
  unread_only: boolean;
}

export interface TaskApprovalRequest {
  extracted_task_id: string;
  assigned_to?: string;
}

export interface OAuthUrlResponse {
  auth_url: string;
  state: string;
}

export interface ExtractionJobResponse {
  job_id: string;
  message: string;
  status: string;
  emails_to_process: number;
}

export interface DatasetItem {
  email_subject: string;
  email_sender: string;
  email_received_at: string;
  task_title: string;
  task_description?: string;
  deadline?: string;
  urgency_level?: number;
  sentiment_score?: number;
  sentiment_label?: string;
  confidence_score?: number;
  approved: boolean;
}

export interface DatasetExport {
  employee_id: string;
  export_date: string;
  total_items: number;
  items: DatasetItem[];
}

