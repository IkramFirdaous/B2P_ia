/**
 * Task-related TypeScript types
 */

export enum TaskStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  BLOCKED = "blocked",
  CANCELLED = "cancelled"
}

export enum TaskSource {
  EMAIL = "email",
  MEETING = "meeting",
  MANUAL = "manual",
  CALENDAR = "calendar"
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  assigned_to?: string;
  created_by: string;
  urgency: number; // 1-5
  deadline?: string; // ISO datetime
  estimated_effort?: number; // Hours
  status: TaskStatus;
  priority_score?: number; // 0-1
  dependencies: string[]; // Task IDs
  source: TaskSource;
  source_metadata?: Record<string, any>;
  completed_at?: string;
  actual_effort?: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  assigned_to?: string;
  created_by: string;
  urgency?: number;
  deadline?: string;
  estimated_effort?: number;
  source?: TaskSource;
  source_metadata?: Record<string, any>;
  dependencies?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  urgency?: number;
  deadline?: string;
  estimated_effort?: number;
  status?: TaskStatus;
  assigned_to?: string;
  actual_effort?: number;
}

export interface TaskWithDetails extends Task {
  assigned_employee_name?: string;
  creator_name: string;
}

export interface TaskCandidate {
  title: string;
  description?: string;
  urgency: number;
  estimated_effort?: number;
  deadline?: string;
  confidence: number; // 0-1
}

export interface ScheduledTask {
  task_id: string;
  task_title: string;
  priority_score: number;
  suggested_start: string;
  suggested_end: string;
  urgency: number;
  deadline?: string;
}
