#!/usr/bin/env python3
"""Check a video folder for missing, malformed, or unfinished stage files.

    python3 tools/validate.py                       # every video
    python3 tools/validate.py videos/2026-08-18-foo # one video

Reports facts about the files. It does not judge whether the content is good, and
it cannot check anything about YouTube policy -- that is on you.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline import (  # noqa: E402
    REPO_ROOT, STAGES, inspect, is_placeholder, read_json, rel, video_dirs,
)

# Fields that must not be null once a stage file is genuinely filled in.
REQUIRED = {
    "topic.json": ["slug", "working_title", "one_line_premise", "chosen_angle"],
    "research.json": ["slug", "key_facts"],
    "voice.json": ["slug", "direction"],
    "visuals.json": ["slug", "scenes"],
    "thumbnail.json": ["slug", "concepts"],
    "upload.json": ["slug", "titles", "description"],
}


def check_video(video_dir: Path) -> tuple[list, list, dict]:
    errors, warnings = [], []
    info = inspect(video_dir)

    for _, filename in STAGES:
        path = video_dir / filename
        if not path.exists():
            continue
        if is_placeholder(path):
            warnings.append(f"{filename}: still an untouched template (not counted as done)")
            continue
        if filename.endswith(".json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                errors.append(f"{filename}: not valid JSON — {exc}")
                continue
            for field in REQUIRED.get(filename, []):
                value = data.get(field)
                if value in (None, "", [], {}):
                    warnings.append(f"{filename}: '{field}' is empty")

    # Cross-file consistency and the rules that actually matter.
    research = read_json(video_dir / "research.json")
    if research:
        facts = research.get("key_facts") or []
        unverified = [f.get("id") for f in facts
                      if isinstance(f, dict) and f.get("verified") is not True]
        if unverified:
            warnings.append(
                f"research.json: {len(unverified)} unverified fact(s) "
                f"({', '.join(str(i) for i in unverified if i)}) — each must be labeled "
                "as unverified in the script or cut")
        for fact in facts:
            if isinstance(fact, dict) and fact.get("claim") and not fact.get("source_url"):
                errors.append(f"research.json: fact {fact.get('id')} has a claim but no source_url")

    upload = read_json(video_dir / "upload.json")
    if upload:
        chapters = upload.get("chapters") or []
        if chapters:
            first = chapters[0].get("timestamp") if isinstance(chapters[0], dict) else None
            if first != "0:00":
                errors.append("upload.json: chapters must start at 0:00")
        if upload.get("published") is True and not upload.get("video_url"):
            warnings.append("upload.json: marked published but video_url is empty")
        if upload.get("ready_for_review") is True and not upload.get("recommended_title"):
            warnings.append("upload.json: ready_for_review is true but no recommended_title")
        if upload.get("pre_publish_checklist_completed") is not True:
            warnings.append("upload.json: pre-publish checklist not completed "
                            "(only you can complete it — checklists/pre-publish.md)")

    thumb = read_json(video_dir / "thumbnail.json")
    if thumb:
        concepts = thumb.get("concepts") or []
        filled = [c for c in concepts if isinstance(c, dict) and c.get("idea")]
        if filled and len(filled) < 10:
            warnings.append(f"thumbnail.json: {len(filled)} concepts filled in, expected 10")

    return errors, warnings, info


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate video stage files.")
    ap.add_argument("path", nargs="?", help="a video folder (default: all of them)")
    args = ap.parse_args()

    if args.path:
        target = Path(args.path)
        if not target.is_absolute():
            target = REPO_ROOT / target
        if not target.is_dir():
            print(f"error: not a directory: {args.path}")
            return 1
        targets = [target]
    else:
        targets = video_dirs()

    if not targets:
        print("\n  No videos to validate yet.\n")
        return 0

    total_errors = 0
    for video_dir in targets:
        errors, warnings, info = check_video(video_dir)
        total_errors += len(errors)
        print(f"\n  {video_dir.name}  —  {info['status']} "
              f"({info['stages_done']}/{info['stages_total']} stages)")
        if not errors and not warnings:
            print("    ok")
        for e in errors:
            print(f"    ERROR    {e}")
        for w in warnings:
            print(f"    warning  {w}")
        if info["next_agent"]:
            print(f"    next     {info['next_agent']} → {info['next_file']}")

    print("\n  Reminder: this checks file structure only. It cannot verify facts, "
          "licenses,\n  or whether your video complies with current YouTube policy.\n")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
