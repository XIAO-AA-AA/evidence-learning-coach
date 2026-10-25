# Evidence Learning Coach

把 AI 变成能记住学习进度、按证据批改、安排延迟复测的学习教练。

适合语言、数学、编程、职业考试和其他长期学习。围绕真实目标选择练习与评分方式，保留每次独立首答，区分“看过答案后会了”与“隔天还能独立完成”。

[English](README.en.md) · [安装](INSTALL.md) · [下载](https://github.com/XIAO-AA-AA/evidence-learning-coach/releases/latest) · [方法与掌握度](skills/evidence-learning-coach/references/learning-protocol.md) · [评分规则](skills/evidence-learning-coach/references/scoring-rubrics.md)

## 一句话安装

在支持 `skill-installer` 的 Codex 中发送：

> 请使用 skill-installer 安装 https://github.com/XIAO-AA-AA/evidence-learning-coach/tree/main/skills/evidence-learning-coach

安装后在下一轮发送：

> 使用 evidence-learning-coach 帮我学习线性代数，每天30分钟，先评估我的基础；学习记录保存在当前项目的 learning-workspace 目录。

下载仓库 ZIP 后，也可以让有文件权限的 Agent 读取 `INSTALL.md` 完成安装。普通聊天工具可使用 Markdown 协议，但自动存档和精确续接需要文件读写能力。自动发现已适配 Codex；其他 Agent 尚未逐一验证。

## 一次学习如何进行

1. 确定目标、现有基础、可用时间与参考材料，问题足够明确时直接开始。
2. 学习者先独立回答或提交作品。提前固定评分标准，暂不展示答案。
3. 依据得分点或可验证行为评分，保留首答、解释错误，接受符合标准的等价表达。
4. 只修补暴露的缺口，提供必要的概念讲解或记忆线索。
5. 隔题或隔日再用未见过的变式测试，分别记录即时修补与延迟表现。
6. 根据证据调整下一次任务，并保存能精确续接的位置。

这套方法来自实际长期学习中的迭代。目前是学习工作流工具，没有通过对照实验验证提分效果，也不承诺任何考试结果。

## 用同一个框架学习不同内容

| 目标 | 独立证据 | 评分重点 |
| --- | --- | --- |
| 记术语、考试默写 | 不查资料的回答 | 得分点覆盖、准确性、固定术语 |
| 数学、计算 | 解题过程与结果 | 模型、步骤、边界、单位与计算 |
| 编程 | 代码、运行结果、解释 | 功能、测试、排错与迁移能力 |
| 语言、写作 | 原始口语或文本 | 任务完成、准确性、表达与迁移 |
| 实践技能 | 可观察作品或实际演示 | 可验证行为；自述和实际演示分别记录 |

评分不足以确认时保留“待复核”，不编造精确分数或把模型判断当成权威结论。

## 本地工作区

核心记录采用可读 Markdown 和 JSON，不需要数据库、API Key 或 Python 第三方依赖。初始化与记录工具要求 Python 3.10+；教练协议本身可直接阅读使用。

```sh
python3 skills/evidence-learning-coach/scripts/learning.py init \
  --root ./learning-workspace --subject '线性代数' --goal '独立解线性方程组'

python3 skills/evidence-learning-coach/scripts/learning.py validate --root ./learning-workspace
python3 skills/evidence-learning-coach/scripts/learning.py review --root ./learning-workspace
```

```text
learning-workspace/
├── profile.md                 目标、偏好、记录权限
├── latest-session-notes.md    下一次从这里续接
├── plans/current-week.md      当前计划
├── progress/mastery-tracker.md
├── mistakes/review-queue.md
├── sources/index.md           材料出处和可信度
├── sessions/                 按需保存的会话总结
└── state/
    ├── config.json
    ├── attempts/             独立首答，逐条保存且不覆盖
    └── assessments/          单独的评分证据，可追加更正
```

学习者说“继续”时，只读取档案、最新续接记录以及当前任务相关的少量资料；不反复扫描全部材料。保存策略默认 `on_request`，用户明确要求存档时才写学习记录；可在档案中开启 `automatic`。

## 可检查的掌握度

`未测试 → 待练习 / 独立首答通过 → 当场修补 → 延迟通过 → 稳定证据`

这些是证据标签，不是固定升级流水线。一次独立错误会重新进入待练习；看过答案后的正确复述只算当场修补。默认24小时为延迟门槛，至少两次相隔24小时且使用不同变式的独立成功支持“稳定证据”；同主题的提示、答案和复述会重置延迟计时。门槛可按目标调整，并非通用学习定律。

自动规则无法判断题目是否真正陌生或评分是否正确，依赖 Agent 如实标记；工具会拒绝引用未确认的评分来升级掌握度。详细规则见[协议](skills/evidence-learning-coach/references/learning-protocol.md)。

## 来源和隐私

只随包提供原创协议、模板和虚构示例。学习资料、个人档案、答题记录和第三方题库由学习者本地维护。生成题清楚标注原创；不把出版物标注的“真题”当成已核验的官方来源。政策、日期等容易变化的事实应查当前可靠来源。

安装包不会修改全局 Agent 指令，不上传学习记录，不安装后台服务。工作区默认忽略其所有内容，避免误提交。主动公开作品时，请单独选择要分享的文件。

## 开发与分发

```sh
python3 -m unittest discover -s tests -v
python3 scripts/package.py
```

打包器只收集本仓库白名单内的文件，输出完整项目 ZIP、单独 Skill ZIP 和 SHA-256 校验文件。更新 `VERSION` 并推送 main 后，GitHub Actions 会验证、创建版本标签并发布下载项。发布流程见 [RELEASING.md](RELEASING.md)，当前验证边界见 [VALIDATION.md](VALIDATION.md)。

版本：`0.1.0`。代码、原创文档、模板统一采用 [MIT](LICENSE)；第三方来源的权利属于其权利人。
