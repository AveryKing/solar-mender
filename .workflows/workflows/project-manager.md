---
description: Project Manager workflow to keep docs, issues, and implementation plan in sync.
---

# Project Manager Workflow

Use this workflow to audit the project's progress, update the issue tracker, and ensure we are following the master implementation plan. This workflow should be run at the start of a session or after major architectural changes.

## 1. 🔍 System Reconnaissance
- Read `docs/setup/IMPLEMENTATION_PLAN.md` to identify the current target phase.
- Read `STATUS.md` for the latest high-level summary.
- Scan the `src/` directory and `package.json` to verify implemented features vs. planned ones.

## 2. 📝 ISSUES.md Synchronization
- **Audit Implementation**: Check if tasks marked as "PLANNED" have already been implemented (e.g., check for Vertex AI usage, parallelization, or HITL nodes).
- **Update Statuses**: 
  - Move completed tasks to `[x]`.
  - Update `Status: In Progress` for active work.
  - Add specific `Location` or `Result` notes for completed items.
- **Module Hygiene**: Ensure all major technical debt identified in `AUDIT_REPORT.md` is tracked in the `Technical Debt` module.

## 3. 📚 Documentation Audit
- Ensure all new tools in `src/tools/` have corresponding files in `docs/tools/`.
- Ensure all agents in `src/agents/` have corresponding files in `docs/agents/`.
- Verify `README.md` reflects the current system capabilities (e.g., grounding, UI integration).

## 4. 🚀 Roadmap Alignment
- Identify the next technical milestone from the `IMPLEMENTATION_PLAN.md`.
- Create a new "Next Phase" module in `ISSUES.md` if necessary.
- Update `STATUS.md` to reflect the transition between phases (e.g., moving from Day 1 to Day 2).

## 5. 🛠️ Technical Debt Identification
- Search for `TODO`, `FIXME`, or `any` in the codebase.
- Add these as issues in the `Technical Debt` module of `ISSUES.md`.

## 6. ✅ Completion Criteria
- `ISSUES.md` accurately reflects the state of the codebase.
- `STATUS.md` is updated.
- Documentation for all core components exists.
- The next actionable task is clearly identified.
