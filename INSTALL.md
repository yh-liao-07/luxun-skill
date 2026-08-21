# luxun-skill 安装说明

---

## 选择你的平台

### A. DeepSeek Harness（推荐）

本项目遵循官方 [AgentSkills](https://agentskills.io) 标准，整个 repo 就是 skill 目录。克隆到 DSH skills 目录即可：

```bash
# 方式 1：安装到当前项目（仅此项目可用）
git clone https://github.com/titanwings/luxun-skill .dsh/skills/luxun-skill

# 方式 2：安装到全局（所有项目可用）
git clone https://github.com/titanwings/luxun-skill ~/.dsh/skills/luxun-skill
```

然后在 DSH 中直接引用 `@luxun-skill` 即可。

> 注意：frontmatter 中 `disable-model-invocation: true`，DSH 不会自动把它塞进对话；只有你显式调用 `@luxun-skill` 时才激活。

### B. Claude Code

```bash
git clone https://github.com/titanwings/luxun-skill ~/.claude/skills/luxun-skill
```

然后在对话中写 `@luxun-skill` 或 `/luxun-skill`。

### C. OpenClaw

```bash
git clone https://github.com/titanwings/luxun-skill ~/.openclaw/workspace/skills/luxun-skill
```

### D. Codex

```bash
git clone https://github.com/titanwings/luxun-skill ~/.codex/skills/luxun-skill
```

---

## 验证安装

```bash
python tools/verify_skill.py SKILL.md
```

期望输出：全部 `PASS`，末尾 `OVERALL PASS`。这 13 项检查确保：
- 心智模型、表达 DNA、诚实边界、矛盾张力都在
- 技法隐形硬约束生效（SKILL.md 明确禁止在输出中提及技法名）
- 引用锚定 ≥ 2 个真实来源
- 版权安全（无长引用转储）

---

## 升级

```bash
cd <你的 luxun-skill 目录>
git pull
python tools/verify_skill.py SKILL.md   # 升级后跑一遍质量门
```

每次升级都应通过完整质量门，任何改动不得削弱「技法隐形」与「诚实边界」两项。