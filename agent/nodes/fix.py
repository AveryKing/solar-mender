import logging
from github import Github
from app.core.config import settings
from agent.state import AgentState
from agent.llm import vertex_client
from agent.utils import estimate_vertex_cost

logger = logging.getLogger(__name__)

async def fix_node(state: AgentState) -> AgentState:
    """
    Node: Fix
    Generates the corrected file content using Gemini 1.5 Pro.
    """
    if state.get("status") == "FAILED":
        return state

    logger.info(f"Generating fix for {state['target_file_path']}")
    
    try:
        gh = Github(settings.GITHUB_TOKEN)
        repo = gh.get_repo(state['repo_name'])
        
        # Fetch current content
        file_content = repo.get_contents(state['target_file_path'])
        original_text = file_content.decoded_content.decode()
        
        model = await vertex_client.get_model("pro")
        prompt = f"""
        You are an expert software engineer. Fix the following code based on the reported root cause.
        Return ONLY the full corrected file content. No markdown blocks.
        
        Root Cause: {state['root_cause']}
        
        File Path: {state['target_file_path']}
        
        Original Content:
        {original_text}
        """
        
        response = await model.generate_content_async(prompt)
        fixed_text = response.text.strip()
        
        # Estimate cost
        cost = estimate_vertex_cost(
            "gemini-1.5-pro", 
            response.usage_metadata.prompt_token_count,
            response.usage_metadata.candidates_token_count
        )
        
        return {
            **state,
            "original_content": original_text,
            "fixed_content": fixed_text,
            "total_cost": cost
        }
    except Exception as e:
        logger.error(f"Error in fix_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
