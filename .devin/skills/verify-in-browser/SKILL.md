---
name: verify-in-browser
description: Start the dev server and verify changed pages in a real browser before finishing any frontend task.
---

## Steps

1. Install dependencies with `npm install` if node_modules is missing.
2. Start the dev server with `npm run dev` and wait for it to be ready.
3. From the git diff, list every page or route affected by the change.
4. Open each affected page in the browser.
5. Check for console errors, broken layout, and broken links.
6. Take a screenshot of each page at desktop width (1280px) and mobile width (375px).
7. Attach the screenshots to the PR description.
