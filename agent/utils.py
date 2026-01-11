from typing import Dict

def estimate_vertex_cost(
    model_name: str, 
    input_tokens: int, 
    output_tokens: int
) -> float:
    """
    Estimates the cost of a Vertex AI Gemini call.
    Prices are approximate for us-central1 (Jan 2026).
    
    Args:
        model_name: Name of the model (flash or pro)
        input_tokens: Number of prompt tokens
        output_tokens: Number of response tokens
        
    Returns:
        Estimated cost in USD.
    """
    # pricing per 1M tokens
    pricing = {
        "gemini-1.5-flash": {
            "input": 0.075,
            "output": 0.30,
        },
        "gemini-1.5-pro": {
            "input": 1.25,
            "output": 3.75,
        }
    }
    
    if model_name not in pricing:
        return 0.0
        
    cost = (input_tokens / 1_000_000) * pricing[model_name]["input"]
    cost += (output_tokens / 1_000_000) * pricing[model_name]["output"]
    
    return round(cost, 6)
