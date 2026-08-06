---
name: pre-pr-check
description: Quality gate to run before opening any PR. Runs lint, build, and tests, then self-reviews the diff.
---

## Steps

1. Run `npm run lint` and fix every error and warning it reports.
2. Run `npm run build` and confirm it completes with no errors.
3. Run `npm test` if the repo has tests; all must pass.
4. Read the full diff against the base branch (`git diff --merge-base origin/main`).
5. Self-review the diff for: leftover console.log or debug code, hardcoded secrets or URLs, missing error handling, and unused imports.
6. Only open the PR after all checks pass. List the checks you ran in the PR description.
