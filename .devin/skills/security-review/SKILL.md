---
name: security-review
description: Review the current diff for security issues (OWASP Top 10) before merging. Use for any change touching APIs, auth, or user input.
---

## Steps

1. Read the full diff against the base branch.
2. Check every API route for: missing auth checks, IDOR (object access without ownership check), and unvalidated user input.
3. Search the diff for hardcoded secrets, tokens, or passwords.
4. Check that user-provided content is never rendered without escaping (XSS).
5. Check error handling: internal errors must not leak stack traces or internal data to the client.
6. Write a short report: issue, file:line, severity (high/medium/low), and suggested fix.
7. If any high severity issue exists, fix it before opening the PR.
