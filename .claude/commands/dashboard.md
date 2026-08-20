---
description: Regenerate and show the video status dashboard
---

Run `python3 tools/dashboard.py --write`, then summarize for the owner:

- each video's current status and what stage comes next
- anything blocked and what it's waiting on
- any video sitting at **Ready to Upload** that's waiting on their review

`dashboard.md` and `dashboard.html` are regenerated. Do not report anything about
expected performance, views, or revenue — this board tracks production status only.
