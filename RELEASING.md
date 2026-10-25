# 发布 v0.1.0

1. 确认发布目标为 `XIAO-AA-AA/evidence-learning-coach`。本目录就是独立仓库内容，不包含旧学习目录。
2. 检查 MIT 许可、名称、README 示例与发布地址。
3. 运行测试与 `python3 scripts/package.py`；检查 `dist/` 两个 ZIP 和校验文件。
4. 将本目录初始化为 Git 仓库并推送 main。不要在上级学习目录执行 `git add .`。
5. 将根目录 `VERSION` 更新为新版本号（如 `0.1.0`）并提交到 main。GitHub Actions 会重新运行测试、打包、创建对应标签和 Release。也支持在 Actions 页面手动运行 Release 工作流。已有版本不会自动覆盖。
6. 在一个未安装该 Skill 的临时目标目录，从公开 GitHub URL 安装，确认相对资源齐全，再用虚构学习目标验收。

只有第6步完成后，才能宣称公开网络安装已验证。本地安装成功不等于 GitHub 下载和宿主重新发现都已验证。

暂存版本默认 MIT。发布者应确认自己对新增内容有授权；第三方教材和学习者资料不包含在许可证授权范围。
