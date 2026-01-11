import logging
from typing import Optional

logger = logging.getLogger(__name__)


def register_agents() -> None:
    """
    Register all agents in the system.
    
    Called during application startup to register available agents.
    Handles errors gracefully to prevent app startup failures.
    """
    try:
        from agent.registry import get_registry
        from agent.repair.agent import RepairAgent
        
        registry = get_registry()
        
        # Register repair agent
        repair_agent = RepairAgent()
        registry.register(repair_agent)
        
        logger.info(f"Registered {len(registry.list_agents())} agent(s)")
    except ImportError as e:
        logger.error(f"Failed to import agent modules: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Failed to register agents: {e}", exc_info=True)
        # Don't re-raise - allow app to start even if agent registration fails
        # Agents can be registered later if needed
