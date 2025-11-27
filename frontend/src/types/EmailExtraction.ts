/**
 * Email Extraction TypeScript types
 * Matches backend Pydantic schemas
 */

// ============================================================================
// Enums
// ============================================================================

export enum ExtractionStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}

// ============================================================================
// Request Types
// ============================================================================

export interface EmailFetchRequest {
  max_emails: number; // 1-100
  unread_only: boolean;
}

export interface TaskApprovalRequest {
  create_task: boolean;
}

// ============================================================================
// Response Types
// ============================================================================

export interface ExtractedEmail {
  id: string;
  email_id: string;
  subject: string;
  sender: string;
  received_at: string; // ISO datetime
  extraction_status: ExtractionStatus;
  extraction_error?: string;
  extracted_at?: string; // ISO datetime
  tasks_count: number;
  created_at: string; // ISO datetime
}

export interface ExtractedTask {
  id: string;
  extracted_email_id: string;
  employee_id: string;
  task_title: string;
  task_description: string;
  deadline?: string; // ISO datetime
  urgency_level: number; // 1-5
  priority_score: number; // 0-1
  sentiment_score?: number; // -1 to 1
  sentiment_label?: string;
  confidence_score: number; // 0-1
  approved: boolean;
  reviewed_at?: string; // ISO datetime
  created_task_id?: string;
  created_at: string; // ISO datetime

  // Enriched fields from email
  email_subject?: string;
  email_sender?: string;
}

export interface EmailProcessingResponse {
  success: boolean;
  message: string;
  stats: {
    emails_fetched: number;
    emails_processed: number;
    emails_failed: number;
    tasks_extracted: number;
    errors: Array<{
      email_id?: string;
      error: string;
      general_error?: string;
    }>;
  };
}

export interface ExtractionStats {
  emails: {
    total: number;
    completed: number;
    failed: number;
    processing: number;
  };
  tasks: {
    total: number;
    pending_review: number;
    approved: number;
  };
}

export interface TaskApprovalResponse {
  success: boolean;
  message: string;
  task: ExtractedTask;
  created_task_id?: string;
}

export interface PaginatedTasks {
  tasks: ExtractedTask[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginatedEmails {
  emails: ExtractedEmail[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TaskDatasetExport {
  task_id: string;
  task_title: string;
  task_description: string;
  deadline?: string;
  urgency_level: number;
  priority_score: number;
  sentiment_score?: number;
  sentiment_label?: string;
  confidence_score: number;
  email_subject: string;
  email_sender: string;
  email_received_at: string;
  approved: boolean;
  created_at: string;
}

// ============================================================================
// UI Helper Types
// ============================================================================

export interface TaskFilters {
  approved?: boolean;
  min_urgency?: number; // 1-5
}

export interface EmailFilters {
  status?: ExtractionStatus;
}
