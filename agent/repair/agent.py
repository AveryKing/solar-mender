from typing import Dict, Any, List
import logging
from langgraph.graph import CompiledGraph

from agent.base import BaseAgent
from agent.repair.graph import create_repair_graph
from agent.repair.state import RepairAgentState
from agent.repair.utils import get_langfuse_callback

logger = logging.getLogger(__name__)


class RepairAgent(BaseAgent):
    """
    Repair agent for automatically fixing CI/CD failures.
    
    This agent diagnoses GitHub Actions failures, identifies root causes,
    locates problematic files, generates fixes, and opens pull requests.
    """
    
    def __init__(self) -> None:
        """Initialize the repair agent."""
        self._graph: CompiledGraph = create_repair_graph()
        self._name: str = "repair"
        self._description: str = "Automatically diagnoses and fixes CI/CD failures in GitHub Actions workflows"
        self._capabilities: List[str] = [
            "diagnose",
            "classify",
            "locate",
            "fix",
            "create_pr"
        ]
    
    @property
    def name(self) -> str:
        """Agent identifier."""
        return self._name
    
    @property
    def description(self) -> str:
        """Human-readable agent description."""
        return self._description
    
    @property
    def capabilities(self) -> List[str]:
        """List of agent capabilities."""
        return self._capabilities
    
    @property
    def graph(self) -> CompiledGraph:
        """Compiled LangGraph instance."""
        return self._graph
    
    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute repair agent with given state.
        
        Args:
            state: Initial agent state dictionary. Must include:
                - job_id: Job identifier
                - run_id: GitHub Actions run ID
                - repo_name: Repository name (owner/repo)
                - total_cost: Initial cost (default 0.0)
                - status: Initial status (default "FIXING")
                - pr_draft: Whether PR should be draft (default False)
        
        Returns:
            Final agent state dictionary after execution.
        """
        langfuse_handler = get_langfuse_callback()
        
        final_state = await self._graph.ainvoke(
            state,
            config={"callbacks": [langfuse_handler] if langfuse_handler else []}
        )
        
        if langfuse_handler:
            langfuse_handler.flush()
        
        return final_state
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Return MCP tools this agent exposes.
        
        Returns:
            List of MCP tool definitions for repair agent.
        """
        return [
            {
                "name": "repair_ci_failure",
                "description": "Diagnose and fix a CI/CD failure in GitHub Actions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "run_id": {
                            "type": "string",
                            "description": "GitHub Actions workflow run ID"
                        },
                        "repo_name": {
                            "type": "string",
                            "description": "Repository name (owner/repo)"
                        }
                    },
                    "required": ["run_id", "repo_name"]
                }
            }
        ]
    
    def get_mcp_resources(self) -> List[Dict[str, Any]]:
        """
        Return MCP resources this agent exposes.
        
        Returns:
            List of MCP resource definitions for repair agent.
        """
        return [
            {
                "uri": "repair://jobs",
                "name": "Repair Jobs",
                "description": "List of repair jobs",
                "mimeType": "application/json"
            }
        ]
