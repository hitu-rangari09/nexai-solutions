---
description: Scaffold a new video folder and run the idea stage
---

Start a new video for the topic: **$ARGUMENTS**

1. Read `CLAUDE.md` and `channel.md`. If `channel.md` still has `<< TO FILL >>` in the
   niche or audience fields, stop and ask the owner to fill them in first.
2. Run `python3 tools/new_video.py "$ARGUMENTS"` to scaffold the folder.
3. Hand off to the **trend-research** agent in Mode A (Scan → Score → Shortlist) to
   fill in `topic.json`.
4. Show the shortlist and **stop**. The owner picks the angle before anything else runs.

Do not run later stages. Do not upload anything. Scores are prioritization aids, not
predictions.
