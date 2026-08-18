---
description: Run only the next pipeline stage for a video folder
---

Advance one stage for: **$ARGUMENTS** (a video folder path; if omitted, ask which one).

1. Run `python3 tools/dashboard.py` to see where things stand.
2. Run `python3 tools/validate.py $ARGUMENTS` and report any errors first.
3. Identify the next incomplete stage from the table in `CLAUDE.md` §2.
4. Invoke **only that stage's agent**. It reads the previous file and writes its own.
5. Report what was written, what's still `null`, and what the owner needs to decide.

Rules: one stage per invocation — do not run ahead. If the input file for the next
stage is missing, say which file is missing and stop. Never set `published`. Never
upload, post, or spend money. Before the upload-preparation stage, restate the policy
reminder from `CLAUDE.md` §0.
