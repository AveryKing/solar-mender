---
description: The standard process for developing Tier 2 Agents
---
# Tier 2 Agent Development Workflow

**PREREQUISITE**: You MUST complete `/onboard-agent` workflow before using this workflow.

This workflow guides you through creating a new LangGraph agent following the project's architecture patterns.

---

// turbo-all
1. **Sync**: 
   - Read `docs/setup/PROJECT_IDENTITY.md` and `docs/setup/IMPLEMENTATION_PLAN.md`.
   - **CRITICAL**: Verify `.agent/knowledge/tech-stack.md` matches the latest `docs/setup/IMPLEMENTATION_PLAN.md`. If not, update it IMMEDIATELY before writing code.
2. **Type-First**: If the new agent needs new state, update `src/types/index.ts`.
3. **Logic**: Create or update the agent file in `src/agents/`.
4. **Tool Check**: Ensure all tools used (e.g. search, db) are imported from `@/tools` and not redefined.
5. **Verify**: 
   - Run `npx tsc --noEmit` to check types.
   - Run `node list_models.js` or equivalent to verify AI connectivity.
6. **Documentation**: 
   - Create `docs/agents/[agent-name].md` documenting the agent's workflow
   - Update `.agent/knowledge/database-schema.md` if table usage changed.
   - Update `.agent/knowledge/decisions.md` if architectural decisions were made
7. **Optimize**: Check `.agent/rules/self-optimization.md` and log any friction in `.agent/knowledge/optimization-log.md`.
