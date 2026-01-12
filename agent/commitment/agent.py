from typing import Dict, Any, List
import logging

from agent.base import BaseAgent
from agent.commitment.graph import create_commitment_graph

logger = logging.getLogger(__name__)

class CommitmentAgent(BaseAgent):
    """
    Agent for crafting high-fidelity 'human-grade' commit messages.
    """
    
    def __init__(self) -> None:
        self._graph: Any = create_commitment_graph()
        self._name: str = "commitment"
        self._description: str = "Crafts professional, human-grade commit messages following the 50/72 rule and explaining the 'Why' vs 'What'."
        self._capabilities: List[str] = ["craft_commit"]
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def capabilities(self) -> List[str]:
        return self._capabilities
    
    @property
    def graph(self) -> Any:
        return self._graph
    
    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute commitment agent.
        Expected state keys:
            - diff: str
            - context: Optional[str]
        """
        return await self._graph.ainvoke(state)
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "mender.craft_commit",
                "description": "Generate a high-fidelity commit message based on a git diff and optional context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "diff": {
                            "type": "string",
                            "description": "The git diff output"
                        },
                        "context": {
                            "type": "string",
                            "description": "Optional context about the changes"
                        }
                    },
                    "required": ["diff"]
                }
            }
        ]
