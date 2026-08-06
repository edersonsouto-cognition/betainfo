---
name: add-api-endpoint
description: Create a new API endpoint following this repo's conventions. Use whenever adding a route under src/app/api.
---

## Steps

1. Create the route handler at `src/app/api/<resource>/route.ts`.
2. Validate the request body with a zod schema defined at the top of the file.
3. Return errors as `{ error: string }` with the correct HTTP status; never leak internal details.
4. Require auth on any endpoint that reads or writes user data.
5. Add a happy-path test and a validation-failure test for the new endpoint.
6. Run the pre-pr-check skill before opening the PR.
