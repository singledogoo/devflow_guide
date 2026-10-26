# devflow_guide 1.0.0 · 验证记录

## 本次真实执行的检查

- Python `scripts/test_devflow.py`：6 项回归测试成功（重复初始化、存量文档映射、不覆盖已有文件、路径越界、追踪错误、类型识别、干运行）。
- 新项目初始化冒烟测试：`embedded / web / app` × `lite / standard / high` 共 9 组成功；所列文档模板全部创建；`audit` 无结构错误但按预期报告未填写占位符；`release` 预检按预期阻断且远端状态 UNKNOWN。
- HTML：使用 Chromium/Playwright 的离线内联方式验证桌面 1440×900 和手机 390×844 页面布局、项目切换、阶段节点、门禁勾选、词典过滤、移动目录；无 JavaScript 执行错误，未发现整页水平溢出。
- 包装：Skill 名称 `devflow-guide` 与目录一致，`SKILL.md` 含标准 YAML 元数据，所有参考资料/模板存在，HTML 无外部脚本依赖。

## 不能由上述测试得出的结论

- 未在实际用户开发仓库运行、未接入真实 GitHub PR/CI、未在嵌入式目标板运行 HIL、未验证生产部署、未取得独立安全/合规批准。
- CLI 对文档/代码相符性的审查是结构性与启发式检查；无法保证业务语义、代码实现正确性或所有关键风险均被覆盖。
- 对正式项目的引入需先执行 `inspect` / `init --dry-run`，经维护者审查后使用。

## English manual

- manual/zh/devflow_guide.html is the original Chinese manual, with a link to English.
- manual/en/devflow_guide.html is the matching English manual, using the same layout and interaction.
- Checks before upload: balanced HTML, inline script passed node --check, and an Edge screenshot at 1440px. The page script builds 10 stages, 55 glossary entries, and 4 design-gate checks.
