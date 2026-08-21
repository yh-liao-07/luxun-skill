# luxun-skill

一个用鲁迅的书面表达方式写文章的 Skill。

以《鲁迅全集》为底本，提取鲁迅的表达方式（白描、反讽、短句、文言白话融合等），做成的可调用写作工具。面向想写鲁迅风格文章、或用鲁迅的方式评论一件事的人。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)
[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-Skill-4D6BFE)](https://github.com/topics/dsh-plugin)

[蒸馏过程](docs/DISTILLATION.md) · [产品文档](docs/PRD.md) · [示例](examples/demo.md) · [English](docs/lang/README_EN.md)

---

## 这是什么

一个 Skill，输入写作任务，输出接近鲁迅书面风格的文字。

内容分三部分：

| 部分 | 内容 | 作用 |
|------|------|------|
| 写作方法论 | 白描、反讽、排比、比喻、收尾等写法的具体规则 | 怎么写 |
| 认知签名 | 心智模型、决策习惯、表达习惯、不擅长什么 | 怎么想 |
| 运行规则 | 约束类条款（见下） | 保证风格一致 |

生成时遵循两项约束：输出不得出现「白描」「反讽」等技法名称，亦不对写作方法作自我评述。技法仅作为 `work.md` 中的内部参考，不进入成稿。

## 蒸馏方法

用 [dot-skill 引擎](https://github.com/titanwings/colleague-skill) 的 celebrity 流程，按六个维度研究：

| 维度 | 内容 |
|------|------|
| 著作 | 「吃人」礼教批判、立人思想、拿来主义、反抗绝望 |
| 对话 | 论战、演讲记录的应答方式 |
| 表达 | 文言白话融合、白描、反讽、排比、色彩、收尾 |
| 决策 | 弃医从文、走异路、卖文为活、横站姿态 |
| 他人评价 | 毛泽东、郁达夫的评价，同代论敌的批评 |
| 时间线 | 创作期 → 散文诗期 → 杂文期 |

研究笔记在 [`knowledge/research/`](knowledge/research/)，可查、可复现。全文见 [docs/DISTILLATION.md](docs/DISTILLATION.md)。

生成后跑 [`tools/verify_skill.py`](tools/verify_skill.py) 做检查，通过才发布。

## 安装

按宿主编不同目录即可。仓库本身就是 Skill 目录。

```bash
git clone https://github.com/yh-liao-07/luxun-skill <目录>
```

| 宿主 | 目录 |
|------|------|
| DeepSeek Harness | `~/.dsh/skills/luxun-skill` 或 `.dsh/skills/luxun-skill` |
| Claude Code | `~/.claude/skills/luxun-skill` |
| OpenClaw | `~/.openclaw/workspace/skills/luxun-skill` |
| Codex | `~/.codex/skills/luxun-skill` |

## 使用

| 指令 | 作用 |
|------|------|
| `@luxun-skill: 写一段关于 XX 的杂文` | 生成文字 |
| `@luxun-skill: 帮我改这篇文章` | 修改润色 |
| `python tools/verify_skill.py SKILL.md` | 本地跑检查 |

默认 `disable-model-invocation: true`，只有显式调用 `@luxun-skill` 时才会启用。

## 示例

改写一段关于网络热梗的短文：

```text
用户 ❯ 用鲁迅的风格写一段关于「嘉豪」这个热梗的短文。

luxun.skill ❯ 嘉豪是一个名字，又不止是一个名字。它是一面照妖镜，
             照出的不是那个被喊的人，而是每一个喊出声的人——
             他们笑的时候，其实是在说：我不敢，所以你也别敢；
             我不活，所以你也别活。
```

更多见 [`examples/demo.md`](examples/demo.md)。

## 边界

- 不还原鲁迅的口语（无录音）
- 不替代《鲁迅全集》原文，引文请查原书
- 未收录书信、日记（本地全集不包含）
- 1936 年之后的事，只能按已有心智模型推测，已在 Skill 内标注

## 来源与致谢

- 底本：《鲁迅全集》（人民文学出版社 18 卷本）
- 引擎：[dot-skill](https://github.com/titanwings/colleague-skill)（titanwings）

授权 MIT。引用信息见 [CITATION.cff](CITATION.cff)。