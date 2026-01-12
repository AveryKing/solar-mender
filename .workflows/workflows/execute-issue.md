---
description: Execute a specific development issue
---
# Issue Execution Workflow

// turbo-all
1. **Understand**: Analyze the task against the current `PROJECT_IDENTITY.md`.
2. **Architecture Check**: Consult `.agent/knowledge/tech-stack.md`.
3. **Draft**: Propose the solution path in a temporary file if complex.
4. **Implement**: Apply changes using the prescribed rules.
5. **Execution Check**: Run the code/script. If it fails, fix the code and repeat until it passes.
6. **Quality**: Run a lint or type check command.
7. **Document**: Update relevant docs:
   - If you modified an agent: Update `docs/agents/[agent-name].md`
   - If you modified a tool: Update `docs/tools/[tool-name].md`
   - If you made an architectural decision: Add to `.agent/knowledge/decisions.md`
   - If you changed dependencies: Update `.agent/knowledge/tech-stack.md`
8. **Report**: Summarize the "Before vs After" for the USER.
9. **Module Completion Check**: If this was the last issue in a module:
   - Mark the module as "✅ COMPLETED" in `ISSUES.md`
   - Generate the next logical module with 3-5 issues
   - Update `PROJECT_IDENTITY.md` if new capabilities were added
10. **Periodic Audit**: If 5+ issues have been completed since last audit:
    - Run `/audit-system` workflow
    - Address any CRITICAL issues immediately
11. **Optimize**: Audit this issue for repeatable patterns and update Meta-Standards.
