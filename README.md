# nexai-solutions

AI Service Website- NexAI Solutions

## Faceless YouTube system

This repo also contains a file-based pipeline for producing faceless YouTube videos.
It **drafts and prepares only** — it never uploads, publishes, posts, or spends money.

- **[CLAUDE.md](CLAUDE.md)** — the orchestrator: rules, pipeline, agent contracts
- **[channel.md](channel.md)** — niche, audience, voice, style (fill this in first)
- **[videos/](videos/)** — one folder per video; the shared content database
- **[dashboard.md](dashboard.md)** — status board (`python3 tools/dashboard.py --write`)
- **[checklists/pre-publish.md](checklists/pre-publish.md)** — run before you upload

```bash
cp .env.example .env          # then add your AI / search / TTS keys
python3 tools/new_video.py "your topic"
python3 tools/dashboard.py
```

`.env` is gitignored and holds AI, search, and TTS keys only — no upload, publish, or
payment credentials, by design.

> YouTube policies, copyright rules, monetization requirements, and AI-content
> disclosure rules change and vary by country. Check the official sources before
> publishing. Nothing in this repo is legal advice.
