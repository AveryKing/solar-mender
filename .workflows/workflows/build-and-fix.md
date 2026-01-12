---
description: Run the project build command and automatically attempt to fix any TypeScript or compilation errors.
---

# Build & Fix Workflow

This workflow automates the "compile -> debug -> fix" loop.

## 1. Run Build
1. Execute the build command:
   ```bash
   npm run build
   ```

## 2. Analyze Output
If the build **PASSES** (Exit Code 0):
- 🎉 Report success and exit.

If the build **FAILS**:
1. Read the error log.
2. Identify the file path and line number of the error.
3. Determine the error type (e.g., TS2339 Property does not exist, TS2307 Module not found).

## 3. Apply Fixes
For each error found:

**Type A: Missing Property on Type**
- Check the Interface definition (usually in `src/types/`).
- Update the interface to include the missing property OR update the code to access the correct property name (e.g., `lead.company_name` instead of `lead.company`).

**Type B: Missing Module**
- Check `package.json`.
- If a package was removed (like `@google/generative-ai`), replace imports with the correct equivalent (e.g., `src/tools/vertex-ai.ts`).

**Type C: Method Mismatch**
- If `invoke()` doesn't exist on a class, switch to the native SDK method (e.g., `generateContent()`).

## 4. Verify
1. Run `npm run build` again.
2. If errors persist, repeat steps 2-3.
3. If fixed, commit the changes using the `/stealth-commit` strategy.
