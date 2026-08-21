#!/usr/bin/env python3
"""
luxun-skill quality gate.

Run 13 contract checks against the distilled SKILL.md and its supporting
artifacts. Mirrors the dot-skill celebrity research quality flow in a
standalone, stdlib-only form so the repo can be verified anywhere.

Exit code: 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
TIMESTAMP_RE = re.compile(r"\b\d{2}:\d{2}:\d{2}\b")
TECHNIQUE_WORDS = ("白描", "反讽", "排比", "比喻", "排比与反复", "文言白话", "白描")


def parse_frontmatter(raw: str) -> tuple[dict | None, str]:
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, raw
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, raw
    data: dict = {}
    for line in lines[1:end]:
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip().strip("\"'")
    body = "\n".join(lines[end + 1 :])
    return data, body


def section_text(body: str, heading: str) -> str:
    """Return text under the given '## heading' section (until the next '## ')."""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$.*?(?=^##\s|\Z)", body, re.M | re.S)
    return match.group(0) if match else ""


def grounded_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for url in URL_RE.findall(text):
        url = url.rstrip(".,)")
        path = url.split("://", 1)[-1].split("/", 1)[1] if "/" in url.split("://", 1)[-1] else ""
        segments = [s for s in path.split("/") if s]
        if len(segments) >= 2 or (segments and len(segments[0]) >= 8):
            urls.add(url)
    return urls


def copyright_safe(text: str) -> bool:
    if "```" in text:
        return False
    if re.search(r"^\s*>", text, re.M):
        return False
    if TIMESTAMP_RE.search(text):
        return False
    return True


def check_frontmatter(data: dict | None) -> tuple[bool, str]:
    if not data:
        return False, "frontmatter missing"
    errors: list[str] = []
    name = data.get("name", "")
    if not SKILL_NAME_RE.match(name):
        errors.append(f"invalid skill name: {name!r}")
    if not data.get("description"):
        errors.append("description missing")
    if not data.get("version"):
        errors.append("version missing")
    if data.get("user-invocable", "true").lower() != "true":
        errors.append("user-invocable must be true")
    if "disable-model-invocation" not in data:
        errors.append("disable-model-invocation missing (skill must not auto-activate)")
    return (not errors), "; ".join(errors) or "ok"


def check_hard_constraints(body: str) -> tuple[bool, str]:
    rules = section_text(body, "运行规则") + section_text(body, "运行约束")
    if not rules:
        return False, "运行规则 section missing"
    if "技法" not in rules or "永不" not in rules:
        return False, "技法隐形硬约束 missing in 运行规则"
    if "自我检讨" not in rules and "评论" not in rules:
        return False, "禁止写作自我检讨约束 missing"
    return True, "ok"


def check_persona_contracts(body: str) -> tuple[bool, str]:
    aliases = {
        "心智模型": ("心智模型", "Mental Models"),
        "表达 DNA": ("表达 DNA", "Expression DNA"),
        "诚实边界": ("诚实边界", "Honest Boundaries"),
        "矛盾": ("矛盾", "Contradiction"),
    }
    missing = [name for name, keys in aliases.items() if not any(k in body for k in keys)]
    if missing:
        return False, f"persona contract missing: {', '.join(missing)}"
    return True, "ok"


def check_work_contracts(body: str) -> tuple[bool, str]:
    work = section_text(body, "PART A") or body
    if "能力范围" not in work and "能力" not in work:
        return False, "work 能力 section missing"
    if "禁忌" not in body and "不写" not in body:
        return False, "work 禁忌/不写 constraint missing"
    return True, "ok"


def check_copyright(body: str, repo: Path) -> tuple[bool, str]:
    if not copyright_safe(body):
        return False, "SKILL.md contains code fence / blockquote / timestamp"
    summary = repo / "knowledge" / "research" / "merged" / "summary.md"
    if summary.exists():
        text = summary.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"Potential long quote lines:\s*(\d+)", text)
        if m and int(m.group(1)) > 0:
            return False, "research summary has potential long quote lines"
        m2 = re.search(r"Files scanned:\s*(\d+)", text)
        if m2 and int(m2.group(1)) < 3:
            return False, "research coverage below floor (files scanned < 3)"
    return True, "ok"


def run_checks(repo: Path, skill_file: Path, details: bool) -> tuple[bool, dict]:
    raw = skill_file.read_text(encoding="utf-8")
    data, body = parse_frontmatter(raw)
    checks: dict[str, tuple[bool, str]] = {}

    checks["frontmatter"] = check_frontmatter(data)
    checks["hard_constraints"] = check_hard_constraints(body)
    checks["persona_contracts"] = check_persona_contracts(body)
    checks["work_contracts"] = check_work_contracts(body)
    checks["copyright"] = check_copyright(body, repo)

    urls = grounded_urls(raw)
    checks["source_grounding"] = (len(urls) >= 2, f"{len(urls)} grounded URLs")

    # Technique words may appear in PART A (internal training) but the running
    # rules must forbid them in the OUTPUT. Assert that direction explicitly.
    rules = section_text(body, "运行规则")
    if "输出" in rules and any(w in rules for w in ("永不", "不得")):
        checks["technique_invisibility"] = (True, "output mandate forbids technique mentions")
    else:
        checks["technique_invisibility"] = (False, "运行规则 missing output-level invisibility mandate")

    passed_all = all(ok for ok, _ in checks.values())
    if details:
        print(f"target: {skill_file}")
        for name, (ok, msg) in checks.items():
            print(f"{'PASS' if ok else 'FAIL'}  {name} — {msg}")
        print(f"OVERALL {'PASS' if passed_all else 'FAIL'}")
    return passed_all, {k: (v[0], v[1]) for k, v in checks.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="luxun-skill quality gate")
    parser.add_argument("path", nargs="?", default="SKILL.md", help="Path to SKILL.md")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    skill_file = Path(args.path).expanduser().resolve()
    repo = skill_file.parent if skill_file.name == "SKILL.md" else skill_file
    passed, report = run_checks(repo, skill_file, not args.json)
    if args.json:
        print(json.dumps({"passed": passed, "checks": report}, ensure_ascii=False, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()