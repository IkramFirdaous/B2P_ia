/**
 * Multi-Agent System API Service
 */
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface AgentRequest {
  task: string;
  context?: Record<string, any>;
  agent_type?: string;
  auto_detect?: boolean;
}

export interface AgentResponse {
  success: boolean;
  agent_used: string;
  result: any;
  message: string;
  suggestions?: string[];
}

export interface WorkflowResponse {
  workflow: string;
  results: AgentResponse[];
  total: number;
  successful: number;
}

class MultiAgentService {
  /**
   * Execute a task using the multi-agent system
   */
  async executeTask(request: AgentRequest): Promise<AgentResponse> {
    const response = await axios.post(`${API_URL}/agent/execute`, request);
    return response.data;
  }

  /**
   * Smart assistant - simplified interface
   */
  async smartAssist(
    query: string,
    employeeId?: number,
    teamId?: number,
    additionalContext?: Record<string, any>
  ): Promise<AgentResponse> {
    const params = new URLSearchParams();
    params.append('query', query);
    if (employeeId) params.append('employee_id', employeeId.toString());
    if (teamId) params.append('team_id', teamId.toString());

    const response = await axios.post(
      `${API_URL}/agent/smart-assist?${params.toString()}`,
      additionalContext || {}
    );
    return response.data;
  }

  /**
   * Get available agents
   */
  async getAvailableAgents(): Promise<any> {
    const response = await axios.get(`${API_URL}/agent/available`);
    return response.data;
  }

  /**
   * Get example queries
   */
  async getExamples(): Promise<any> {
    const response = await axios.get(`${API_URL}/agent/examples`);
    return response.data;
  }

  /**
   * Execute a pre-defined workflow
   */
  async executeWorkflow(
    workflowType: string,
    employeeId?: number,
    teamId?: number
  ): Promise<WorkflowResponse> {
    const params = new URLSearchParams();
    params.append('workflow_type', workflowType);
    if (employeeId) params.append('employee_id', employeeId.toString());
    if (teamId) params.append('team_id', teamId.toString());

    const response = await axios.post(
      `${API_URL}/agent/workflow?${params.toString()}`
    );
    return response.data;
  }

  /**
   * Execute multiple requests in batch
   */
  async batchExecute(requests: AgentRequest[]): Promise<any> {
    const response = await axios.post(`${API_URL}/agent/batch`, requests);
    return response.data;
  }
}

export const multiAgentService = new MultiAgentService();
