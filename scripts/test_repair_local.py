
import asyncio
import logging
import sys
import os

# Ensure app imports work
sys.path.append(os.getcwd())

from agent.repair.agent import RepairAgent
from app.core.config import settings

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing Repair Agent...")
    try:
        agent = RepairAgent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return

    # Mock state based on a real or mock failure
    # We use a mocked run_id. If you strictly need real GitHub data, ensure this ID exists.
    # If the agent crashes accessing GitHub, make sure GITHUB_TOKEN is in .env
    initial_state = {
        "job_id": 999,  # Test ID
        "run_id": "20905043913",  # Valid recent run ID
        "repo_name": "AveryKing/solar-mender",
        "error_logs": None,
        "root_cause": None,
        "target_file_path": None,
        "original_content": None,
        "fixed_content": None,
        "context_files": {},
        "diagnosis_confidence": 0.0,
        "fix_confidence": 0.0,
        "failure_category": None,
        "commit_author": "LocalUser",
        "total_cost": 0.0,
        "status": "QUEUED",
        "error": None,
        "pr_url": None,
        "pr_draft": True
    }
    
    logger.info(f"🚀 Starting Local Repair Agent Test for Run {initial_state['run_id']}...")
    logger.info("Press Ctrl+C to stop if it hangs (e.g. on timeouts).")
    
    # Mock Vertex AI to bypass permission issues during local testing
    from unittest.mock import MagicMock
    from agent.schemas import DiagnoseResponse
    
    logger.info("⚠️ Mocking Vertex AI for local testing...")
    
    mock_model = MagicMock()
    mock_structured_llm = MagicMock()
    
    # Mock the diagnosis response
    mock_diagnosis = {
        "parsed": DiagnoseResponse(
            root_cause="The 'WorkflowRun' object does not have a 'get_logs_url' attribute. PyGithub v2 changes API structure.",
            confidence=0.95,
            steps_to_fix=["Use gh CLI to fetch logs", "Parse logs from stdout"]
        ),
        "raw": MagicMock(usage_metadata={"input_tokens": 100, "output_tokens": 50})
    }
    
    async def mock_ainvoke(*args, **kwargs):
        return mock_diagnosis
        
    mock_structured_llm.ainvoke = mock_ainvoke
    mock_model.with_structured_output.return_value = mock_structured_llm
    
    # Patch the singleton
    from agent.llm import vertex_client
    vertex_client.get_model = MagicMock(return_value=mock_model)

    try:
        # We use ainvoke to run the graph asynchronously
        final_state = await agent.graph.ainvoke(initial_state)
        
        print("\n" + "="*50)
        print("✅ Test Execution Complete")
        print("="*50)
        print(f"Final Status:      {final_state.get('status')}")
        print(f"Error Message:     {final_state.get('error')}")
        print(f"Root Cause:        {final_state.get('root_cause')}")
        print(f"Commit Author:     {final_state.get('commit_author')}")
        print(f"Diagnosis Conf:    {final_state.get('diagnosis_confidence')}")
        print(f"Total Cost:        ${final_state.get('total_cost'):.4f}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"\n❌ Test Failed to Execute: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
