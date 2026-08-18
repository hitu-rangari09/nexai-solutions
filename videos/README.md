# videos/ — the shared content database

One folder per video. The folder is the database. Each stage writes exactly one file,
and the next stage reads it. No hidden state.

## Naming

```
videos/YYYY-MM-DD-kebab-case-slug/
```

Folders starting with `_` (like `_template/`) are ignored by the dashboard.

## Flow

```
topic.json → research.json → script.md → voice.json → visuals.json → thumbnail.json → upload.json
                                                                                   ↘ analytics.json (after the owner publishes)
```

| File | Written by | Reads |
|------|-----------|-------|
| `topic.json` | trend-research | `channel.md` |
| `research.json` | trend-research | `topic.json` |
| `script.md` | script-writing | `research.json`, `topic.json`, `channel.md` |
| `voice.json` | voice-production | `script.md`, `channel.md` |
| `visuals.json` | visual-planning | `script.md`, `voice.json` |
| `thumbnail.json` | thumbnail-creation | `topic.json`, `script.md` |
| `upload.json` | upload-preparation | all of the above |
| `analytics.json` | analytics-review | `upload.json` + numbers the owner supplies |

## Rules

1. **Never skip a stage.** If the input file is missing, the agent stops and says which one.
2. **Never overwrite the owner's edits.** Read the existing file first; extend it, or ask.
3. **Provenance is mandatory.** `generated_at`, `generated_by`, and a source for every fact.
4. **`null` beats a guess.** Unknown fields stay `null`, and get listed in `open_questions`.
5. **No keys in these files, ever.** Keys live in `.env`.
6. **`published: true` is set by the owner only**, by hand, after they upload the video
   themselves. No agent uploads, publishes, schedules, or posts anything.

## Optional subfolders (gitignored — big binaries)

```
audio/     TTS exports
assets/    images, b-roll you downloaded
renders/   final cuts
```

These are ignored by git on purpose. Keep the license/permission proof for anything in
`assets/` recorded in `visuals.json` under `b_roll[].license`.
