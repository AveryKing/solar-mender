import logging
from agent.state import AgentState
from agent.llm import vertex_client
from agent.utils import estimate_vertex_cost

logger = logging.getLogger(__name__)

async def locate_node(state: AgentState) -> AgentState:
    """
    Node: Locate
    Identifies which file needs fixing based on the root cause.
    """
    if state.get("status") == "FAILED":
        return state

    logger.info(f"Locating file for root cause: {state['root_cause']}")
    
    try:
        model = await vertex_client.get_model("flash")
        prompt = f"""
        Based on this root cause of a CI/CD failure, identify the absolute file path that likely needs to be fixed.
        Return ONLY the file path.
        Root Cause: {state['root_cause']}
        """
        
        response = await model.generate_content_async(prompt)
        target_file = response.text.strip().replace("`", "")
        
        # Estimate cost
        cost = estimate_vertex_cost(
            "gemini-1.5-flash", 
            response.usage_metadata.prompt_token_count,
            response.usage_metadata.candidates_token_count
        )
        
        return {
            **state,
            "target_file_path": target_file,
            "total_cost": cost
        }
    except Exception as e:
        logger.error(f"Error in locate_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
