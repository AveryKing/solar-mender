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
        
        from app.core.config import settings
        
        # Build PR body with confidence scores and metadata
        pr_body = f"""This PR was automatically generated to fix the following CI failure.

**Root Cause:** {state.get('root_cause', 'Unknown')}

**Failure Category:** {state.get('failure_category', 'unknown')}

**Confidence Scores:**
- Diagnosis: {state.get('diagnosis_confidence', 0.0):.1%}
- Fix: {state.get('fix_confidence', 0.0):.1%}

**Estimated Vertex Cost:** ${state.get('total_cost', 0.0):.4f}

**⚠️ Please review carefully before merging.**"""
        
        # Create PR (draft by default for human-in-the-loop)
        is_draft = settings.PR_DRAFT_BY_DEFAULT and not settings.AUTO_MERGE_ENABLED
        pr = repo.create_pull(
            title=f"Repair: Fix CI failure in run {state['run_id']}",
            body=pr_body,
            head=branch_name,
            base="main",
            draft=is_draft
        )
        
        logger.info(f"Created {'draft' if is_draft else 'ready'} PR: {pr.html_url}")
        
        return {
            **state,
            "status": "PR_OPENED",
            "pr_url": pr.html_url,
            "pr_draft": is_draft
        }
    except Exception as e:
        logger.error(f"Error in pr_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
