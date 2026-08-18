#!/usr/bin/env python3
"""Status dashboard for the faceless YouTube pipeline.

    python3 tools/dashboard.py            # print the board
    python3 tools/dashboard.py --write    # also write dashboard.md and dashboard.html

Status is derived from files on disk only. Nothing here uploads, publishes, or
contacts any service -- it reads the videos/ folder and prints what it finds.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import (  # noqa: E402
    ALL_STATUSES, REPO_ROOT, STAGES, env_has_forbidden_keys, inspect, rel, video_dirs,
)

DONE, TODO = "●", "○"

POLICY_NOTE = (
    "YouTube policies, copyright rules, monetization requirements, and AI-content "
    "disclosure rules change and vary by country. Check the official sources before "
    "publishing. Nothing here is legal advice."
)


def collect():
    return [inspect(d) for d in video_dirs()]


def progress_bar(row) -> str:
    if row["status"] == "Published":
        return DONE * len(STAGES) + " ✓"
    return "".join(DONE if row["present"][f] else TODO for _, f in STAGES)


def print_board(rows) -> None:
    width = 78
    print()
    print("=" * width)
    print("  FACELESS YOUTUBE PIPELINE — STATUS BOARD")
    print(f"  {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * width)

    if not rows:
        print("\n  No videos yet.")
        print('  Start one:  python3 tools/new_video.py "your topic here"\n')
    else:
        legend = "  " + " → ".join(name for name, _ in STAGES) + " → Published"
        print(legend)
        print("-" * width)
        for row in rows:
            title = row["title"] or row["slug"]
            print(f"\n  {title}")
            print(f"    {row['slug']}")
            print(f"    [{progress_bar(row)}]  {row['status']}"
                  f"  ({row['stages_done']}/{row['stages_total']} files)")
            if row["status"] == "Published":
                print("    published — set by the owner")
                if not row["has_analytics"]:
                    print("    next: analytics-review (needs numbers you supply)")
            elif row["next_agent"]:
                print(f"    next: {row['next_agent']} → writes {row['next_file']}")
        print()

    print("-" * width)
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in ALL_STATUSES}
    print("  " + "   ".join(f"{s}: {n}" for s, n in counts.items() if n))
    print("-" * width)

    findings = env_has_forbidden_keys(REPO_ROOT / ".env")
    if findings:
        print("\n  ⚠  .env contains credential names that are out of scope for this")
        print("     system (upload/publish/payment). Review these yourself:")
        for name in findings:
            print(f"       - {name}")
        print("     (Names only were checked. No values were read.)")

    print(f"\n  Reminder: {POLICY_NOTE}")
    print("  Nothing in this system uploads, publishes, posts, or spends money.\n")


def render_markdown(rows) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    out = [
        "# Video Dashboard",
        "",
        f"_Generated {now} by `tools/dashboard.py`. Status is derived from files on disk._",
        "",
        "`Idea → Research → Script → Voice → Visuals → Thumbnail → Ready to Upload → Published`",
        "",
    ]
    if not rows:
        out += ["No videos yet. Start one:", "",
                '```bash', 'python3 tools/new_video.py "your topic here"', '```', ""]
    else:
        header = "| Video | " + " | ".join(n for n, _ in STAGES) + " | Status | Next |"
        out.append(header)
        out.append("|---" * (len(STAGES) + 3) + "|")
        for row in rows:
            cells = [DONE if row["present"][f] else TODO for _, f in STAGES]
            if row["status"] == "Published":
                cells = [DONE] * len(STAGES)
            nxt = "— (published)" if row["status"] == "Published" else (
                f"`{row['next_agent']}` → `{row['next_file']}`" if row["next_agent"] else "—")
            title = row["title"] or row["slug"]
            out.append(f"| **{title}**<br>`{row['slug']}` | " + " | ".join(cells)
                       + f" | {row['status']} | {nxt} |")
        out.append("")
        counts = {s: sum(1 for r in rows if r["status"] == s) for s in ALL_STATUSES}
        out.append("**Totals:** " + " · ".join(f"{s} {n}" for s, n in counts.items() if n))
        out.append("")

    out += [
        "---",
        "",
        "### Rules this board reflects",
        "",
        "- **Ready to Upload** means the draft material is ready for *your* review — not that anything is going live.",
        "- **Published** is set by you, by hand, in `upload.json`, after you upload the video yourself.",
        "- No agent uploads, publishes, posts, schedules, or spends money.",
        "",
        f"> {POLICY_NOTE}",
        "",
    ]
    return "\n".join(out)


def render_html(rows) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    stage_names = [n for n, _ in STAGES]

    body = []
    if not rows:
        body.append('<p class="empty">No videos yet. Run '
                    '<code>python3 tools/new_video.py "your topic"</code> to start one.</p>')
    else:
        for row in rows:
            title = html.escape(row["title"] or row["slug"])
            slug = html.escape(row["slug"])
            status = html.escape(row["status"])
            cls = "published" if row["status"] == "Published" else "active"
            steps = []
            for name, filename in STAGES:
                done = row["present"][filename] or row["status"] == "Published"
                steps.append(
                    f'<li class="{"done" if done else "todo"}">'
                    f'<span class="dot"></span><span class="lbl">{html.escape(name)}</span></li>'
                )
            done_step = ('<li class="done"><span class="dot"></span>'
                         '<span class="lbl">Published</span></li>'
                         if row["status"] == "Published"
                         else '<li class="todo"><span class="dot"></span>'
                              '<span class="lbl">Published</span></li>')
            steps.append(done_step)
            if row["status"] == "Published":
                nxt = ("Analytics review pending — supply your numbers"
                       if not row["has_analytics"] else "Analytics reviewed")
            elif row["next_agent"]:
                nxt = f"Next: <code>{html.escape(row['next_agent'])}</code> → writes <code>{html.escape(row['next_file'])}</code>"
            else:
                nxt = "—"
            body.append(f"""<article class="card {cls}">
  <header><h2>{title}</h2><span class="badge">{status}</span></header>
  <p class="slug">{slug}</p>
  <ol class="steps">{''.join(steps)}</ol>
  <p class="next">{nxt}</p>
</article>""")

    counts = {s: sum(1 for r in rows if r["status"] == s) for s in ALL_STATUSES}
    totals = "".join(
        f'<span class="pill">{html.escape(s)} <b>{n}</b></span>'
        for s, n in counts.items() if n
    ) or '<span class="pill">no videos yet</span>'

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Video Dashboard</title>
<style>
  :root {{
    --bg:#f7f7f8; --card:#fff; --ink:#1b1b1f; --muted:#6b6b76;
    --line:#e3e3e8; --done:#2f7d4f; --todo:#c9c9d1; --accent:#3b5bdb;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#131316; --card:#1c1c20; --ink:#ececed; --muted:#9a9aa5;
             --line:#2c2c33; --done:#4caf7d; --todo:#3a3a44; --accent:#7d95f0; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:2rem 1rem 3rem; background:var(--bg); color:var(--ink);
         font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
  .wrap {{ max-width:920px; margin:0 auto; }}
  h1 {{ font-size:1.5rem; margin:0 0 .25rem; }}
  .meta {{ color:var(--muted); font-size:.85rem; margin:0 0 1.25rem; }}
  .flow {{ font-size:.8rem; color:var(--muted); margin-bottom:1.5rem; }}
  .totals {{ display:flex; flex-wrap:wrap; gap:.5rem; margin-bottom:1.5rem; }}
  .pill {{ background:var(--card); border:1px solid var(--line); border-radius:999px;
           padding:.25rem .7rem; font-size:.8rem; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
           padding:1.1rem 1.2rem; margin-bottom:1rem; }}
  .card.published {{ border-color:var(--done); }}
  .card header {{ display:flex; align-items:center; justify-content:space-between; gap:1rem; }}
  .card h2 {{ font-size:1.05rem; margin:0; }}
  .badge {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.06em;
            color:var(--muted); border:1px solid var(--line); border-radius:6px;
            padding:.15rem .5rem; white-space:nowrap; }}
  .slug {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.75rem;
           color:var(--muted); margin:.3rem 0 .9rem; word-break:break-all; }}
  .steps {{ list-style:none; display:flex; flex-wrap:wrap; gap:.15rem 0; padding:0; margin:0 0 .85rem; }}
  .steps li {{ position:relative; flex:1 1 90px; min-width:80px; text-align:center;
               padding-top:1.1rem; font-size:.68rem; color:var(--muted); }}
  .steps li::before {{ content:""; position:absolute; top:.42rem; left:0; right:50%;
                       height:2px; background:var(--todo); }}
  .steps li::after {{ content:""; position:absolute; top:.42rem; left:50%; right:0;
                      height:2px; background:var(--todo); }}
  .steps li:first-child::before, .steps li:last-child::after {{ background:transparent; }}
  .steps li.done::before, .steps li.done::after {{ background:var(--done); }}
  .steps li.done + li.todo::before {{ background:var(--done); }}
  .dot {{ position:absolute; top:0; left:50%; transform:translateX(-50%);
          width:11px; height:11px; border-radius:50%; background:var(--todo); }}
  .steps li.done .dot {{ background:var(--done); }}
  .steps li.done {{ color:var(--ink); }}
  .lbl {{ display:block; }}
  .next {{ margin:0; font-size:.82rem; color:var(--muted); }}
  code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.9em;
          background:rgba(125,125,140,.14); padding:.1rem .3rem; border-radius:4px; }}
  .empty {{ color:var(--muted); }}
  .notice {{ margin-top:2rem; border-left:3px solid var(--accent); padding:.1rem 0 .1rem 1rem;
             font-size:.85rem; color:var(--muted); }}
  .notice b {{ color:var(--ink); }}
</style>
</head><body><div class="wrap">
<h1>Video Dashboard</h1>
<p class="meta">Generated {now} by <code>tools/dashboard.py</code> — status derived from files on disk.</p>
<p class="flow">{' → '.join(html.escape(s) for s in stage_names)} → Published</p>
<div class="totals">{totals}</div>
{''.join(body)}
<div class="notice">
<p><b>Ready to Upload</b> means the draft material is ready for <em>your</em> review — not that anything is going live.
<b>Published</b> is a field you set by hand in <code>upload.json</code> after you upload the video yourself.
No agent uploads, publishes, posts, schedules, or spends money.</p>
<p>{html.escape(POLICY_NOTE)}</p>
</div>
</div></body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Show the video pipeline status board.")
    ap.add_argument("--write", action="store_true",
                    help="write dashboard.md and dashboard.html")
    ap.add_argument("--quiet", action="store_true", help="suppress the console board")
    args = ap.parse_args()

    rows = collect()
    if not args.quiet:
        print_board(rows)

    if args.write:
        md = REPO_ROOT / "dashboard.md"
        page = REPO_ROOT / "dashboard.html"
        md.write_text(render_markdown(rows), encoding="utf-8")
        page.write_text(render_html(rows), encoding="utf-8")
        print(f"  wrote {rel(md)}")
        print(f"  wrote {rel(page)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
