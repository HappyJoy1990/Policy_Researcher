# 源包解析留档：政策采集_Workbuddy_新版.zip

> 本文件用于保证「不丢信息」。原包为自定义智能体群配置，不是 WorkBuddy 标准专家包，改造后其全部内容均有对应去向。

## 一、原包文件清单

| 文件 | 作用 |
|------|------|
| README.md | 五智能体政策研判流水线说明、运行要求、H5 交接提示 |
| workbuddy_manifest.json | 自定义导入配置（manifest_version `workbuddy.agent.v1`） |
| agents/master_orchestrator.prompt.md | 总控协调官：7 步流程、驳回规则、区域扩展、最终交付 |
| agents/scope_parser.prompt.md | 主体/赛道/主区域解析 |
| agents/policy_scanner.prompt.md | 全国＋主区域官方政策检索，14 字段政策卡片 |
| agents/opportunity_risk.prompt.md | 机会风险 ≥8 条、覆盖 ≥60%、B 组 ≤20% |
| agents/reasoning.prompt.md | L1-L6 六层逻辑链、PESTEL、多源流、三情景 |
| agents/json_validator.prompt.md | 契约校验，只校验不改写 |
| schemas/*.schema.json（5 个） | scope / policy / opportunity_risk / reasoning / final_report 分步契约 |
| examples/minimal-input.json | `{"user_input":"示例新能源装备公司"}` |

## 二、原 workbuddy_manifest.json 全文

```json
{
  "manifest_version": "workbuddy.agent.v1",
  "id": "cn.policy-radar.master-orchestrator",
  "name": "产业政策研判总控",
  "version": "2.0.0",
  "locale": "zh-CN",
  "description": "按产业、区域、政策、机会风险和六层逻辑链生成结构化政策研判报告。",
  "entry_agent": "Scope_Parser_Agent",
  "orchestrator_prompt": "agents/master_orchestrator.prompt.md",
  "subagents": [
    {"id":"Scope_Parser_Agent","prompt":"agents/scope_parser.prompt.md"},
    {"id":"Policy_Scanner_Agent","prompt":"agents/policy_scanner.prompt.md"},
    {"id":"Opportunity_Risk_Agent","prompt":"agents/opportunity_risk.prompt.md"},
    {"id":"Reasoning_Agent","prompt":"agents/reasoning.prompt.md"},
    {"id":"JSON_Validator_Agent","prompt":"agents/json_validator.prompt.md"}
  ],
  "capabilities": ["web_search", "official_source_verification", "structured_json", "h5_report_handoff"],
  "ui": {
    "icon": {"type":"svg","mime_type":"image/svg+xml","data":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 64 64\"><rect width=\"64\" height=\"64\" rx=\"14\" fill=\"#155EEF\"/><path d=\"M16 18h32v8H16zm0 14h22v8H16zm0 14h32v4H16z\" fill=\"#fff\"/><circle cx=\"46\" cy=\"36\" r=\"7\" fill=\"#F79009\"/></svg>"},
    "input_component": {"type":"textarea","name":"user_input","label":"公司名称或行业领域","placeholder":"例如：某新能源装备公司；或：低空经济","required":true},
    "progress_component": {"type":"stepper","steps":["产业与区域解析","全国+主区域政策检索","机会与风险","六层逻辑推演","合并校验与交付"]},
    "output_component": {"type":"code","language":"json","copyable":true,"title":"政策研判报告 JSON"}
  },
  "contracts": {"final_report":"schemas/final_report.schema.json","scope":"schemas/scope.schema.json","policy":"schemas/policy.schema.json","opportunity_risk":"schemas/opportunity_risk.schema.json","reasoning":"schemas/reasoning.schema.json"}
}
```

## 三、原包运行要求（原文要点）

- 需要联网检索能力；公司输入需查询官方工商/企业登记信息；政策必须引用官方发文详情页。
- 严格区分 A 组直接适用证据与 B 组间接参考证据；任何契约不通过都必须驳回重做。
- 最终回复必须包含完整 JSON 代码块，`meta` 中写明主区域和扩展区域，并提示「请复制此 JSON 到 Workbuddy 中生成 H5 报告。」

## 四、去向映射

| 源内容 | 本专家包去向 |
|--------|-------------|
| 总控协调官 7 步流程、驳回规则、区域扩展 | `agents/policy-research-team-lead.md` 的 SOP Phase 0-6 与区域扩展规则 |
| Scope_Parser_Agent | `agents/scope-metrics-analyst.md` |
| Policy_Scanner_Agent | `agents/policy-evidence-scanner.md` |
| Opportunity_Risk_Agent | `agents/impact-action-analyst.md` |
| Reasoning_Agent | `agents/logic-scenario-analyst.md` |
| JSON_Validator_Agent | `agents/report-contract-validator.md` |
| 5 个 schema | `skills/policy-research-contracts/references/*.schema.json`（修复冲突并扩展字段） |
| examples/minimal-input.json | `skills/policy-research-contracts/examples/minimal-input.json` |
| capabilities 四项 | web_search / official_source_verification 写入成员数据获取方式；structured_json 写入契约 Skill；h5_report_handoff 写入交付规范与 `meta.handoff_message` |
| ui.input_component（textarea 必填、占位提示） | 专家卡片 `quickPrompts` 第一条 + 主理人 Phase 1 输入规范 |
| ui.progress_component（5 步 stepper） | 主理人 SOP 的 Phase 1-5 与每阶段进度通报要求 |
| ui.output_component（可复制 JSON 代码块） | 主理人 Phase 6 交付规范 |
| ui.icon（蓝色文档 + 橙色圆点 SVG） | 由专家包 `avatars/team.png` 与卡片展示替代，原 SVG 留档于本文件 |
| manifest_version / id / name / version / locale / description | 由标准 `.codebuddy-plugin/plugin.json` 的 name、version、description、displayName、displayDescription 承接 |

## 五、改造中发现的问题

1. **格式不兼容**：`workbuddy.agent.v1` 为自定义清单，专家中心按 `.codebuddy-plugin/plugin.json` 识别，原包直接放入不会被检测到。
2. **契约冲突**：`policy.schema.json` 设置 `additionalProperties:false` 且未声明 `evidence_quote`，但 policy_scanner 提示词要求逐条输出该字段，按原契约必然校验失败。本版已把 `evidence_quote` 纳入 schema 必填项。
3. **协作机制缺失**：原包用自然语言描述「依次调用」，没有正式的建团、调度、消息中转与「不代写成员产出」约束。本版按 Team 规范补齐。
4. **能力边界**：原包止于「采集 + 研判」，无政策沿革、区域对比、量化测算与落地路径。本版新增四项研究能力，见 `research-extensions.md`。
