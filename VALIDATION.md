# v0.1.0 验证记录

验证日期：2026-10-25。

已执行：

- macOS / Python 3.12.14、3.14.6：22项行为测试通过。
- Codex Skill 结构校验通过（官方 skill-creator 随包校验器）。
- 从临时位置安装 Skill，再用安装后的相对资源初始化工作区并验证成功。
- 从独立 Skill ZIP 解压、安装并初始化成功。
- 相同安装可重复执行，不同内容的已有安装保持不变。
- 独立首答不可覆盖；评分更正保留旧评分。
- 即时修补、同题重复、未确认评分不建立延迟掌握证据。
- 新的独立失败会撤回稳定状态；反馈时间会重置延迟时钟。
- 公开包采用白名单，未包含真实学习记录、第三方教材或题库。
- GitHub公开地址：通过正式 skill-installer 下载并安装到临时目录成功；安装后的Skill文件与本地源文件一致。
- 下载后的Skill可独立初始化中文学习工作区，validate与review命令运行正常。
- GitHub Actions / Linux：22项测试与发布包构建通过。[首轮CI记录](https://github.com/XIAO-AA-AA/evidence-learning-coach/actions/runs/40148697118)。

发布下载项见[Releases](https://github.com/XIAO-AA-AA/evidence-learning-coach/releases)，后续测试见[Actions](https://github.com/XIAO-AA-AA/evidence-learning-coach/actions)。

尚未验证：真实宿主重新发现技能、其他Agent自动发现、Windows本地运行、真实学习效果。配置与文件测试通过不代表模型在每次实际教学中都正确遵循协议。

结构校验器的PyYAML仅安装在开发临时目录；项目运行和测试不依赖它。
