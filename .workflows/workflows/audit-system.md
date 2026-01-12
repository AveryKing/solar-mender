---
description: Analyze the system for flaws, gaps, and technical debt
---
# System Audit Workflow

This workflow performs a comprehensive analysis of the codebase to identify:
- Security vulnerabilities
- Performance bottlenecks
- Missing error handling
- Incomplete features
- Technical debt
- Documentation gaps

## Execution Steps

// turbo-all
1. **Codebase Scan**: Review all source files in `src/` for:
   - Missing `try/catch` blocks around external API calls
   - Hardcoded secrets or API keys
   - `any` types in TypeScript
   - TODO comments or placeholder code
   - Functions without error handling

2. **Architecture Review**: Check against `.agent/knowledge/tech-stack.md`:
   - Are all external services properly abstracted?
   - Are there single points of failure?
   - Is the state management consistent across agents?

3. **Testing Coverage**: Analyze `src/` for:
   - Tools without corresponding test files
   - Nodes without integration tests
   - Critical paths without verification scripts

4. **Documentation Audit**: Verify:
   - Every agent has a corresponding doc in `docs/agents/`
   - Every tool has a corresponding doc in `docs/tools/`
   - `README.md` reflects current capabilities
   - `STATUS.md` is up to date

5. **Security Check**: Look for:
   - Environment variables used without fallbacks
   - Database queries vulnerable to injection
   - Unvalidated user inputs
   - Missing rate limiting on external API calls

6. **Performance Analysis**: Identify:
   - Synchronous operations that could be parallelized
   - Redundant API calls
   - Large data structures loaded into memory
   - Missing caching opportunities

7. **Generate Issues**: For each flaw found:
   - Create a new issue in `ISSUES.md` under "Module: Technical Debt"
   - Include severity (Critical/High/Medium/Low)
   - Provide specific file paths and line numbers
   - Suggest a fix or mitigation

8. **Workflow Analysis**: Analyze the agent development process:
   - Review `.agent/workflows/` for completeness
   - Check if workflows are documented in `.agent/workflows/README.md`
   - Verify workflows follow the standard format (YAML frontmatter + steps)
   - Identify missing workflows for common tasks
   - Check if `.agent/knowledge/` is up to date
   - Verify `AGENT_HANDBOOK.md` reflects current workflows
   - Look for workflow friction points (unclear steps, missing examples)

9. **Knowledge Base Audit**: Review agent knowledge system:
   - Check `.agent/knowledge/coding-standards.md` for outdated rules
   - Verify `.agent/knowledge/tech-stack.md` matches actual dependencies
   - Ensure `PROJECT_IDENTITY.md` is current
   - Look for undocumented patterns or decisions
   - Identify knowledge gaps that slow down agents

10. **Report**: Summarize findings:
   - Total issues found by category
   - Critical issues requiring immediate attention
   - Workflow improvements needed
   - Knowledge base gaps
   - Recommendations for next sprint

## Output Format

Add issues to `ISSUES.md` under a new or existing "Technical Debt" module:

```markdown
## Module: Technical Debt 🔧

- [ ] **[CRITICAL] Missing Error Handling in Prospecting Node**
  - **Status**: Pending
  - **Location**: `src/agents/prospecting.ts:40-45`
  - **Issue**: No try/catch around webSearch call, will crash on API failure
  - **Fix**: Wrap in try/catch and return empty leads array on error

- [ ] **[HIGH] Hardcoded API Timeout in Google Search**
  - **Status**: Pending
  - **Location**: `src/tools/google-search.ts:30`
  - **Issue**: 10s timeout is hardcoded, should be configurable
  - **Fix**: Add GOOGLE_SEARCH_TIMEOUT_MS env var with default
```

## When to Run This Workflow

- After completing a major module
- Before deploying to production
- When experiencing unexplained errors
- Monthly as part of maintenance
- When onboarding a new developer

## Example Usage

```
User: "Run a system audit"
Agent: [Executes this workflow and generates issues]
```
