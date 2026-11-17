---
name: policy-research-contracts
description: "JSON Schema contracts, evidence-grading rules, rejection rules, research-extension fields and report templates for the Policy Research Think Tank. Load when producing or validating any stage of a policy research report."
---

# 政策研究契约体系

本 Skill 是「政研智库团」的共享契约层，由原「政策采集智能体群 v2.0」的 5 套 Schema 升级而来。**所有成员产出、主理人汇编、校验驳回，均以本目录文件为准。**

## 一、契约文件索引

| 阶段 | 责任 Agent | 契约文件 | 关键约束 |
|------|-----------|---------|---------|
| Phase 1 范围 | scope-metrics-analyst | `references/scope.schema.json` | input_type、S1-Sn、regions.primary、boundary_confidence；新增研究问题、时间窗、指标口径字典 |
| Phase 2 证据 | policy-evidence-scanner | `references/policy.schema.json` | 14 项必填政策字段 + evidence_quote；≥10 条全国高相关；A/B 分组；沿革、区域对比、量化锚点 |
| Phase 3 机会风险 | impact-action-analyst | `references/opportunity_risk.schema.json` | ≥8 条、覆盖 ≥60% 赛道、B 组引用 ≤20%；新增申报落地行动清单 |
| Phase 4 推演 | logic-scenario-analyst | `references/reasoning.schema.json` | 每条关键政策恰好 L1-L6、三情景 A/B 标注；新增量化影响测算与敏感性 |
| Phase 5/6 交付 | report-contract-validator / 主理人 | `references/final_report.schema.json` | meta.regions、handoff_message、validation；新增研究扩展章节 |

其他资料：
- `references/source-manifest.md`：原始 zip 包的完整解析与字段去向映射（含原 UI 组件配置）。
- `references/research-extensions.md`：四项新增研究能力的字段定义与可追溯硬规则。
- `templates/research-report-outline.md`：人类可读政策研究报告大纲。
- `templates/final_report.example.json`：最终 JSON 骨架（占位符，禁止当作事实使用）。
- `examples/minimal-input.json`：最小输入示例。

## 二、流水线与信息流

```
user_input → scope.json → policies(A/B + lineage + comparison + anchors)
           → opportunities_risks(+ action_items)
           → reasoning(+ quantitative_impact)
           → validation → final_report.json → H5 报告交接
```

所有跨阶段信息流必须经主理人中转。每阶段产出为合法 JSON，不得以散文替代契约字段。

## 三、证据分级铁律

1. **A 组（直接适用）**：国家级政策 + `regions.primary` 主区域政策。后续结论以 A 组为主证据。
2. **B 组（间接参考）**：其他省市政策。仅用于趋势或跟进可能性判断，必须写明来源省市；在 `evidence_policy_ids` 中占比 ≤20%。
3. 只采信官方发文详情页；`source_url` 必须是官方页面；`evidence_quote` 必须是原文摘录。
4. 征求意见稿、规划意向按 `status` 枚举标注为非强制，不得当作已生效约束。
5. 主区域确无核实文件时显式写「该区域暂无经核实的地方文件，建议以全国层面政策+基准情景为主要依据」，不得脑补。
6. 区域扩展：追加 `regions.additional`、复用国家级政策、不覆盖主区域结论；更换主区域则重跑 Phase 2-5。

## 四、枚举速查（来自 policy.schema.json）

| 字段 | 取值 |
|------|------|
| effect_level | 法律 / 行政法规 / 部门规章 / 部门规范性文件 / 地方性法规 / 地方政府规章 / 地方规范性文件 / 国家标准 / 行业标准 / 规划纲要 / 征求意见稿 |
| region_scope | national / regional |
| applicability | 直接适用 / 间接参考 / 不适用 |
| status | 已生效 / 已发布未生效 / 征求意见稿 / 规划意向（非强制） |
| relevance / certainty_tier / boundary_confidence | 高 / 中 / 低 |
| pestel_dimension | 数组，至少 1 项（P / E / S / T / E / L） |

## 五、驳回（REJECTED）规则

任一命中即将该阶段产出退回责任 Agent 重做，主理人**不得自行修补**：

- 全国高相关政策 < 10 条；
- 政策缺 PESTEL / applicability / 任一必填字段 / source_url / evidence_quote；
- 未尝试主区域官方平台；
- 机会风险 < 8 条、赛道覆盖 < 60%、B 组引用 > 20%；
- logic_chain 缺层、跳层、层间缺 transmission_variable；
- 三情景触发条件未标 A/B 证据；
- 沿革版本链引用了不存在的政策 id；区域对比矩阵格子缺政策 id 或来源 URL；
- 量化数值既无 `quantitative_anchors` 出处、也未标注为假设；
- `action_items` 缺责任部门或时间节点（无出处时须显式写「待核实」）。

## 六、交付规范

1. 最终输出符合 `final_report.schema.json`，用 ```json 代码块包裹。
2. `meta.regions.primary` 必填，`meta.regions.additional` 可选；`meta.handoff_message` 固定为「H5 报告已由 policy-report-h5 渲染器生成，可直接在右侧结果区预览。」
3. 人类可读报告按 `templates/research-report-outline.md` 输出，并明确区分：已核实事实 / 基于 A 组的判断 / 基于 B 组的趋势参考 / 测算假设。
4. `validation.valid` 为 false 时禁止交付，必须先退回重做。

## 七、相对原包的修复与升级

- 原 `policy.schema.json` 声明 `additionalProperties:false`，但政策提示词要求输出 `evidence_quote`，两者冲突；本版已将 `evidence_quote` 正式纳入 schema 并设为必填。
- 原包 `workbuddy_manifest.json` 为自定义格式（`manifest_version: workbuddy.agent.v1`），无法被 WorkBuddy 专家中心识别；本版改为标准 `.codebuddy-plugin/plugin.json` + `settings.json` + Team 成员结构，原 UI 组件配置留档于 `source-manifest.md`。
- 原 5 个角色提示词升级为 5 个具备独立职责、数据获取方式与结构化输出模板的 Agent MD，并新增主理人 SOP 与正式团队协作机制。
- 新增四项研究能力字段，详见 `research-extensions.md`。
