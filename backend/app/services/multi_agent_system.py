"""
Multi-Agent System Orchestrator
This system provides a unified interface to execute all AI features through intelligent agent routing.
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel
import json

from app.services.task_prioritization_service import TaskPrioritizationService
from app.services.burnout_detection_service import BurnoutDetectionService
from app.services.workload_balancing_service import WorkloadBalancingService
from app.services.task_extraction_service import TaskExtractionService
from app.services.recognition_service import RecognitionService


class AgentType(str, Enum):
    """Available agent types in the system"""
    TASK_PRIORITIZATION = "task_prioritization"
    BURNOUT_DETECTION = "burnout_detection"
    WORKLOAD_BALANCING = "workload_balancing"
    TASK_EXTRACTION = "task_extraction"
    RECOGNITION = "recognition"
    ORCHESTRATOR = "orchestrator"


class AgentRequest(BaseModel):
    """Request model for agent execution"""
    task: str
    context: Optional[Dict[str, Any]] = {}
    agent_type: Optional[AgentType] = None
    auto_detect: bool = True


class AgentResponse(BaseModel):
    """Response model from agent execution"""
    success: bool
    agent_used: str
    result: Any
    message: str
    suggestions: Optional[List[str]] = []


class Agent:
    """Base class for all agents"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def can_handle(self, task: str, context: Dict[str, Any]) -> float:
        """
        Determine if this agent can handle the task
        Returns a confidence score between 0 and 1
        """
        raise NotImplementedError

    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        """Execute the agent's task"""
        raise NotImplementedError


class TaskPrioritizationAgent(Agent):
    """Agent for task prioritization"""

    def __init__(self):
        super().__init__(
            name="Task Prioritization Agent",
            description="Prioritizes tasks based on urgency, deadlines, effort, and productivity patterns"
        )
        self.service = TaskPrioritizationService()

    async def can_handle(self, task: str, context: Dict[str, Any]) -> float:
        keywords = ["prioritize", "priority", "urgent", "important", "order", "rank", "sort tasks"]
        task_lower = task.lower()
        return max([0.9 if keyword in task_lower else 0.0 for keyword in keywords] + [0.0])

    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        try:
            employee_id = context.get("employee_id")
            if not employee_id:
                return AgentResponse(
                    success=False,
                    agent_used=self.name,
                    result=None,
                    message="employee_id is required for task prioritization",
                    suggestions=["Provide employee_id in context"]
                )

            # Get prioritized tasks
            prioritized_tasks = self.service.prioritize_employee_tasks(employee_id)

            return AgentResponse(
                success=True,
                agent_used=self.name,
                result=prioritized_tasks,
                message=f"Successfully prioritized {len(prioritized_tasks)} tasks",
                suggestions=[
                    "Focus on high-priority tasks first",
                    "Consider delegating low-priority tasks"
                ]
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                agent_used=self.name,
                result=None,
                message=f"Error: {str(e)}"
            )


class BurnoutDetectionAgent(Agent):
    """Agent for burnout detection and prevention"""

    def __init__(self):
        super().__init__(
            name="Burnout Detection Agent",
            description="Monitors and predicts employee burnout risk"
        )
        self.service = BurnoutDetectionService()

    async def can_handle(self, task: str, context: Dict[str, Any]) -> float:
        keywords = ["burnout", "stress", "wellbeing", "health", "tired", "exhausted", "overwork"]
        task_lower = task.lower()
        return max([0.9 if keyword in task_lower else 0.0 for keyword in keywords] + [0.0])

    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        try:
            employee_id = context.get("employee_id")
            if not employee_id:
                return AgentResponse(
                    success=False,
                    agent_used=self.name,
                    result=None,
                    message="employee_id is required for burnout detection"
                )

            # Calculate burnout risk
            burnout_data = self.service.calculate_burnout_risk(employee_id)

            # Generate recommendations
            recommendations = self.service.generate_recommendations(burnout_data)

            return AgentResponse(
                success=True,
                agent_used=self.name,
                result={
                    "burnout_data": burnout_data,
                    "recommendations": recommendations
                },
                message=f"Burnout risk level: {burnout_data.get('risk_level', 'unknown')}",
                suggestions=recommendations[:3] if recommendations else []
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                agent_used=self.name,
                result=None,
                message=f"Error: {str(e)}"
            )


class WorkloadBalancingAgent(Agent):
    """Agent for workload balancing across teams"""

    def __init__(self):
        super().__init__(
            name="Workload Balancing Agent",
            description="Balances workload across team members equitably"
        )
        self.service = WorkloadBalancingService()

    async def can_handle(self, task: str, context: Dict[str, Any]) -> float:
        keywords = ["balance", "distribute", "workload", "equitable", "fair", "share", "team load"]
        task_lower = task.lower()
        return max([0.9 if keyword in task_lower else 0.0 for keyword in keywords] + [0.0])

    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        try:
            team_id = context.get("team_id")
            if not team_id:
                return AgentResponse(
                    success=False,
                    agent_used=self.name,
                    result=None,
                    message="team_id is required for workload balancing"
                )

            # Calculate workload equity
            equity_report = self.service.calculate_team_equity(team_id)

            # Get recommendations
            recommendations = self.service.suggest_rebalancing(team_id)

            return AgentResponse(
                success=True,
                agent_used=self.name,
                result={
                    "equity_report": equity_report,
                    "recommendations": recommendations
                },
                message="Workload analysis complete",
                suggestions=[r.get("action", "") for r in recommendations[:3]] if recommendations else []
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                agent_used=self.name,
                result=None,
                message=f"Error: {str(e)}"
            )


class TaskExtractionAgent(Agent):
    """Agent for extracting tasks from text using NLP"""

    def __init__(self):
        super().__init__(
            name="Task Extraction Agent",
            description="Extracts tasks from emails, meeting notes, and documents using NLP"
        )
        self.service = TaskExtractionService()

    async def can_handle(self, task: str, context: Dict[str, Any]) -> float:
        keywords = ["extract", "parse", "analyze text", "find tasks", "meeting notes", "email"]
        task_lower = task.lower()
        has_text = context.get("text") is not None
        keyword_match = max([0.7 if keyword in task_lower else 0.0 for keyword in keywords] + [0.0])
        return min(keyword_match + (0.2 if has_text else 0.0), 1.0)

    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        try:
            text = context.get("text")
            if not text:
                return AgentResponse(
                    success=False,
                    agent_used=self.name,
                    result=None,
                    message="text is required for task extraction"
                )

            # Extract tasks
            extracted_tasks = self.service.extract_tasks_from_text(text)

            return AgentResponse(
                success=True,
                agent_used=self.name,
                result=extracted_tasks,
                message=f"Extracted {len(extracted_tasks)} tasks from text",
                suggestions=[
                    "Review extracted tasks for accuracy",
                    "Assign tasks to team members"
                ]
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                agent_used=self.name,
                result=None,
                message=f"Error: {str(e)}"
            )


class RecognitionAgent(Agent):
    """Agent for employee recognition and achievements"""

    def __init__(self):
        super().__init__(
            name="Recognition Agent",
            description="Tracks and recognizes employee achievements automatically"
        )
        self.service = RecognitionService()

    async def can_handle(self, task: str, context: Dict[str, Any]) -> float:
        keywords = ["recognition", "achievement", "accomplishment", "reward", "celebrate", "milestone"]
        task_lower = task.lower()
        return max([0.9 if keyword in task_lower else 0.0 for keyword in keywords] + [0.0])

    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        try:
            employee_id = context.get("employee_id")
            if not employee_id:
                return AgentResponse(
                    success=False,
                    agent_used=self.name,
                    result=None,
                    message="employee_id is required for recognition"
                )

            # Detect achievements
            achievements = self.service.detect_achievements(employee_id)

            return AgentResponse(
                success=True,
                agent_used=self.name,
                result=achievements,
                message=f"Detected {len(achievements)} achievements",
                suggestions=[
                    "Celebrate achievements with the team",
                    "Send recognition notifications"
                ]
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                agent_used=self.name,
                result=None,
                message=f"Error: {str(e)}"
            )


class MultiAgentOrchestrator:
    """Main orchestrator that routes requests to appropriate agents"""

    def __init__(self):
        self.agents = [
            TaskPrioritizationAgent(),
            BurnoutDetectionAgent(),
            WorkloadBalancingAgent(),
            TaskExtractionAgent(),
            RecognitionAgent()
        ]

    async def select_agent(self, task: str, context: Dict[str, Any]) -> Optional[Agent]:
        """Select the best agent for the task"""
        scores = []
        for agent in self.agents:
            score = await agent.can_handle(task, context)
            scores.append((agent, score))

        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)

        # Return agent with highest score if above threshold
        if scores and scores[0][1] > 0.5:
            return scores[0][0]

        return None

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute a task using the multi-agent system

        Args:
            request: AgentRequest with task and context

        Returns:
            AgentResponse with results
        """
        # If agent type is specified, use it directly
        if request.agent_type and not request.auto_detect:
            agent = self._get_agent_by_type(request.agent_type)
            if agent:
                return await agent.execute(request.task, request.context)

        # Auto-detect best agent
        agent = await self.select_agent(request.task, request.context)

        if not agent:
            return AgentResponse(
                success=False,
                agent_used="None",
                result=None,
                message="No suitable agent found for this task",
                suggestions=[
                    "Try rephrasing your task",
                    "Specify an agent_type manually",
                    f"Available agents: {', '.join([a.name for a in self.agents])}"
                ]
            )

        return await agent.execute(request.task, request.context)

    def _get_agent_by_type(self, agent_type: AgentType) -> Optional[Agent]:
        """Get agent by type"""
        agent_map = {
            AgentType.TASK_PRIORITIZATION: TaskPrioritizationAgent,
            AgentType.BURNOUT_DETECTION: BurnoutDetectionAgent,
            AgentType.WORKLOAD_BALANCING: WorkloadBalancingAgent,
            AgentType.TASK_EXTRACTION: TaskExtractionAgent,
            AgentType.RECOGNITION: RecognitionAgent
        }

        agent_class = agent_map.get(agent_type)
        if agent_class:
            for agent in self.agents:
                if isinstance(agent, agent_class):
                    return agent

        return None

    def get_available_agents(self) -> List[Dict[str, str]]:
        """Get list of available agents"""
        return [
            {
                "name": agent.name,
                "description": agent.description
            }
            for agent in self.agents
        ]


# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()
