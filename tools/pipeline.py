"""Shared pipeline definitions for the faceless YouTube system.

Standard library only. No network. No side effects on import.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = REPO_ROOT / "videos"
TEMPLATE_DIR = VIDEOS_DIR / "_template"

# (status label, file that proves the stage is done)
STAGES = [
    ("Idea", "topic.json"),
    ("Research", "research.json"),
    ("Script", "script.md"),
    ("Voice", "voice.json"),
    ("Visuals", "visuals.json"),
    ("Thumbnail", "thumbnail.json"),
    ("Ready to Upload", "upload.json"),
]

# Full board, including the terminal state only the owner can set.
ALL_STATUSES = [name for name, _ in STAGES] + ["Published"]

AGENT_FOR_FILE = {
    "topic.json": "trend-research",
    "research.json": "trend-research",
    "script.md": "script-writing",
    "voice.json": "voice-production",
    "visuals.json": "visual-planning",
    "thumbnail.json": "thumbnail-creation",
    "upload.json": "upload-preparation",
    "analytics.json": "analytics-review",
}


def read_json(path: Path):
    """Return parsed JSON, or None if missing/unreadable. Never raises."""
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def is_placeholder(path: Path) -> bool:
    """True if the file is byte-identical to its template (scaffolded, not filled in)."""
    template = TEMPLATE_DIR / path.name
    if not template.exists() or not path.exists():
        return False
    try:
        return path.read_bytes() == template.read_bytes()
    except OSError:
        return False


def video_dirs():
    """Every video folder, sorted. Folders starting with '_' or '.' are ignored."""
    if not VIDEOS_DIR.is_dir():
        return []
    return sorted(
        d for d in VIDEOS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(("_", "."))
    )


def inspect(video_dir: Path) -> dict:
    """Derive a video's status purely from files on disk.

    Status rules (see CLAUDE.md section 2):
      - a stage counts as done when its file exists AND is not an untouched template
      - "Ready to Upload" additionally requires upload.json ready_for_review == true
      - "Published" requires upload.json published == true, which only the owner sets
    """
    present = {}
    for _, filename in STAGES:
        path = video_dir / filename
        present[filename] = path.exists() and not is_placeholder(path)

    upload = read_json(video_dir / "upload.json") or {}
    ready_for_review = upload.get("ready_for_review") is True
    published = upload.get("published") is True

    if present.get("upload.json") and not ready_for_review:
        present["upload.json"] = False

    status = None
    for label, filename in STAGES:
        if present[filename]:
            status = label
        else:
            break
    if published:
        status = "Published"
    if status is None:
        status = "Idea" if (video_dir / "topic.json").exists() else "Empty"

    # Next stage = first incomplete stage, unless already published.
    next_file = None
    if status != "Published":
        for _, filename in STAGES:
            if not present[filename]:
                next_file = filename
                break

    done = sum(1 for _, f in STAGES if present[f])
    return {
        "slug": video_dir.name,
        "path": video_dir,
        "status": status,
        "present": present,
        "published": published,
        "ready_for_review": ready_for_review,
        "stages_done": done,
        "stages_total": len(STAGES),
        "next_file": next_file,
        "next_agent": AGENT_FOR_FILE.get(next_file) if next_file else None,
        "has_analytics": (video_dir / "analytics.json").exists()
        and not is_placeholder(video_dir / "analytics.json"),
        "title": (read_json(video_dir / "topic.json") or {}).get("working_title"),
    }


def env_has_forbidden_keys(env_path: Path) -> list:
    """Flag credential names in .env that this system must not hold.

    Upload/publish/payment credentials are out of scope by design (CLAUDE.md section 0).
    Only key NAMES are inspected -- values are never read or printed.
    """
    forbidden_markers = [
        "OAUTH", "REFRESH_TOKEN", "CLIENT_SECRET", "UPLOAD",
        "STRIPE", "PAYPAL", "BILLING", "CARD", "PAYMENT",
    ]
    findings = []
    if not env_path.exists():
        return findings
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return findings
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name = line.split("=", 1)[0].strip().upper()
        for marker in forbidden_markers:
            if marker in name:
                findings.append(name)
                break
    return findings


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


__all__ = [
    "REPO_ROOT", "VIDEOS_DIR", "TEMPLATE_DIR", "STAGES", "ALL_STATUSES",
    "AGENT_FOR_FILE", "read_json", "is_placeholder", "video_dirs", "inspect",
    "env_has_forbidden_keys", "rel",
]
