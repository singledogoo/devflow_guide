# 示例：TASK-ISP-007（演示数据，不代表真实项目状态）

- TYPE: defect
- BASELINE: **必须读取实际仓库，不在模板中虚构 SHA**
- REQ: REQ-ISP-001
- GOAL: 当 Gamma `enabled=false` 时跳过仅在启用状态需要的参数范围验证；启用时仍保持合法区间约束。
- SCOPE: 参数解析/验证模块 + 关联契约文档 + 单元/集成测试。禁止顺手修改无关 ISP 模块。
- DESIGN: 若现有 ADR 仍为 Proposed，不称其为已采纳或已发布契约；先检查审批状态。
- ACCEPTANCE: enabled=true 且合法/非法参数；enabled=false 且超范围/合法参数；缺省值；序列化兼容；错误码稳定。
- TEST: 真实执行 unit/API/回归；没有图像流水线自动测试时列出 UNKNOWN。
- RISK: 上游调用方参数解释、版本兼容、错误拒绝。
- STOP: 接口契约发生冲突或规范未采纳，先提交设计影响评估，不擅自发布。
