from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from agent.registry import get_registry

router = APIRouter()


@router.get("", response_model=List[Dict[str, Any]])
async def list_agents():
    """
    List all registered agents with metadata.
    
    Returns:
        List of agent metadata dictionaries.
    """
    registry = get_registry()
    return registry.get_agent_metadata()


@router.get("/{agent_name}", response_model=Dict[str, Any])
async def get_agent(agent_name: str):
    """
    Get metadata for a specific agent.
    
    Args:
        agent_name: Agent identifier.
        
    Returns:
        Agent metadata dictionary.
        
    Raises:
        HTTPException: If agent not found.
    """
    registry = get_registry()
    metadata = registry.get_agent_metadata_by_name(agent_name)
    
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    return metadata


@router.get("/{agent_name}/tools", response_model=List[Dict[str, Any]])
async def get_agent_tools(agent_name: str):
    """
    Get MCP tools exposed by a specific agent.
    
    Args:
        agent_name: Agent identifier.
        
    Returns:
        List of MCP tool definitions.
        
    Raises:
        HTTPException: If agent not found.
    """
    registry = get_registry()
    agent = registry.get(agent_name)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    return agent.get_mcp_tools()


@router.get("/{agent_name}/resources", response_model=List[Dict[str, Any]])
async def get_agent_resources(agent_name: str):
    """
    Get MCP resources exposed by a specific agent.
    
    Args:
        agent_name: Agent identifier.
        
    Returns:
        List of MCP resource definitions.
        
    Raises:
        HTTPException: If agent not found.
    """
    registry = get_registry()
    agent = registry.get(agent_name)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    return agent.get_mcp_resources()
