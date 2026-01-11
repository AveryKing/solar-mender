from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langgraph.graph import CompiledGraph
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base interface for all agents in the system.
    
    All agents must implement this interface to be compatible with
    the agent registry and MCP integration.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Agent identifier.
        
        Returns:
            Unique agent name (e.g., 'repair', 'test', 'review').
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable agent description.
        
        Returns:
            Description of what the agent does.
        """
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        List of agent capabilities.
        
        Returns:
            List of capability strings (e.g., ['diagnose', 'fix', 'test']).
        """
        pass
    
    @property
    @abstractmethod
    def graph(self) -> CompiledGraph:
        """
        Compiled LangGraph instance.
        
        Returns:
            Compiled LangGraph workflow for this agent.
        """
        pass
    
    @abstractmethod
    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent with given state.
        
        Args:
            state: Initial agent state dictionary.
            
        Returns:
            Final agent state dictionary after execution.
        """
        pass
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Return MCP tools this agent exposes.
        
        Override this method to expose agent-specific tools via MCP.
        
        Returns:
            List of MCP tool definitions.
        """
        return []
    
    def get_mcp_resources(self) -> List[Dict[str, Any]]:
        """
        Return MCP resources this agent exposes.
        
        Override this method to expose agent-specific resources via MCP.
        
        Returns:
            List of MCP resource definitions.
        """
        return []
