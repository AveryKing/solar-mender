"""
Prompt templates for the repair agent nodes.
"""

DIAGNOSE_PROMPT = """
You are an expert software engineer analyzing CI/CD failure logs.

Analyze the following GitHub Action failure logs and provide:
1. A concise root cause summary (one sentence)
2. A confidence score (0.0-1.0) indicating how certain you are about this diagnosis

Common failure patterns:
- Missing imports/dependencies: "import error", "module not found"
- Syntax errors: "syntax error", "invalid syntax", "indentation error"
- Test failures: "test failed", "assertion error"
- Configuration issues: "config error", "environment variable"

Format your response as JSON:
{{
    "root_cause": "concise summary of the root cause",
    "confidence": 0.85
}}

Logs:
{logs}
"""

FIX_PROMPT = """
You are an expert software engineer fixing CI/CD failures.

Fix the following code based on the reported root cause. 
Return your response as JSON with:
1. The complete fixed file content
2. A confidence score (0.0-1.0) indicating how certain you are this fix will work
3. A brief explanation of the fix

Rules:
- Return ONLY valid JSON, no markdown blocks
- Include the complete file content (don't show diffs)
- Maintain existing code style and patterns
- Only fix what's broken, don't refactor unnecessarily
- Pay attention to imports and related files context

Example fixes:
- Missing import: Add the import statement at the top
- Syntax error: Fix the syntax while maintaining style
- Type error: Add type hints or fix type mismatches
- Missing dependency: Add to requirements.txt if needed

Format:
{{
    "fixed_content": "complete file content here",
    "confidence": 0.9,
    "explanation": "brief explanation of what was fixed"
}}

Root Cause: {root_cause}

File Path: {file_path}

Original Content:
{original_content}
"""

CONTEXT_READING_PROMPT = """
Analyze the codebase structure and identify related files for context.

Given:
- Target file: {target_file}
- Root cause: {root_cause}

Return a JSON array of file paths that should be read for context (imports, tests, configs, etc.):
{{
    "related_files": ["path/to/file1", "path/to/file2"]
}}
"""
