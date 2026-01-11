from typing import List, Dict, Optional
import logging
from github import Github, GithubException
from app.core.config import settings

logger = logging.getLogger(__name__)

async def get_related_files(
    repo: Github,
    repo_name: str,
    target_file: str,
    root_cause: str
) -> Dict[str, str]:
    """
    Identifies and reads related files for context.
    
    Args:
        repo: GitHub repository object.
        repo_name: Full repository name (owner/repo).
        target_file: The file that needs fixing.
        root_cause: Root cause summary for context.
        
    Returns:
        Dictionary mapping file paths to their contents.
    """
    context_files: Dict[str, str] = {}
    
    try:
        # Always include the target file
        try:
            content = repo.get_contents(target_file)
            if isinstance(content, list):
                # Directory, skip
                pass
            else:
                context_files[target_file] = content.decoded_content.decode()
        except GithubException as e:
            logger.warning(f"Could not read target file {target_file}: {e}")
        
        # Read imports from the target file if it's Python
        if target_file.endswith(".py") and target_file in context_files:
            imports = extract_imports(context_files[target_file])
            for imp in imports[:5]:  # Limit to 5 imports
                try:
                    imp_file = resolve_import_path(imp, target_file, repo_name)
                    if imp_file and imp_file not in context_files:
                        content = repo.get_contents(imp_file)
                        if not isinstance(content, list):
                            context_files[imp_file] = content.decoded_content.decode()
                except (GithubException, ValueError):
                    pass  # Skip if can't resolve
        
        # Try to find test file for the target file
        test_file = find_test_file(target_file)
        if test_file:
            try:
                content = repo.get_contents(test_file)
                if not isinstance(content, list):
                    context_files[test_file] = content.decoded_content.decode()
            except GithubException:
                pass
        
        # Read common config files if relevant
        if "config" in root_cause.lower() or "environment" in root_cause.lower():
            config_files = ["requirements.txt", "pyproject.toml", ".env.example"]
            for config_file in config_files:
                if config_file not in context_files:
                    try:
                        content = repo.get_contents(config_file)
                        if not isinstance(content, list):
                            context_files[config_file] = content.decoded_content.decode()
                    except GithubException:
                        pass
        
    except Exception as e:
        logger.error(f"Error gathering context files: {e}")
    
    return context_files

def extract_imports(file_content: str) -> List[str]:
    """Extracts import statements from Python file."""
    imports: List[str] = []
    lines = file_content.split("\n")
    
    for line in lines:
        line = line.strip()
        if line.startswith("import ") or line.startswith("from "):
            if line.startswith("from "):
                # Extract module name
                module = line.split(" import")[0].replace("from ", "").strip()
                imports.append(module)
            else:
                # Extract module name
                module = line.replace("import ", "").strip().split()[0]
                imports.append(module)
    
    return imports[:10]  # Limit imports

def resolve_import_path(module: str, current_file: str, repo_name: str) -> Optional[str]:
    """
    Attempts to resolve an import to a file path.
    
    This is a simplified version - in production, you'd use importlib or AST parsing.
    """
    # Remove relative imports for now
    if module.startswith("."):
        return None
    
    # Simple heuristics for common patterns
    module_parts = module.split(".")
    
    # Try as-is
    path = "/".join(module_parts) + ".py"
    
    # For app/ imports, try app/ structure
    if current_file.startswith("app/"):
        if not path.startswith("app/"):
            path = f"app/{path}"
    
    return path

def find_test_file(file_path: str) -> Optional[str]:
    """Attempts to find a test file for the given file path."""
    # Common patterns: test_*.py, *_test.py, tests/*.py
    if file_path.endswith(".py"):
        base = file_path.replace(".py", "")
        
        # Try test_*.py pattern
        test_path = base.replace("/", "/test_")
        if not test_path.startswith("test_"):
            parts = test_path.split("/")
            parts[-1] = f"test_{parts[-1]}"
            test_path = "/".join(parts)
        test_path += ".py"
        
        # Try tests/ directory
        if "/" in test_path:
            test_path2 = test_path.rsplit("/", 1)[0] + "/tests/" + test_path.rsplit("/", 1)[1]
            return test_path2
        
        return test_path
    
    return None
