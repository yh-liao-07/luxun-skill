"""Contract tests for the distilled luxun skill artifacts."""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "SKILL.md"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def frontmatter() -> dict:
    lines = SKILL.read_text(encoding="utf-8").splitlines()
    assert lines[0].strip() == "---", "SKILL.md must start with frontmatter"
    data: dict = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = v.strip().strip("\"'")
    return data


class TestFrontmatter(unittest.TestCase):
    def test_name_is_kebab_case(self):
        self.assertRegex(frontmatter()["name"], NAME_RE)

    def test_required_fields_present(self):
        data = frontmatter()
        for field in ("description", "version", "user-invocable", "disable-model-invocation"):
            self.assertIn(field, data, f"missing frontmatter field: {field}")

    def test_not_auto_invoked(self):
        self.assertEqual(frontmatter()["disable-model-invocation"].lower(), "true")


class TestArtifactsExist(unittest.TestCase):
    def test_core_files(self):
        for name in ("SKILL.md", "work.md", "persona.md", "meta.json", "README.md"):
            self.assertTrue((REPO / name).exists(), f"missing {name}")

    def test_research_transparency(self):
        self.assertTrue((REPO / "knowledge" / "research" / "merged" / "summary.md").exists())
        raw = REPO / "knowledge" / "research" / "raw"
        notes = list(raw.glob("*.md"))
        self.assertGreaterEqual(len(notes), 3, "at least 3 research raw notes required")

    def test_docs_and_community_files(self):
        for name in ("docs/PRD.md", "docs/DISTILLATION.md", "docs/lang/README_EN.md",
                     "ROADMAP.md", "INSTALL.md", "CONTRIBUTING.md", "CITATION.cff", "LICENSE"):
            self.assertTrue((REPO / name).exists(), f"missing {name}")


class TestHardConstraints(unittest.TestCase):
    def test_technique_invisibility_in_running_rules(self):
        text = SKILL.read_text(encoding="utf-8")
        match = re.search(r"^##\s+运行规则\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        self.assertIsNotNone(match, "运行规则 section missing")
        rules = match.group(1)
        self.assertIn("技法", rules)
        self.assertIn("永不", rules)

    def test_no_writing_self_review_in_running_rules(self):
        text = SKILL.read_text(encoding="utf-8")
        match = re.search(r"^##\s+运行规则\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
        rules = match.group(1) if match else ""
        self.assertIn("自我检讨", rules)

    def test_copyright_safe(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertNotIn("```", text, "code fences would break AgentSkills parsers")
        self.assertFalse(re.search(r"^\s*>", text, re.M), "blockquote lines not allowed in SKILL.md")

    def test_honest_boundaries_present(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("诚实边界", text)
        self.assertIn("1936", text)


class TestDemoExamples(unittest.TestCase):
    def test_demo_output_blocks_are_technique_leak_free(self):
        demo = (REPO / "examples" / "demo.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```\n(.*?)```", demo, re.S)
        self.assertGreaterEqual(len(blocks), 2, "at least 2 fenced demo outputs expected")
        leaked = []
        for block in blocks:
            for word in ("白描", "反讽", "排比", "技法"):
                if word in block:
                    leaked.append(f"{word} in: {block[:30]!r}")
        self.assertEqual(leaked, [], "demo output blocks must not mention techniques")


class TestQualityGate(unittest.TestCase):
    def test_verify_skill_passes(self):
        result = subprocess.run(
            [sys.executable, str(REPO / "tools" / "verify_skill.py"), str(SKILL), "--json"],
            capture_output=True, text=True, cwd=REPO,
        )
        self.assertEqual(result.returncode, 0, f"verify_skill failed:\n{result.stdout}\n{result.stderr}")
        self.assertIn('"passed": true', result.stdout)


if __name__ == "__main__":
    unittest.main()