from typing import Dict, Optional, List
import logging
from agent.base import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Central registry for managing and discovering agents.
    
    Provides agent registration, lookup, and metadata access
    for MCP integration and routing.
    """
    
    def __init__(self) -> None:
        """Initialize empty agent registry."""
        self._agents: Dict[str, BaseAgent] = {}
    
    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent in the registry.
        
        Args:
            agent: Agent instance implementing BaseAgent interface.
            
        Raises:
            ValueError: If agent name is already registered.
        """
        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' is already registered")
        
        self._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """
        Get agent by name.
        
        Args:
            name: Agent name identifier.
            
        Returns:
            Agent instance if found, None otherwise.
        """
        return self._agents.get(name)
    
    def list_agents(self) -> List[BaseAgent]:
        """
        List all registered agents.
        
        Returns:
            List of all registered agent instances.
        """
        return list(self._agents.values())
    
    def get_agent_names(self) -> List[str]:
        """
        Get list of registered agent names.
        
        Returns:
            List of agent name identifiers.
        """
        return list(self._agents.keys())
    
    def get_agent_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all agents (for MCP discovery).
        
        Returns:
            List of agent metadata dictionaries containing:
            - name: Agent identifier
            - description: Agent description
            - capabilities: List of capabilities
            - tools: MCP tools exposed by agent
            - resources: MCP resources exposed by agent
        """
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "tools": agent.get_mcp_tools(),
                "resources": agent.get_mcp_resources(),
            }
            for agent in self._agents.values()
        ]
    
    def get_agent_metadata_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific agent.
        
        Args:
            name: Agent name identifier.
            
        Returns:
            Agent metadata dictionary if found, None otherwise.
        """
        agent = self.get(name)
        if not agent:
            return None
        
        return {
            "name": agent.name,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "tools": agent.get_mcp_tools(),
            "resources": agent.get_mcp_resources(),
        }


# Global registry instance
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """
    Get the global agent registry instance.
    
    Returns:
        Global AgentRegistry singleton.
    """
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
