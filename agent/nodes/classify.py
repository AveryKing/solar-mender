import logging
import json
from agent.state import AgentState
from agent.classification import classify_failure, should_auto_fix
from app.core.config import settings

logger = logging.getLogger(__name__)

async def classify_node(state: AgentState) -> AgentState:
    """
    Node: Classify
    Classifies the failure category and determines if it should be auto-fixed.
    """
    if state.get("status") == "FAILED":
        return state

    logger.info(f"Classifying failure for job {state['job_id']}")

    try:
        root_cause = state.get("root_cause", "")
        error_logs = state.get("error_logs", "")

        category, confidence = classify_failure(root_cause, error_logs)
        should_fix = should_auto_fix(category, confidence, settings.MIN_CONFIDENCE_THRESHOLD)

        logger.info(f"Failure category: {category}, confidence: {confidence:.2f}, should_fix: {should_fix}")

        # If confidence too low or category not fixable, skip to end
        if not should_fix:
            return {
                **state,
                "failure_category": category.value,
                "diagnosis_confidence": confidence,
                "status": "FAILED",
                "error": f"Failure category '{category.value}' with confidence {confidence:.2f} below threshold or not auto-fixable"
            }

        return {
            **state,
            "failure_category": category.value,
            "diagnosis_confidence": confidence
        }

    except Exception as e:
        logger.error(f"Error in classify_node: {e}")
        return {**state, "status": "FAILED", "error": str(e)}
