# luxun-skill

A Skill for writing in Lu Xun's written style: plain-style narration, understated irony, short sentences, and a mix of classical and vernacular Chinese.

Built from the *Complete Works of Lu Xun*. For people who want to write in a Lu Xun-like register, or comment on something the way he would.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-Skill-4D6BFE)](https://github.com/topics/dsh-plugin)

[Distillation record](../docs/DISTILLATION.md) · [PRD](../docs/PRD.md) · [Examples](../examples/demo.md) · [中文](../README.md)

---

## What this is

A Skill that takes a writing task and outputs text in a Lu Xun-like register.

Three parts:

| Part | Content | Purpose |
|------|---------|---------|
| Writing methodology | Rule-level notes on plain-style narration, irony, parallelism, metaphor, endings | How to write |
| Cognitive signature | Mental models, decision habits, expression habits, limits | How to think |
| Operating rules | Constraints (see below) | Keep the style consistent |

Two hard constraints when generating: the output must not mention technique names (such as "plain-style narration" or "irony"), and must not contain meta-commentary about the writing itself. Techniques live only in `work.md`; they do not surface in the finished text.

## Distillation method

Built with the [dot-skill engine](https://github.com/titanwings/colleague-skill) celebrity flow, researched across six dimensions:

| Dimension | Content |
|-----------|---------|
| Writings | critique of ritual, "stand the person", take-it-ism, resistance to despair |
| Conversations | polemics, lecture records |
| Expression | classical-modern fusion, plain narration, irony, parallelism, color, endings |
| Decisions | giving up medicine for literature, living by the pen |
| External views | Mao Zedong, Yu Dafu, and his opponents' criticism |
| Timeline | creative era → *Wild Grass* era → essay era |

Research notes are in [`knowledge/research/`](../knowledge/research/). Full record in [docs/DISTILLATION.md](../docs/DISTILLATION.md). The repo also ships [`tools/verify_skill.py`](../tools/verify_skill.py), which runs the checks before release.

## Install

The repository is itself the Skill directory. Clone it into the host's skills directory:

```bash
git clone https://github.com/yh-liao-07/luxun-skill <dir>
```

| Host | Directory |
|------|-----------|
| DeepSeek Harness | `~/.dsh/skills/luxun-skill` or `.dsh/skills/luxun-skill` |
| Claude Code | `~/.claude/skills/luxun-skill` |
| OpenClaw | `~/.openclaw/workspace/skills/luxun-skill` |
| Codex | `~/.codex/skills/luxun-skill` |

## Usage

| Command | Purpose |
|---------|---------|
| `@luxun-skill: write an essay about X` | Generate text |
| `@luxun-skill: revise this article` | Edit/reword |
| `python tools/verify_skill.py SKILL.md` | Run local checks |

`disable-model-invocation: true` is set, so the Skill activates only when `@luxun-skill` is called explicitly.

## Boundaries

- Does not reproduce Lu Xun's spoken voice (no recordings)
- Does not replace the original works; quote from the source text directly
- Does not include letters or diaries (not in the local corpus)
- For events after 1936, extrapolates from his mental models only — noted inside the Skill

## Sources & credits

- Base corpus: *Complete Works of Lu Xun* (People's Literature Publishing House, 18 volumes)
- Engine: [dot-skill](https://github.com/titanwings/colleague-skill) (titanwings)

MIT license. See [CITATION.cff](../CITATION.cff).