/**
 * Employee-related TypeScript types
 */

export interface Employee {
  id: string;
  name: string;
  email: string;
  role: string;
  team_id?: string;
  productivity_periods: {
    morning: number;
    afternoon: number;
    evening: number;
  };
  created_at: string;
  updated_at: string;
}

export interface EmployeeWithStats extends Employee {
  active_tasks_count: number;
  completed_tasks_count: number;
  current_workload: number;
  burnout_risk_score?: number;
  skills_count: number;
}

export interface EmployeeCreate {
  name: string;
  email: string;
  role: string;
  team_id?: string;
  productivity_periods?: {
    morning: number;
    afternoon: number;
    evening: number;
  };
}

export interface EmployeeUpdate {
  name?: string;
  email?: string;
  role?: string;
  team_id?: string;
  productivity_periods?: {
    morning: number;
    afternoon: number;
    evening: number;
  };
}

export enum SkillCategory {
  TECHNICAL = "technical",
  SOFT_SKILL = "soft_skill",
  DOMAIN = "domain"
}

export enum SkillLevel {
  BEGINNER = "beginner",
  INTERMEDIATE = "intermediate",
  EXPERT = "expert"
}

export interface Skill {
  id: string;
  name: string;
  category: SkillCategory;
  description?: string;
  created_at: string;
}

export interface EmployeeSkill {
  id: string;
  employee_id: string;
  skill_id: string;
  level: SkillLevel;
  skill_name?: string;
  skill_category?: SkillCategory;
}
