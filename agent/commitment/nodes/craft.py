import logging
from agent.commitment.state import CommitmentState
from agent.commitment.schemas import CommitMessage
from agent.llm import vertex_client
from agent.prompts import COMMIT_CRAFT_PROMPT  # We will define this next

logger = logging.getLogger(__name__)

async def craft_commit_node(state: CommitmentState) -> CommitmentState:
    """
    Node: Craft high-fidelity commit message.
    Analyzes the diff and context to produce a professional 'human' commit.
    """
    if state.get("status") == "FAILED":
        return state

    try:
        model = vertex_client.get_model("pro")  # Pro for better reasoning
        structured_llm = model.with_structured_output(CommitMessage)
        
        prompt = COMMIT_CRAFT_PROMPT.format(
            diff=state["diff"],
            context=state.get("context", "No extra context provided.")
        )
        
        response: CommitMessage = await structured_llm.ainvoke(prompt)
        
        message = f"{response.subject}\n\n{response.body}"
        
        return {
            **state,
            "commit_message": message,
            "status": "COMPLETED"
        }
    except Exception as e:
        logger.error(f"Error in craft_commit_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
