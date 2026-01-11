import logging
from github import Github
from app.core.config import settings
from agent.state import AgentState
from agent.llm import vertex_client
from agent.utils import estimate_vertex_cost
from agent.context import get_related_files

logger = logging.getLogger(__name__)

async def locate_node(state: AgentState) -> AgentState:
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
        
        model = await vertex_client.get_model("flash")
        prompt = f"""
        Based on this root cause of a CI/CD failure, identify the absolute file path that likely needs to be fixed.
        Return ONLY the file path, no markdown, no quotes.
        
        Root Cause: {state['root_cause']}
        Error Logs: {state.get('error_logs', '')[:500]}
        """
        
        response = await model.generate_content_async(prompt)
        target_file = response.text.strip().replace("`", "").replace('"', "").replace("'", "")
        
        # Gather context files for better understanding
        context_files = await get_related_files(repo, state['repo_name'], target_file, state.get('root_cause', ''))
        
        logger.info(f"Located target file: {target_file}, gathered {len(context_files)} context files")
        
        # Estimate cost
        cost = estimate_vertex_cost(
            "gemini-1.5-flash", 
            response.usage_metadata.prompt_token_count,
            response.usage_metadata.candidates_token_count
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
