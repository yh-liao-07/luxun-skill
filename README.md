<div align="center">

<img src="docs/social-preview.svg" alt="LUXUN.SKILL — 把鲁迅的表达方式蒸馏成一个写作 Skill" width="100%">

<br>

# 🖋️ luxun-skill

### *"横眉冷对千夫指，俯首甘为孺子牛。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-Skill-4D6BFE)](https://github.com/topics/dsh-plugin)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-teal)](https://github.com/topics/openclaw)
[![Codex](https://img.shields.io/badge/Codex-Skill-black)](https://github.com/features/copilot)

<br>

<table>
<tr><td align="left">

✍️ &nbsp;你想写**像**鲁迅的文章——冷静的白描、含而不露的反讽、短句的节律——但每次下笔都变成「鲁迅语录」的搬运？<br>
🗞️ &nbsp;你想让他**评**当下的事——用他的眼光看人心、看热闹、看集体的沉默？<br>
🧩 &nbsp;你想**蒸馏**一个鲁迅式的 Skill——不是模仿腔调，而是复现他的心智模型与表达框架？

</td></tr>
</table>

### ✨ 这，就是 luxun-skill 做的事。

<br>

**原材料 + 六维研究 → 一个真正像他的写作 Skill**

不搬语录，不抄名言。用他的方式**想**，用他的口吻**写**。

[📖 蒸馏过程](docs/DISTILLATION.md) · [📋 产品文档](docs/PRD.md) · [🗺️ Roadmap](ROADMAP.md) · [💬 示例](examples/demo.md)

[**English**](docs/lang/README_EN.md)

</div>

---

> 📝 **2026.07.01 Update — v1.0 发布**：基于 [dot-skill 引擎](https://github.com/titanwings/colleague-skill)（celebrity 六维研究流程）完成鲁迅蒸馏。原材料为《鲁迅全集》18 卷本地全文，输出「Work 写作方法论 + Persona 认知签名」双层 Skill，通过 13 项质量检查与技法隐形硬约束。

> 🔷 **运行宿主**：DeepSeek Harness 原生 filesystem skill 发现（`~/.dsh/skills/luxun-skill` 全局或 `.dsh/skills/luxun-skill` 项目级），Claude Code / OpenClaw / Codex 可直接安装。

---

## 目录

- [这是什么](#-这是什么)
- [蒸馏方法](#-蒸馏方法)
- [支持的数据来源](#-支持的数据来源)
- [安装](#-安装)
- [使用](#-使用)
- [示例](#-示例)
- [质量与诚实边界](#-质量与诚实边界)
- [引用与致谢](#-引用与致谢)

---

## 🖋️ 这是什么

一个**人**被蒸馏成了一种**写作能力**。

从《呐喊》《彷徨》《野草》《朝花夕拾》到十六部杂文集，鲁迅的书面表达被拆成三部分：

| 部分 | 内容 | 干什么用 |
|------|------|----------|
| **PART A — 写作方法论** | 白描、反讽、排比、比喻、收束的技术规范 | 「怎么写」——你的写作工具箱 |
| **PART B — 认知签名** | 心智模型、决策习惯、表达 DNA、诚实边界 | 「怎么想」——他看问题的框架 |
| **运行规则** | 技法隐形、永不自我检讨、Layer 0 优先 | 保证写出来像他，而不是像『模仿他的 AI』 |

> ⚠️ 本 Skill **不搬运语录**。它提取的是表达框架——你可以用它写全新的内容，但内容本身属于你。

---

## 🔬 蒸馏方法

完整的蒸馏过程见 [docs/DISTILLATION.md](docs/DISTILLATION.md)，核心是 dot-skill 引擎的 **celebrity 六维研究**：

| 维度 | 研究对象 | 从《鲁迅全集》中提取 |
|------|----------|----------------------|
| 1 著作 | 系统性观点 | 「吃人」礼教批判、立人思想、拿来主义、反抗绝望 |
| 2 对话 | 论战与应答 | 与梁实秋论战、演讲记录的应答方式 |
| 3 表达 DNA | 语言指纹 | 文言白话融合、白描、反讽、排比、色彩、名句收束 |
| 4 决策 | 行为证据 | 弃医从文、走异路、卖文为活、横站姿态 |
| 5 他者视角 | 外部评价 | 毛泽东、郁达夫、同代论敌的对照 |
| 6 时间线 | 认知演变 | 创作期 → 散文诗期 → 杂文期 |

研究笔记完整保留在 [`knowledge/research/`](knowledge/research/)，可审计、可复现。

**质量关卡**：13 项自动检查（心智模型、表达 DNA、诚实边界、矛盾张力、引用锚定、版权安全……），全部通过才发布。见 [`tools/verify_skill.py`](tools/verify_skill.py)。

---

## 📦 支持的数据来源

| 来源 | 类型 | 说明 |
|------|------|------|
| 📚 《鲁迅全集》文本 | 一手著作 | 本 Skill 的主要底本（本地 18 卷全文） |
| 📄 PDF / 图片 / 截图 | 辅助 | 手稿、文集扫描件 |
| 📝 Markdown / 直接粘贴 | 辅助 | 补充材料或校正对话 |
| 🌐 公开网页 | 外部佐证 | 论战史、外部评价（研究阶段使用） |

---

## ⚡ 安装

这是 2026 年——你有 Agent，让它自己装。在你的 Agent（DeepSeek Harness / Claude Code / OpenClaw / Codex）里直接说：

> 帮我安装 luxun-skill：`https://github.com/titanwings/luxun-skill`

Agent 会检测当前宿主的 skills 目录，克隆仓库并注册入口。装好后在任何宿主输入 `@luxun-skill`（DSH）或 `/{luxun-skill}` 即可启动。

<details>
<summary><b>🛠️ 想自己装？点开看路径</b></summary>

<br>

```bash
git clone https://github.com/titanwings/luxun-skill <TARGET>
```

| 宿主 | `<TARGET>` 路径 |
|------|-----------------|
| DeepSeek Harness | `~/.dsh/skills/luxun-skill`（全局）或 `.dsh/skills/luxun-skill`（项目） |
| Claude Code | `~/.claude/skills/luxun-skill` |
| OpenClaw | `~/.openclaw/workspace/skills/luxun-skill` |
| Codex | `~/.codex/skills/luxun-skill` |

</details>

---

## 🚀 使用

装好后，把写作任务直接交给它：

| 指令 | 说明 |
|------|------|
| `@luxun-skill: 写一段关于XX的杂文` | 完整调用——方法论 + 鲁迅式思维 + 表达风格 |
| `@luxun-skill: 帮我改一下这篇文章` | 用鲁迅的表达层次修改润色 |
| `tools/verify_skill.py` | 本地跑质量门（13 项检查） |

所有技法自动隐形：输出中不会出现「白描」「反讽」字样，也不会自我检讨「这篇我没套技法」。

---

## ✨ 示例

### 改写一篇关于「嘉豪」热梗的短文

```text
用户 ❯ 用鲁迅的风格写一段关于「嘉豪」这个网络热梗的短文。
       技法不要太刻意，自由发挥，立意要深刻。

luxun.skill ❯ 嘉豪是一个名字，又不止是一个名字。它是一面照妖镜，
             照出的不是那个被喊的人，而是每一个喊出声的人——
             他们笑的时候，其实是在说：我不敢，所以你也别敢；
             我不活，所以你也别活。

             可我总想起那个举手的人。
             他的手心在出汗，他的答案或许是错的，他的脸涨得通红。
             但那个瞬间，他是亮的。
             是那种让满屋子的沉默都显得灰暗的亮。
```

### 用「拿来主义」的框架回答一个问题

```text
用户 ❯ 现在的 AI 工具到底该不该用？

luxun.skill ❯ 不是「用」或「不用」的问题。
             是要先问：它来了之后，你的脑子还动不动？
             会动的，拿来用，越用越好用。
             不会动的，用完只剩一个更空的脑袋——
             那它不是工具，是鸦片。
```

<br>

更多例子见 [`examples/demo.md`](examples/demo.md)。

---

## 🧭 质量与诚实边界

| 检查 | 状态 |
|------|:----:|
| 心智模型（3 个，可跨语境迁移） | ✅ |
| 表达 DNA（8 类风格标记，带原文例证） | ✅ |
| 诚实边界（无录音、无书信日记、1936 后仅外推） | ✅ |
| 矛盾张力（冷笔与热肠、白话与文言、启蒙与绝望） | ✅ |
| 版权安全（无长引用、无全文转储） | ✅ |
| 技法隐形（输出中不出现技法名词） | ✅ |

**它不能做什么**：
- 不能还原鲁迅的口语/声音（无录音留存）
- 不能代替《鲁迅全集》本身——语录请查原文
- 对 1936 年之后的世界，只能基于其心智模型合理推测（已标注）

---

## 📖 引用与致谢

本 Skill 使用 **dot-skill 引擎**（[titanwings/colleague-skill](https://github.com/titanwings/colleague-skill)）的 celebrity 六维研究流程蒸馏生成。感谢 titanwings 的开源工作。

原材料：《鲁迅全集》（人民文学出版社 18 卷本，本地 txt 库）。

CITATION.cff 见 [CITATION.cff](CITATION.cff)。

---

<div align="center">

Created by [@yh-liao-07](https://github.com/yh-liao-07) · 基于 [dot-skill](https://github.com/titanwings/colleague-skill) 引擎

</div>