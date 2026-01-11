from typing import Dict, List, Tuple
from enum import Enum

class FailureCategory(str, Enum):
    """Categories of CI/CD failures for routing."""
    DEPENDENCY = "dependency"
    SYNTAX = "syntax"
    TEST = "test"
    CONFIG = "config"
    INFRASTRUCTURE = "infrastructure"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

# Common failure patterns for classification
FAILURE_PATTERNS: Dict[FailureCategory, List[str]] = {
    FailureCategory.DEPENDENCY: [
        "module not found",
        "package not found",
        "import error",
        "cannot find module",
        "missing dependency"
    ],
    FailureCategory.SYNTAX: [
        "syntax error",
        "indentation error",
        "invalid syntax",
        "unexpected token"
    ],
    FailureCategory.TEST: [
        "test failed",
        "assertion error",
        "test suite failed",
        "unit test"
    ],
    FailureCategory.CONFIG: [
        "configuration error",
        "config file",
        "environment variable",
        ".env"
    ],
    FailureCategory.INFRASTRUCTURE: [
        "connection refused",
        "permission denied",
        "disk space",
        "memory error"
    ],
    FailureCategory.TIMEOUT: [
        "timeout",
        "timed out",
        "execution timeout"
    ]
}

def classify_failure(root_cause: str, logs: str) -> Tuple[FailureCategory, float]:
    """
    Classifies a failure into a category with confidence score.
    
    Args:
        root_cause: The root cause summary from diagnose node.
        logs: Raw error logs for pattern matching.
        
    Returns:
        Tuple of (category, confidence_score) where confidence is 0.0-1.0.
    """
    combined_text = f"{root_cause.lower()} {logs.lower()}"
    
    matches: Dict[FailureCategory, int] = {
        category: 0 for category in FailureCategory
    }
    
    for category, patterns in FAILURE_PATTERNS.items():
        for pattern in patterns:
            if pattern in combined_text:
                matches[category] += 1
    
    # Find category with most matches
    max_matches = max(matches.values())
    
    if max_matches == 0:
        return (FailureCategory.UNKNOWN, 0.3)
    
    # Get category with highest match count
    best_category = max(matches.items(), key=lambda x: x[1])[0]
    
    # Confidence is based on match ratio (simple heuristic)
    total_patterns = sum(len(patterns) for patterns in FAILURE_PATTERNS.values())
    confidence = min(0.9, 0.5 + (max_matches / total_patterns) * 0.4)
    
    return (best_category, confidence)

def should_auto_fix(category: FailureCategory, confidence: float, min_threshold: float = 0.7) -> bool:
    """
    Determines if a failure should be auto-fixed based on category and confidence.
    
    Args:
        category: The failure category.
        confidence: The confidence score (0.0-1.0).
        min_threshold: Minimum confidence required for auto-fix.
        
    Returns:
        True if should auto-fix, False otherwise.
    """
    # Don't auto-fix infrastructure or timeout issues
    skip_categories = {FailureCategory.INFRASTRUCTURE, FailureCategory.TIMEOUT}
    
    if category in skip_categories:
        return False
    
    return confidence >= min_threshold
