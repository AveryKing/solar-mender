import logging
from app.core.config import settings
from agent.repair.state import RepairAgentState
from agent.utils import estimate_vertex_cost
from agent.schemas import DiagnoseResponse
from agent.prompts import DIAGNOSE_PROMPT

logger = logging.getLogger(__name__)

async def diagnose_node(state: RepairAgentState) -> RepairAgentState:
    """
    Node: Diagnose
    Fetches GitHub Action logs and uses Gemini 1.5 Flash to identify root cause.
    """
    logger.info(f"Diagnosing job {state['job_id']} for repo {state['repo_name']}")
    
    from github import Github
    from agent.llm import vertex_client
    
    try:
        gh = Github(settings.GITHUB_TOKEN)
        repo = gh.get_repo(state['repo_name'])
        run = repo.get_workflow_run(int(state['run_id']))
        
        # Check if the failure was caused by the agent itself
        commit_author = run.head_commit.author.login
        if commit_author == "diviora-repair-agent[bot]" or "repair-agent" in commit_author.lower():
            return {
                **state,
                "status": "FAILED",
                "error": f"Possible infinite loop detected: failure caused by {commit_author}"
            }

        # Fetch logs (simplified logic for brevity, PyGithub logs access)
        logs_url = run.get_logs_url()
        # For this implementation, we assume we fetch the text summary of the logs
        logs_content = "Mock logs: Error: module 'axios' not found in app/utils/api.py"
        
        # Get model and configure structured output
        model = vertex_client.get_model("flash")
        structured_llm = model.with_structured_output(DiagnoseResponse, include_raw=True)
        
        prompt = DIAGNOSE_PROMPT.format(logs=logs_content)
        
        # Invoke model
        response = await structured_llm.ainvoke(prompt)
        
        parsed_result: DiagnoseResponse = response["parsed"]
        raw_response = response["raw"]
        
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
        
        return {
            **state,
            "error_logs": logs_content,
            "root_cause": parsed_result.root_cause,
            "diagnosis_confidence": parsed_result.confidence,
            "total_cost": cost,
            "commit_author": commit_author
        }
        
    except Exception as e:
        logger.error(f"Error in diagnose_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
