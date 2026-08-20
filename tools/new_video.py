#!/usr/bin/env python3
"""Scaffold a new video folder from videos/_template/.

    python3 tools/new_video.py "how ai voice cloning actually works"
    python3 tools/new_video.py "..." --date 2026-09-01

Copies only topic.json by default -- the later stage files are written by their
agents, so an empty folder full of blank templates doesn't fake progress on the
dashboard. Use --all-stubs if you want every template copied up front.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import TEMPLATE_DIR, VIDEOS_DIR, rel  # noqa: E402

STUB_ORDER = [
    "topic.json", "research.json", "script.md", "voice.json",
    "visuals.json", "thumbnail.json", "upload.json",
]


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug[:60].strip("-")


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a new video folder.")
    ap.add_argument("topic", help="working title / topic, in quotes")
    ap.add_argument("--date", default=dt.date.today().isoformat(),
                    help="folder date prefix, YYYY-MM-DD (default: today)")
    ap.add_argument("--all-stubs", action="store_true",
                    help="copy every stage template, not just topic.json")
    args = ap.parse_args()

    slug = slugify(args.topic)
    if not slug:
        print("error: topic produced an empty slug — use some letters or numbers")
        return 1

    if not TEMPLATE_DIR.is_dir():
        print(f"error: template folder missing at {rel(TEMPLATE_DIR)}")
        return 1

    folder = VIDEOS_DIR / f"{args.date}-{slug}"
    if folder.exists():
        print(f"error: {rel(folder)} already exists — nothing was changed")
        return 1

    folder.mkdir(parents=True)
    files = STUB_ORDER if args.all_stubs else ["topic.json"]
    for name in files:
        src = TEMPLATE_DIR / name
        if src.exists():
            shutil.copy2(src, folder / name)

    # Seed the fields we actually know, so nothing downstream has to guess them.
    topic_path = folder / "topic.json"
    if topic_path.exists():
        try:
            data = json.loads(topic_path.read_text(encoding="utf-8"))
            data["slug"] = folder.name
            data["working_title"] = args.topic
            data["generated_at"] = dt.datetime.now().isoformat(timespec="seconds")
            data["generated_by"] = "new_video.py (scaffold — not yet researched)"
            topic_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except (OSError, ValueError) as exc:
            print(f"warning: could not seed topic.json ({exc}) — the file was still copied")

    print(f"\n  created {rel(folder)}")
    for name in files:
        if (folder / name).exists():
            print(f"    {name}")
    print("\n  Next: run the trend-research agent on this folder to fill in topic.json,")
    print("  then research.json. Nothing is researched, written, or uploaded yet.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
