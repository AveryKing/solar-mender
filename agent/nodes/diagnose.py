import logging
from github import Github
from app.core.config import settings
from agent.state import AgentState
from agent.llm import vertex_client
from agent.utils import estimate_vertex_cost

logger = logging.getLogger(__name__)

async def diagnose_node(state: AgentState) -> AgentState:
    """
    Node: Diagnose
    Fetches GitHub Action logs and uses Gemini 1.5 Flash to identify root cause.
    """
    logger.info(f"Diagnosing job {state['job_id']} for repo {state['repo_name']}")
    
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
        # Note: In a real scenario, logs can be large; we'd fetch specific failed jobs
        logs_url = run.get_logs_url()
        # For this implementation, we assume we fetch the text summary of the logs
        # ... fetch logs ...
        logs_content = "Mock logs: Error: module 'axios' not found in app/utils/api.py"
        
        model = await vertex_client.get_model("flash")
        prompt = f"""
        Analyze the following GitHub Action failure logs and summarize the root cause in one sentence.
        Logs:
        {logs_content}
        """
        
        response = await model.generate_content_async(prompt)
        
        # Estimate cost
        cost = estimate_vertex_cost(
            "gemini-1.5-flash", 
            response.usage_metadata.prompt_token_count,
            response.usage_metadata.candidates_token_count
        )
        
        return {
            **state,
            "error_logs": logs_content,
            "root_cause": response.text.strip(),
            "total_cost": cost,
            "commit_author": commit_author
        }
        
    except Exception as e:
        logger.error(f"Error in diagnose_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
