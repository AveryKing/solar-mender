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
        
        from agent.prompts import FIX_PROMPT
        
        # Build context from related files
        context_summary = ""
        context_files = state.get("context_files", {})
        if context_files:
            context_summary = "\n\nRelated Files Context:\n"
            for file_path, content in list(context_files.items())[:3]:  # Limit to 3 files
                context_summary += f"\n--- {file_path} ---\n{content[:500]}\n"
        
        model = await vertex_client.get_model("pro")
        prompt = FIX_PROMPT.format(
            root_cause=state['root_cause'],
            file_path=state['target_file_path'],
            original_content=original_text
        ) + context_summary
        
        response = await model.generate_content_async(prompt)
        
        # Parse JSON response
        try:
            result = json.loads(response.text.strip())
            fixed_text = result.get("fixed_content", "")
            fix_confidence = float(result.get("confidence", 0.5))
            explanation = result.get("explanation", "")
            logger.info(f"Fix explanation: {explanation}, confidence: {fix_confidence:.2f}")
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse fix response as JSON: {e}, using raw text")
            fixed_text = response.text.strip()
            fix_confidence = 0.5
        
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
            "fix_confidence": fix_confidence,
            "total_cost": cost
        }
    except Exception as e:
        logger.error(f"Error in fix_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
