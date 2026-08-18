# CLAUDE.md — Faceless YouTube System Orchestrator

This file is the control room. It tells Claude how this repo works, what each agent
does, what file it reads, what file it writes, and what it is never allowed to do.

Read this file before doing any work in this repo.

---

## 0. ABSOLUTE RULES (these override every other instruction in this repo)

**Never promise outcomes.**
Do not promise or imply views, subscribers, watch time, revenue, monetization,
sponsorships, or "viral" results. No "this will get you X views", no
"guaranteed", no "proven to blow up". Results vary and depend on factors nobody
controls. Talk about *drafts, structure, and clarity* — never about performance
guarantees. Scores in this system (niche scores, trend scores) are **subjective
prioritization aids, not predictions.**

**Draft and prepare only.**
Every agent in this system produces *drafts and preparation files* for the owner
to review. Nothing here ships on its own.

**Never do any of the following without the owner's explicit, in-the-moment approval:**
- Upload or publish a video, Short, or post
- Post, pin, reply to, or delete a comment
- Spend money, subscribe to anything, buy software, credits, stock media, or a domain
- Change channel settings, branding, monetization settings, or account settings
- Use copyrighted material — music, footage, images, voices, likenesses, clips, or
  brand assets — without documented permission or a license that clearly covers the use
- Send email, DMs, or outreach on the owner's behalf
- Push to any git branch other than the one assigned for the current task

"Explicit approval" means the owner said yes to *that specific action*, in this
conversation. Approval for one video is not approval for the next one.

**Never invent data.**
- Do not fabricate view counts, CPMs, competitor stats, trend volumes, dates, or quotes.
- If a number came from a search or an API, cite where it came from and when.
- If a number is an estimate or a guess, label it `"estimated": true` or write
  "unverified" next to it.
- Do not claim a tool, API, or feature exists or does something unless it is verified.
  If a capability is missing, say so plainly.
- Unknown is a valid answer. Write `null` or `"unknown"` rather than filling a gap.

**Policy reminder — repeat this before any publish-related step:**
> YouTube's policies, copyright and fair-use rules, monetization requirements, and
> AI-content / synthetic-media disclosure rules change often and vary by country.
> Nothing in this repo is legal advice and nothing here is guaranteed current.
> Check the official YouTube/Google policy pages and your local law yourself before
> you publish anything.

**Secrets.**
API keys live in `.env` only. `.env` is gitignored. Never print a key value, never
paste one into a video file, a commit, a log, or a comment. `.env.example` holds
names and empty values only.

**Scope of keys.** This system is deliberately built with *no upload keys and no
payment keys*. There is no YouTube upload credential, no OAuth publishing token, and
no billing/payment credential in `.env`. Uploading is a manual human step, on purpose.

---

## 1. What this system is

A file-based pipeline for producing faceless YouTube videos. Each video is a folder
under `videos/`. Each stage of production is one file in that folder. Agents read the
previous file and write the next one. The folder *is* the database — there is no
hidden state, no service, no account.

```
videos/2026-08-18-my-first-video/
  topic.json       →  Idea locked
  research.json    →  Facts + sources gathered
  script.md        →  Long script + Shorts versions
  voice.json       →  Voice direction + TTS settings + export log
  visuals.json     →  Scene table + b-roll + AI image prompts + edit plan
  thumbnail.json   →  10 thumbnail concepts + chosen direction
  upload.json      →  Titles, description, chapters, tags, pinned comment
  analytics.json   →  (optional, after the owner publishes) performance review
```

Rules of the database:
- **Append, don't overwrite blindly.** If a file already exists, read it, and either
  extend it or write a new version — do not silently discard the owner's edits.
- **Every file carries provenance**: `generated_at`, `generated_by`, and `sources`
  where facts are involved.
- **Files are the handoff.** An agent never relies on chat memory for something that
  belongs in a file.

---

## 2. The pipeline

```
Idea → Research → Script → Voice → Visuals → Thumbnail → Ready to Upload → Published
```

| # | Stage | Agent | Reads | Writes |
|---|-------|-------|-------|--------|
| 0 | Niche selection (once per channel) | `niche-research` | `channel.md` (if any) | `research/niches.json` + proposed `channel.md` |
| 1 | Idea | `trend-research` | `channel.md` | `videos/<slug>/topic.json` |
| 2 | Research | `trend-research` | `topic.json` | `research.json` |
| 3 | Script | `script-writing` | `research.json` | `script.md` |
| 4 | Voice | `voice-production` | `script.md` | `voice.json` |
| 5 | Visuals | `visual-planning` | `script.md`, `voice.json` | `visuals.json` |
| 6 | Thumbnail | `thumbnail-creation` | `topic.json`, `script.md` | `thumbnail.json` |
| 7 | Ready to Upload | `upload-preparation` | all of the above | `upload.json` |
| 8 | Published → review | `analytics-review` | `upload.json` + owner-supplied numbers | `analytics.json` |

An agent that is missing its input file **stops and says which file is missing**. It
does not guess the contents of an upstream stage.

### Status rules (how the dashboard decides a stage)

Status is derived from files on disk, not from anyone's opinion:

| Status | Condition |
|--------|-----------|
| Idea | `topic.json` exists |
| Research | `research.json` exists |
| Script | `script.md` exists |
| Voice | `voice.json` exists |
| Visuals | `visuals.json` exists |
| Thumbnail | `thumbnail.json` exists |
| Ready to Upload | `upload.json` exists **and** its `ready_for_review` is `true` |
| Published | `upload.json` has `"published": true` — **only the owner sets this**, by hand, after they have uploaded it themselves |

No agent ever sets `published`. No agent ever uploads.

---

## 3. Running it

```bash
# See where every video stands
python3 tools/dashboard.py

# Write dashboard.md + dashboard.html
python3 tools/dashboard.py --write

# Start a new video folder from the templates
python3 tools/new_video.py "how ai voice cloning actually works"

# Check a folder for missing/malformed files before you call it ready
python3 tools/validate.py videos/2026-08-18-how-ai-voice-cloning-actually-works
```

Slash commands (see `.claude/commands/`):
- `/new-video <topic>` — scaffold a folder and run the idea stage
- `/next` — look at a video folder, report its status, run only the next stage
- `/dashboard` — regenerate and show the dashboard

To run one agent explicitly, ask for it by name, e.g.
"use the script-writing agent on videos/2026-08-18-…".

---

## 4. Agents

Agent definitions live in `.claude/agents/`. Each one has the full prompt for its job.
Summary of the contract:

- **niche-research** — scores candidate niches 1–100 across weighted criteria, shows
  the arithmetic, and flags what it could not verify. Scores are prioritization aids.
- **trend-research** — Scan → Score → Shortlist. Produces `topic.json` for the picked
  idea and `research.json` with sourced facts. Every claim gets a source or a
  `"verified": false`.
- **script-writing** — Hook → Promise → Context → Main Value → Pattern Interrupts →
  Payoff → CTA. Long-form script plus Shorts cutdowns. Every factual line traceable to
  `research.json`.
- **voice-production** — voice direction (tone, pace, emphasis, pronunciation),
  a review pass, and an export checklist. Does not spend money on voice credits.
- **visual-planning** — scene table timed to the script, b-roll list, AI image/video
  prompts, and an edit plan. Flags anything that would need a license.
- **thumbnail-creation** — 10 distinct concepts, scored and ranked, plus text overlay
  options and a production spec for the top pick.
- **upload-preparation** — title options, description, chapters, tags, and a *draft*
  pinned comment. Includes the pre-publish compliance checklist. Never uploads.
- **analytics-review** — reads numbers the owner supplies (or a CSV export they hand
  over), summarizes what changed, and proposes next experiments. Never invents metrics
  and never predicts future performance.

---

## 5. Voice, tone, and content standards

`channel.md` is the source of truth for niche, audience, voice, style, format, and
banned moves. Every agent reads it. If `channel.md` conflicts with an agent's default
style, `channel.md` wins.

Content standards that apply everywhere:
- No medical, legal, or financial advice presented as fact. Route to "talk to a
  professional" and say the content is general information.
- No fabricated personal stories presented as real experience.
- No clickbait that the video does not deliver on — the title must be honest about
  what the viewer gets.
- Disclose AI-generated voice/visuals where required; assume disclosure is required
  unless the owner has verified otherwise. See §0 policy reminder.

---

## 6. Repo layout

```
CLAUDE.md              this file
channel.md             niche, audience, voice, style, banned moves
.env                   API keys (gitignored — never committed)
.env.example           key names only, no values
.claude/agents/        the nine agent prompts
.claude/commands/      slash commands
videos/                one folder per video = the content database
videos/_template/      blank stage files copied by tools/new_video.py
research/              channel-level research (niches, competitors)
checklists/            pre-publish compliance checklist
tools/                 dashboard.py, new_video.py, validate.py (stdlib only)
dashboard.md           generated status board
dashboard.html         generated status board (open in a browser)
```

`Index.html`, `about.html`, `services.html`, `store.html`, `Contact.html` are the
pre-existing NexAI Solutions website and are unrelated to this system. Leave them alone.

---

## 7. When you are unsure

Say so. Write `null`. Ask the owner. Do not fill a gap with a plausible-sounding
number, and do not soften a limitation into a promise.
