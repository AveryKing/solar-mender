import logging
from github import Github, InputGitTreeElement
from app.core.config import settings
from agent.state import AgentState

logger = logging.getLogger(__name__)

async def pr_node(state: AgentState) -> AgentState:
    """
    Node: PR
    Opens a Pull Request with the fix.
    """
    if state.get("status") == "FAILED":
        return state

    logger.info(f"Opening PR for {state['repo_name']}")
    
    try:
        gh = Github(settings.GITHUB_TOKEN)
        repo = gh.get_repo(state['repo_name'])
        
        # Create a new branch
        branch_name = f"fix/repair-job-{state['job_id']}"
        sb = repo.get_branch("main")
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=sb.commit.sha)
        
        # Commit the fix
        repo.update_file(
            path=state['target_file_path'],
            message=f"Fix: Automatic repair for CI failure in run {state['run_id']}",
            content=state['fixed_content'],
            sha=repo.get_contents(state['target_file_path']).sha,
            branch=branch_name
        )
        
        # Create PR
        pr = repo.create_pull(
            title=f"Repair: Fix CI failure in run {state['run_id']}",
            body=f"This PR was automatically generated to fix the following failure:\n\n**Root Cause:** {state['root_cause']}\n\n**Estimated Vertex Cost:** ${state['total_cost']:.4f}",
            head=branch_name,
            base="main"
        )
        
        return {
            **state,
            "status": "PR_OPENED",
            "pr_url": pr.html_url
        }
    except Exception as e:
        logger.error(f"Error in pr_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
