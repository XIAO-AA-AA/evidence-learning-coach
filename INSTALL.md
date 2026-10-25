# 安装与开始学习

## 一句话安装

对支持 `skill-installer` 的 Codex 发送：

> 请使用 skill-installer 安装 https://github.com/XIAO-AA-AA/evidence-learning-coach/tree/main/skills/evidence-learning-coach

技能将在安装完成后的下一轮对话可用。安装技能本身不创建学习档案，也不启动学习；再告诉 Agent 你想学什么和工作区位置。

## ZIP / 本地安装

下载并解压完整项目，进入解压目录运行：

```sh
python3 install.py
```

默认将 `skills/evidence-learning-coach` 复制到 Codex 的技能目录：`$CODEX_HOME/skills`，未设置时使用用户目录下的 `.codex/skills`。不会修改其他技能或全局指令。

指定一个有写入权限的位置：

```sh
python3 install.py --dest ./agent-skills
```

`--dest` 指技能的父目录，最终目录是 `./agent-skills/evidence-learning-coach`。自定义位置需要 Agent 自己支持读取或发现该路径。

相同内容再次安装会直接成功；已有不同内容时会停止，保留现有版本。升级前请自行备份旧版本，再选择新安装位置；脚本不会自动覆盖用户修改。

只下载 Skill ZIP 时，可把包含 `SKILL.md` 的 `evidence-learning-coach` 目录放入 Agent 已配置的技能目录。

安装器拒绝包内软链接，并检查必须文件。下载和安装只需要文件权限；不需要 API Key、不安装依赖、不申请管理员权限。

## 给其他 Agent 的安装指令

> 阅读此仓库的 INSTALL.md 和 skills/evidence-learning-coach/SKILL.md。将该技能安装到你实际支持的技能目录，保持所有相对路径完整，验证文件可读取。若你没有技能发现能力，则读取学习协议直接执行。说明已经验证的能力，并保留现有学习记录。

这是通用的交接说明，不代表所有 Agent 都支持自动发现、写文件或持久存档。

## 开始 / 继续

> 使用 evidence-learning-coach，帮我学习日语。我目前能读假名，每天40分钟，目标是能进行旅行对话。请先给一个小诊断，再安排今天的练习。记录位置为 ./learning-workspace，只有我说存档时才保存。

> 使用 evidence-learning-coach，继续 ./learning-workspace，严格从最新续接点开始。

> 对今天的学习存档，保留独立首答，更新复习队列，并写明下一次第一项任务。

## 安装验收

Agent 应确认 `SKILL.md`、`references/`、`scripts/learning.py` 和 `assets/workspace/` 都在；使用一个临时目录初始化并验证工作区后，删除或保留该测试目录均由宿主环境策略决定。不要往现有真实学习目录写测试数据。
