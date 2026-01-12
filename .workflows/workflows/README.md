# Workflow Documentation

This directory contains reusable workflows that guide Antigravity agents through complex, multi-step processes. Each workflow is a markdown file with YAML frontmatter defining its purpose.

## Available Workflows

### 1. `/onboard-agent` - Agent Onboarding
**Purpose**: Onboard new agents or developers to the project.

**When to Use**:
- Before making your first contribution
- Before using `/develop-agent` workflow
- After being away from the project for >1 week
- After major project structure changes

**Output**: Complete understanding of project structure, conventions, and current state.

**Example**:
```
User: "Onboard me to this project"
Agent: [Reads all key docs, verifies build, confirms understanding]
```

---

### 2. `/audit-system` - System Audit
**Purpose**: Analyze the codebase for flaws, gaps, and technical debt.

**When to Use**:
- After completing 5+ issues (automatic trigger)
- After completing a major module
- Before deploying to production
- When experiencing unexplained errors
- Monthly as part of maintenance

**Output**: Generates issues in `ISSUES.md` under "Technical Debt" module with severity ratings and specific fixes. Creates `AUDIT_REPORT.md` and `WORKFLOW_AUDIT.md`.

**Example**:
```
User: "Run a system audit"
Agent: [Scans codebase, generates 5 new technical debt issues]
```

---

### 3. `/execute-issue` - Issue Execution
**Purpose**: Standard process for implementing a single issue from `ISSUES.md`.

**When to Use**:
- Every time you start work on a new issue
- Ensures consistency across all development tasks

**Steps**:
1. Understand the task
2. Check architecture
3. Draft solution
4. Implement changes
5. Execute & verify
6. Run quality checks
7. Document changes
8. Report to user
9. Check for module completion
10. Optimize standards

**Example**:
```
User: "Implement the next issue"
Agent: [Follows this workflow step-by-step]
```

---

### 4. `/develop-agent` - Tier 2 Agent Development
**Purpose**: Create new LangGraph agents following the project's architecture.

**When to Use**:
- Building a new autonomous agent (e.g., "Content Agent", "Analytics Agent")
- Extending the system with new capabilities

**Output**: Complete agent implementation with state, nodes, graph, tests, and documentation.

**Example**:
```
User: "Create a new Content Agent that writes blog posts"
Agent: [Follows this workflow to scaffold the agent]
```

---

### 5. `/trigger-deployment` - Trigger GitHub Actions Deployment
**Purpose**: Trigger the deployment pipeline by creating an empty commit and pushing to main.

**When to Use**:
- After updating GitHub secrets (API keys, tokens, etc.)
- To redeploy without code changes
- When environment variables need to be picked up

**Output**: Empty commit pushed to main, triggering GitHub Actions deployment.

**Example**:
```
User: "Trigger deployment after updating secrets"
Agent: [Creates empty commit and pushes to trigger deployment]
```

---

### 6. `/debug-system` - System Debugging
**Purpose**: Diagnose and fix errors using Server Logs and Langfuse Traces.

**When to Use**:
- When the UI shows an error
- When a run fails
- When behavior is unexpected

**Steps**:
1. Check Server Logs
2. Inspect Langfuse Trace
3. Reproduce Issue
4. Fix & Verify

**Example**:
```
User: "The agent failed to send an email"
Agent: [Runs debug workflow, checks Langfuse, finds invalid API key error]
```

---

### 7. `/generate-tests` - Test Generation & Coverage
**Purpose**: Generate comprehensive test coverage for LangGraph agents, tools, and async pipelines.

**When to Use**:
- Before production deploy (ensure critical paths are tested)
- After major refactor (verify nothing broke)
- When adding new agent (generate tests alongside implementation)
- Monthly maintenance (expand coverage incrementally)
- After bug discovery (add regression tests)

**Test Types**:
- **Unit Tests**: Pure functions, tools, utilities (<100ms)
- **Integration Tests**: LangGraph nodes, agent logic (<5s)
- **Async Pipeline Tests**: Cloud Tasks handlers, processors (<10s)
- **E2E Tests**: Full workflow execution (<60s)

**Key Features**:
- **Cost-Aware**: Uses API mocking to avoid burning GCP credits
- **Tiered Execution**: Fast tests on every commit, slow tests on merge
- **CI/CD Integration**: Automated testing in GitHub Actions
- **Langfuse Integration**: Tests produce traceable metrics

**Output**: Test files, coverage reports, CI configuration, test utilities

**Example**:
```
User: "Generate tests for the prospecting agent"
Agent: [Creates unit, integration, and pipeline tests with >90% coverage]
```

---

## How Workflows Work

### Structure
Each workflow file has:
1. **YAML Frontmatter**: `description` field for quick reference
2. **Markdown Content**: Step-by-step instructions
3. **Turbo Annotations**: `// turbo` or `// turbo-all` for auto-execution

### Turbo Mode
- `// turbo`: Auto-run the next command step only
- `// turbo-all`: Auto-run ALL command steps in the workflow

### Invoking a Workflow
Agents can invoke workflows by:
1. Reading the workflow file with `view_file`
2. Following the steps sequentially
3. Reporting progress to the user

Users can invoke workflows with slash commands:
```
/audit-system
/execute-issue
/develop-agent
```

## Creating New Workflows

When creating a new workflow:

1. **Name it clearly**: Use kebab-case (e.g., `deploy-to-production.md`)
2. **Add frontmatter**:
   ```yaml
   ---
   description: Brief one-line description
   ---
   ```
3. **Structure it**:
   - Clear numbered steps
   - Specific, actionable instructions
   - Expected outputs
   - When to use it
4. **Document it**: Add an entry to this README
5. **Test it**: Run through the workflow manually to verify

## Best Practices

- **One Workflow = One Purpose**: Don't combine unrelated tasks
- **Be Specific**: Avoid vague instructions like "check the code"
- **Include Examples**: Show what success looks like
- **Update Regularly**: Workflows should evolve with the project
- **Use Turbo Wisely**: Only auto-run safe, non-destructive commands

## Workflow Lifecycle

1. **Creation**: Agent or user creates a new workflow
2. **Documentation**: Added to this README
3. **Usage**: Invoked via slash command or direct reference
4. **Refinement**: Updated based on execution feedback
5. **Archival**: Moved to `.agent/workflows/archive/` if obsolete
