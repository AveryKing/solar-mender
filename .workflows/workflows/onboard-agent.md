---
description: Onboard a new agent to the project
---
# Agent Onboarding Workflow

This workflow ensures new Antigravity agents (or human developers) understand the project structure, conventions, and current state before making contributions.

**Run this workflow**: Before using `/develop-agent` or making your first contribution.

---

## Execution Steps

// turbo-all

1. **Read Project Identity**:
   - Open `PROJECT_IDENTITY.md` to understand:
     - Active environment variables
     - Key constraints and focus
     - Current automation status
   - Verify you understand the project's core mission

2. **Review Current Status**:
   - Open `STATUS.md` to see:
     - Current objective
     - Completed modules
     - Active module and next priorities
     - Recent test results
   - Note the current system health score

3. **Study Architecture Decisions**:
   - Read `.agent/knowledge/decisions.md` to understand:
     - Why LangGraph was chosen
     - Why Gemini 2.0 Flash is the primary LLM
     - Why Supabase, Trigger.dev, and Resend were selected
     - Trade-offs and consequences of each decision
   - This prevents re-litigating settled decisions

4. **Learn the Tech Stack**:
   - Read `.agent/knowledge/tech-stack.md` to understand:
     - Core backend technologies
     - Available tools and their interfaces
     - Environment variable requirements
   - Review `package.json` to see current dependencies

5. **Understand Coding Standards**:
   - Read `.agent/knowledge/coding-standards.md` to learn:
     - Core principles (RTFM, Verification-through-Execution, etc.)
     - TypeScript standards
     - Testing requirements
     - Module completion responsibilities
   - These are non-negotiable rules

6. **Explore Available Workflows**:
   - Read `.agent/workflows/README.md` to discover:
     - Available workflows and when to use them
     - How to invoke workflows
     - Turbo mode explanation
   - Familiarize yourself with `/audit-system`, `/execute-issue`, `/develop-agent`

7. **Review Agent Handbook**:
   - Read `AGENT_HANDBOOK.md` to understand:
     - Your role as "The Antigravity IDE"
     - How to pick up work from `ISSUES.md`
     - Key commands and file references
     - Agent responsibilities

8. **Check Current Issues**:
   - Open `ISSUES.md` to see:
     - Completed modules (marked with ✅)
     - Active module (marked with 🚧)
     - Pending issues (marked with `[ ]`)
   - Identify where you can contribute

9. **Run a Test Build**:
   - Execute `npm run build` to verify the codebase compiles
   - Execute `npm test` to verify tests pass
   - This ensures your environment is set up correctly

10. **Review Recent Audit Reports**:
    - Read `AUDIT_REPORT.md` to see recent code quality findings
    - Read `WORKFLOW_AUDIT.md` to see workflow health
    - Understand current technical debt and improvement areas

11. **Understand the System Architecture**:
    - Review `src/graph.ts` to see the master orchestration
    - Review `src/types/index.ts` to understand core data structures
    - Review `src/agents/` to see existing agent implementations

12. **Confirm Onboarding Complete**:
    - You should now understand:
      - ✅ Project mission and current status
      - ✅ Why key technical decisions were made
      - ✅ Coding standards and workflows
      - ✅ How to pick up and execute issues
      - ✅ Current system architecture
    - You are ready to contribute!

---

## Onboarding Checklist

Use this checklist to verify you've completed onboarding:

- [ ] Read `PROJECT_IDENTITY.md`
- [ ] Read `STATUS.md`
- [ ] Read `.agent/knowledge/decisions.md`
- [ ] Read `.agent/knowledge/tech-stack.md`
- [ ] Read `.agent/knowledge/coding-standards.md`
- [ ] Read `.agent/workflows/README.md`
- [ ] Read `AGENT_HANDBOOK.md`
- [ ] Reviewed `ISSUES.md`
- [ ] Successfully ran `npm run build`
- [ ] Successfully ran `npm test`
- [ ] Read `AUDIT_REPORT.md` and `WORKFLOW_AUDIT.md`
- [ ] Reviewed `src/graph.ts` and `src/types/index.ts`

---

## What to Do After Onboarding

1. **Pick an Issue**: Choose a `[ ]` issue from `ISSUES.md` in the active module
2. **Execute It**: Use `/execute-issue` workflow to implement it
3. **Document**: Update relevant docs as you work
4. **Test**: Verify your changes with tests
5. **Report**: Summarize what you did for the user

---

## For Human Developers

If you're a human developer (not an AI agent):

1. **Clone the repo**: `git clone <repo-url>`
2. **Install dependencies**: `npm install`
3. **Copy environment variables**: Create `.env` from `.env.example` (if it exists)
4. **Set up Supabase**: Follow instructions in `USER_ACTIONS.md`
5. **Run the onboarding workflow**: Follow steps 1-12 above
6. **Make your first contribution**: Pick an issue and use `/execute-issue`

---

## Frequency

- **New agents**: Run this workflow once before first contribution
- **Returning agents**: Re-run if you've been away for >1 week
- **After major changes**: Re-run if project structure or tech stack changes significantly
