import logging
from github import Github
from app.core.config import settings
from agent.repair.state import RepairAgentState
from agent.llm import vertex_client
from agent.utils import estimate_vertex_cost
from agent.schemas import FixResponse
from agent.prompts import FIX_PROMPT

logger = logging.getLogger(__name__)

async def fix_node(state: RepairAgentState) -> RepairAgentState:
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
        
        # Build context from related files
        context_summary = ""
        context_files = state.get("context_files", {})
        if context_files:
            context_summary = "\n\nRelated Files Context:\n"
            for file_path, content in list(context_files.items())[:3]:  # Limit to 3 files
                context_summary += f"\n--- {file_path} ---\n{content[:500]}\n"
        
        # Get model and configure structured output
        model = vertex_client.get_model("pro")
        structured_llm = model.with_structured_output(FixResponse, include_raw=True)
        
        prompt = FIX_PROMPT.format(
            root_cause=state['root_cause'],
            file_path=state['target_file_path'],
            original_content=original_text
        ) + context_summary
        
        # Invoke model
        response = await structured_llm.ainvoke(prompt)
        
        parsed_result: FixResponse = response["parsed"]
        raw_response = response["raw"]
        
        fixed_text = parsed_result.fixed_content
        fix_confidence = parsed_result.confidence
        explanation = parsed_result.explanation
        
        logger.info(f"Fix explanation: {explanation}, confidence: {fix_confidence:.2f}")
        
        # Get token usage from metadata
        usage = raw_response.usage_metadata or {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        # Estimate cost
        cost = estimate_vertex_cost(
            "gemini-1.5-pro", 
            input_tokens,
            output_tokens
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
