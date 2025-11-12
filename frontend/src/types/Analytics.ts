/**
 * Analytics and Burnout-related TypeScript types
 */

export interface BurnoutMetric {
  id: string;
  employee_id: string;
  date: string;
  hours_worked: number;
  breaks_taken: number;
  cognitive_load: number; // 0-1
  social_interactions: number;
  task_completion_rate: number; // 0-1
  sentiment_score?: number; // -1 to 1
  risk_score?: number; // 0-1
  created_at: string;
}

export interface BurnoutRiskResponse {
  employee_id: string;
  current_risk_score: number; // 0-1
  risk_level: "low" | "medium" | "high" | "critical";
  factors: {
    [key: string]: number; // Factor name to contribution score
  };
  recommendations: string[];
  trend: "improving" | "stable" | "declining";
}

export interface TeamEquityResponse {
  team_id: string;
  team_name: string;
  equity_score: number; // 0-1, 1 = perfect equity
  member_workloads: EmployeeWorkloadDetail[];
  recommendations: string[];
}

export interface EmployeeWorkloadDetail {
  employee_id: string;
  employee_name: string;
  cumulative_load: number;
  critical_score: number;
  global_score: number;
  active_tasks: number;
}

export interface ActivityTrackingRequest {
  employee_id: string;
  hours_worked: number;
  breaks_taken: number;
  sentiment?: number;
  date?: string;
}

export enum AchievementType {
  DELIVERABLE = "deliverable",
  INNOVATION = "innovation",
  CLIENT_FEEDBACK = "client_feedback",
  COLLABORATION = "collaboration",
  LEARNING = "learning"
}

export interface Achievement {
  id: string;
  employee_id: string;
  type: AchievementType;
  description: string;
  impact_score: number; // 0-1
  related_task_id?: string;
  recognized_by_manager: boolean;
  recognition_note?: string;
  created_at: string;
}

export interface AchievementSummary {
  total_achievements: number;
  recognized_by_manager: number;
  recognition_rate: number;
  average_impact_score: number;
  by_type: {
    [key in AchievementType]?: {
      count: number;
      avg_impact: number;
    };
  };
}
