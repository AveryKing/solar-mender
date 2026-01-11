import logging
from github import Github
from app.core.config import settings
from agent.repair.state import RepairAgentState
from agent.llm import vertex_client
from agent.utils import estimate_vertex_cost
from agent.context import get_related_files
from agent.schemas import LocateResponse

logger = logging.getLogger(__name__)

async def locate_node(state: RepairAgentState) -> RepairAgentState:
    """
    Node: Locate
    Identifies which file needs fixing based on the root cause.
    Also gathers context files for better understanding.
    """
    if state.get("status") == "FAILED":
        return state

    logger.info(f"Locating file for root cause: {state['root_cause']}")
    
    try:
        gh = Github(settings.GITHUB_TOKEN)
        repo = gh.get_repo(state['repo_name'])
        
        # Get model and configure structured output
        model = vertex_client.get_model("flash")
        structured_llm = model.with_structured_output(LocateResponse, include_raw=True)
        
        prompt = f"""
        Based on this root cause of a CI/CD failure, identify the absolute file path that likely needs to be fixed.
        
        Root Cause: {state['root_cause']}
        Error Logs: {state.get('error_logs', '')[:500]}
        """
        
        # Invoke model
        response = await structured_llm.ainvoke(prompt)
        
        parsed_result: LocateResponse = response["parsed"]
        raw_response = response["raw"]
        target_file = parsed_result.file_path.strip()
        
        # Gather context files for better understanding
        context_files = await get_related_files(repo, state['repo_name'], target_file, state.get('root_cause', ''))
        
        logger.info(f"Located target file: {target_file}, gathered {len(context_files)} context files")
        
        # Get token usage from metadata
        usage = raw_response.usage_metadata or {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        # Estimate cost
        cost = estimate_vertex_cost(
            "gemini-1.5-flash", 
            input_tokens,
            output_tokens
        )
        
        # Store context files in state (we'll use them in fix_node)
        state_with_context = {
            **state,
            "target_file_path": target_file,
            "total_cost": cost,
            "context_files": context_files  # Store for fix_node
        }
        
        return state_with_context
    except Exception as e:
        logger.error(f"Error in locate_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
