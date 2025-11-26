"""
Multi-Agent API Endpoints
Unified API for all AI features through intelligent agent routing
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.multi_agent_system import (
    orchestrator,
    AgentRequest,
    AgentResponse,
    AgentType
)

router = APIRouter()


@router.post("/agent/execute", response_model=AgentResponse)
async def execute_agent_task(request: AgentRequest, db: Session = Depends(get_db)):
    """
    Execute a task using the multi-agent system

    This unified endpoint automatically routes your request to the appropriate agent.

    Examples:
    - "Prioritize my tasks" → Task Prioritization Agent
    - "Check burnout risk for employee" → Burnout Detection Agent
    - "Balance team workload" → Workload Balancing Agent
    - "Extract tasks from this email" → Task Extraction Agent
    - "Show achievements for employee" → Recognition Agent

    Args:
        request: AgentRequest containing:
            - task: Natural language description of what you want to do
            - context: Additional context (employee_id, team_id, text, etc.)
            - agent_type: (Optional) Force a specific agent
            - auto_detect: Whether to auto-detect the best agent (default: True)

    Returns:
        AgentResponse with results and suggestions
    """
    try:
        # Add db to context
        if request.context is None:
            request.context = {}
        request.context["db"] = db
        
        response = await orchestrator.execute(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/available")
async def get_available_agents():
    """
    Get list of available agents and their capabilities

    Returns:
        List of agents with names and descriptions
    """
    return {
        "agents": orchestrator.get_available_agents(),
        "total": len(orchestrator.agents)
    }


@router.post("/agent/smart-assist")
async def smart_assist(
    query: str,
    employee_id: int = None,
    team_id: int = None,
    additional_context: Dict[str, Any] = {}
):
    """
    Smart assistant endpoint - just ask a question in natural language

    This is a simplified interface that automatically builds the context
    and routes to the right agent.

    Examples:
    - "What should I work on next?" (with employee_id)
    - "Am I at risk of burnout?" (with employee_id)
    - "Is my team's workload balanced?" (with team_id)

    Args:
        query: Natural language question or command
        employee_id: Optional employee ID
        team_id: Optional team ID
        additional_context: Any additional context data

    Returns:
        AgentResponse with results
    """
    # Build context
    context = additional_context.copy()
    if employee_id:
        context["employee_id"] = employee_id
    if team_id:
        context["team_id"] = team_id

    # Create request
    request = AgentRequest(
        task=query,
        context=context,
        auto_detect=True
    )

    try:
        response = await orchestrator.execute(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/batch")
async def batch_execute(requests: List[AgentRequest]):
    """
    Execute multiple agent requests in batch

    Useful for complex workflows that require multiple agents.

    Args:
        requests: List of AgentRequest objects

    Returns:
        List of AgentResponse objects
    """
    results = []
    for request in requests:
        try:
            response = await orchestrator.execute(request)
            results.append(response)
        except Exception as e:
            results.append(
                AgentResponse(
                    success=False,
                    agent_used="None",
                    result=None,
                    message=f"Error: {str(e)}"
                )
            )

    return {
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r.success)
    }


@router.get("/agent/examples")
async def get_examples():
    """
    Get example queries for each agent type

    Returns:
        Examples of how to use different agents
    """
    return {
        "examples": [
            {
                "agent": "Task Prioritization",
                "queries": [
                    "Prioritize my tasks",
                    "What should I work on next?",
                    "Show me my most important tasks",
                    "Rank my tasks by priority"
                ],
                "required_context": ["employee_id"]
            },
            {
                "agent": "Burnout Detection",
                "queries": [
                    "Check my burnout risk",
                    "Am I stressed?",
                    "How is my wellbeing?",
                    "Show me burnout indicators"
                ],
                "required_context": ["employee_id"]
            },
            {
                "agent": "Workload Balancing",
                "queries": [
                    "Balance team workload",
                    "Is the team's work distributed fairly?",
                    "Show workload equity",
                    "Who is overloaded?"
                ],
                "required_context": ["team_id"]
            },
            {
                "agent": "Task Extraction",
                "queries": [
                    "Extract tasks from this email",
                    "Parse meeting notes",
                    "Find tasks in this text",
                    "Analyze this document for tasks"
                ],
                "required_context": ["text"]
            },
            {
                "agent": "Recognition",
                "queries": [
                    "Show my achievements",
                    "What milestones have I reached?",
                    "Detect accomplishments",
                    "Track my progress"
                ],
                "required_context": ["employee_id"]
            }
        ]
    }


@router.post("/agent/workflow")
async def execute_workflow(
    workflow_type: str,
    employee_id: int = None,
    team_id: int = None
):
    """
    Execute pre-defined workflows that use multiple agents

    Available workflows:
    - "daily_briefing": Get priorities, burnout check, and achievements
    - "team_health": Team workload balance and burnout risks
    - "productivity_check": Task priorities and completion stats

    Args:
        workflow_type: Type of workflow to execute
        employee_id: Optional employee ID
        team_id: Optional team ID

    Returns:
        Workflow results from multiple agents
    """
    workflows = {
        "daily_briefing": [
            AgentRequest(
                task="Prioritize my tasks",
                context={"employee_id": employee_id},
                agent_type=AgentType.TASK_PRIORITIZATION
            ),
            AgentRequest(
                task="Check burnout risk",
                context={"employee_id": employee_id},
                agent_type=AgentType.BURNOUT_DETECTION
            ),
            AgentRequest(
                task="Show achievements",
                context={"employee_id": employee_id},
                agent_type=AgentType.RECOGNITION
            )
        ],
        "team_health": [
            AgentRequest(
                task="Balance team workload",
                context={"team_id": team_id},
                agent_type=AgentType.WORKLOAD_BALANCING
            ),
            AgentRequest(
                task="Check team burnout risks",
                context={"team_id": team_id},
                agent_type=AgentType.BURNOUT_DETECTION
            )
        ]
    }

    if workflow_type not in workflows:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown workflow type. Available: {list(workflows.keys())}"
        )

    # Execute workflow
    requests = workflows[workflow_type]
    results = []

    for request in requests:
        try:
            response = await orchestrator.execute(request)
            results.append(response)
        except Exception as e:
            results.append(
                AgentResponse(
                    success=False,
                    agent_used="None",
                    result=None,
                    message=f"Error: {str(e)}"
                )
            )

    return {
        "workflow": workflow_type,
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r.success)
    }
