from typing import Dict, Any, List
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from agent.registry import get_registry
from app.db.base import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

router = APIRouter()
logger = logging.getLogger(__name__)


class MCPToolRequest(BaseModel):
    """Request model for MCP tool invocations."""
    tool_name: str = Field(..., description="Name of the MCP tool to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class MCPToolResponse(BaseModel):
    """Response model for MCP tool invocations."""
    success: bool
    result: Any = None
    error: str = None


@router.post("/invoke", response_model=MCPToolResponse)
async def invoke_mcp_tool(
    request: MCPToolRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Invoke an MCP tool exposed by any registered agent.
    
    This endpoint allows the IDE agent (Cursor) to delegate tasks to Solar Mender
    via the Model Context Protocol (MCP).
    
    Args:
        request: Tool invocation request with tool_name and arguments.
        db: Database session.
        
    Returns:
        MCPToolResponse with success status and result/error.
        
    Raises:
        HTTPException: If tool not found or invocation fails.
    """
    registry = get_registry()
    
    # Find the tool across all agents
    tool_agent = None
    tool_def = None
    
    for agent_name in registry.list_agents():
        agent = registry.get(agent_name)
        tools = agent.get_mcp_tools()
        
        for tool in tools:
            if tool["name"] == request.tool_name:
                tool_agent = agent
                tool_def = tool
                break
        
        if tool_agent:
            break
    
    if not tool_agent or not tool_def:
        raise HTTPException(
            status_code=404,
            detail=f"MCP tool '{request.tool_name}' not found"
        )
    
    try:
        # Route to appropriate handler based on tool name
        if request.tool_name == "mender.monitor_deployment":
            result = await handle_monitor_deployment(
                request.arguments, tool_agent, db
            )
        elif request.tool_name == "mender.craft_commit":
            result = await handle_craft_commit(
                request.arguments, tool_agent, db
            )
        elif request.tool_name == "mender.remote_build":
            result = await handle_remote_build(
                request.arguments, tool_agent, db
            )
        else:
            # Generic agent invocation for other tools
            result = await tool_agent.invoke(request.arguments)
        
        return MCPToolResponse(success=True, result=result)
    
    except Exception as e:
        logger.error(f"Error invoking MCP tool '{request.tool_name}': {e}", exc_info=True)
        return MCPToolResponse(
            success=False,
            error=str(e)
        )


async def handle_monitor_deployment(
    arguments: Dict[str, Any],
    agent,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Handle monitor_deployment tool invocation.
    
    Starts background monitoring of a GitHub Actions run.
    If the run fails, automatically triggers repair agent.
    
    Args:
        arguments: Tool arguments (run_id, repo_name).
        agent: The repair agent instance.
        db: Database session.
        
    Returns:
        Dict with job_id and monitoring status.
    """
    from app.db.models import JobStatus, RepairJob
    
    run_id = arguments.get("run_id")
    repo_name = arguments.get("repo_name")
    
    if not run_id or not repo_name:
        raise ValueError("run_id and repo_name are required")
    
    # Create a job record for tracking
    
    job = RepairJob(
        repo_name=repo_name,
        run_id=str(run_id),
        status=JobStatus.PENDING,
        vertex_cost_est=0.0
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # For now, return job ID for status tracking
    # In production, this would:
    # 1. Use Cloud Tasks with delay to poll GitHub API
    # 2. Check run status periodically
    # 3. Trigger repair agent automatically on failure
    # 4. Notify client when complete
    
    logger.info(f"Created monitoring job {job.id} for run {run_id}")
    
    return {
        "job_id": job.id,
        "status": "monitoring",
        "message": f"Monitoring job {job.id} created for run {run_id}. Use job status endpoint to check progress."
    }


async def handle_craft_commit(
    arguments: Dict[str, Any],
    agent,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Handle craft_commit tool invocation.
    
    Generates a high-fidelity commit message using the CommitmentAgent.
    
    Args:
        arguments: Tool arguments (diff, context).
        agent: The commitment agent instance.
        db: Database session (not used but required by signature).
        
    Returns:
        Dict with commit_message.
    """
    diff = arguments.get("diff")
    context = arguments.get("context", "")
    
    if not diff:
        raise ValueError("diff is required")
    
    # Prepare state for commitment agent
    state = {
        "diff": diff,
        "context": context,
        "status": "RUNNING",
        "job_id": 0,  # Not persisted for commit messages
        "agent_name": "commitment",
        "data": {},
        "metadata": {},
        "total_cost": 0.0
    }
    
    # Invoke agent
    result = await agent.invoke(state)
    
    return {
        "commit_message": result.get("commit_message"),
        "logical_groups": result.get("logical_groups", [])
    }


async def handle_remote_build(
    arguments: Dict[str, Any],
    agent,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Handle remote_build tool invocation.
    
    Triggers a build in a remote environment (GitHub Actions).
    For now, returns instructions - full implementation would trigger a workflow.
    
    Args:
        arguments: Tool arguments (branch, repo_name).
        agent: Not used but required by signature.
        db: Database session (not used but required by signature).
        
    Returns:
        Dict with build status.
    """
    branch = arguments.get("branch", "main")
    repo_name = arguments.get("repo_name")
    
    if not repo_name:
        raise ValueError("repo_name is required")
    
    # In a full implementation, this would:
    # 1. Trigger a GitHub Actions workflow for the branch
    # 2. Monitor the build
    # 3. If it fails, trigger the repair agent
    # For now, return a placeholder response
    
    return {
        "status": "not_implemented",
        "message": "Remote build feature requires GitHub Actions workflow trigger API integration",
        "branch": branch,
        "repo_name": repo_name
    }
