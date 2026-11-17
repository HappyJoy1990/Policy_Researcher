# 政研智库团（Policy Research Think Tank）

Team 型专家团（6 个角色），由 `政策采集_Workbuddy_新版.zip` 解析改造而来。输入公司名称或行业领域，联网检索官方政策，输出经契约校验的政策研究报告 + 可直接预览的 H5 报告页。H5 渲染器已内置（policy-report-h5 Skill），客户会话里产出 JSON 后自动渲染，无需复制到别处。

## 来源与改造

原包是自定义格式的「政策采集智能体群 v2.0」（1 总控 + 5 子智能体 + 5 套 JSON Schema），无法被专家中心直接识别。本包按 WorkBuddy 专家规范 v2.0 转为标准 Team 型专家包，并升级为「政策研究」：

| 原包 | 本包 |
|------|------|
| master_orchestrator | `policy-research-team-lead`（谭策衡，首席政策研究官） |
| Scope_Parser_Agent | `scope-metrics-analyst`（解界明，研究范围与口径官） |
| Policy_Scanner_Agent | `policy-evidence-scanner`（查文渊，政策证据与沿革研究员） |
| Opportunity_Risk_Agent | `impact-action-analyst`（施可行，机会风险与落地顾问） |
| Reasoning_Agent | `logic-scenario-analyst`（秦溯因，政策逻辑与情景推演官） |
| JSON_Validator_Agent | `report-contract-validator`（祁核真，报告契约审校官） |
| 5 套 schema | `skills/policy-research-contracts/references/`（修复 evidence_quote 冲突并扩展字段） |
| 自定义 manifest / UI 组件 | 标准 `plugin.json` + `settings.json`；原配置全文留档于 `source-manifest.md` |

完整解析与逐字段去向见 `skills/policy-research-contracts/references/source-manifest.md`。

## 保留的硬约束

- 公司输入必须联网核验工商登记，以注册地省/市为主区域；行业输入主区域为全国。
- 全国 + 主区域双轨检索官方发文详情页，全国高相关政策 ≥10 条。
- A 组（直接适用）/ B 组（间接参考）分级；B 组引用 ≤20%，只作趋势参考。
- 机会风险 ≥8 条、覆盖 ≥60% 赛道；每条关键政策恰好 L1-L6 六层逻辑链。
- 契约不通过一律驳回重做，主理人与校验官均不得自行修补或编造。
- 最终 JSON 的 `meta` 写明主区域/扩展区域，并提示复制生成 H5 报告。

## 新增研究能力

1. **政策沿革与版本比对**：发布—修订—废止—接力时间轴、版本变化要点、连续性/转向信号。
2. **区域横向对比矩阵**：支持力度、门槛、补贴额度、覆盖赛道、生效时序、申报窗口，逐格绑定政策 id 与官方链接。
3. **量化影响评估**：指标口径字典 + 官方数值锚点 + 三情景测算 + 敏感性，假设必须显式标注。
4. **申报落地行动清单**：条件、材料、责任部门、时间窗口、状态与前置依赖。

字段定义与可追溯规则见 `skills/policy-research-contracts/references/research-extensions.md`。

## 目录结构

```
policy-research/
├── .codebuddy-plugin/plugin.json        专家卡片与团队声明
├── settings.json                        主 Agent 指向主理人
├── agents/                              主理人 SOP + 5 名团员定义
├── skills/policy-research-contracts/
│   ├── SKILL.md                         契约体系与驳回规则
│   ├── references/                      5 套 schema + 源包解析 + 扩展契约
│   ├── templates/                       报告大纲 + final_report 骨架
│   └── examples/minimal-input.json
├── skills/policy-report-h5/
│   ├── SKILL.md                         H5 渲染触发说明
│   └── scripts/render_h5.py             纯标准库渲染器（final_report.json → H5）
└── avatars/                             团队 + 6 名角色头像
```

## 使用示例

- 帮我研究【公司或行业】适用的全国与主区域政策，输出完整政策研究报告
- 梳理【某政策/某赛道】近五年的政策沿革与版本变化，并做区域横向对比
- 量化评估【某政策】对我司的影响，给出申报条件、时间节点与落地行动清单
- 也看看【某省/市】的政策（区域扩展：复用国家级政策，追加 `regions.additional`）

## 头像（待手动补充）

本次未生成头像文件（图片生成会额外消耗积分，按你的选择跳过）。头像缺失不影响专家注册与使用，但建议补齐 7 张：

- `team.png`、`policy-research-team-lead.png`、`scope-metrics-analyst.png`、`policy-evidence-scanner.png`、`impact-action-analyst.png`、`logic-scenario-analyst.png`、`report-contract-validator.png`
- 规格：PNG/JPG、512×512、单张 ≤500KB，文件名须与 `plugin.json` 中声明一致
- 统一「深青＋银灰」风格锚定词与逐张生成提示词见 `avatars/AVATAR_PROMPTS.md`

## 安装与注册

专家目录：`%WORKBUDDY_CONFIG_DIR%/plugins/marketplaces/my-experts/plugins/policy-research/`

```bash
python3 scripts/validate_expert.py <expert-dir>
python3 scripts/register_expert.py <expert-dir>
python3 scripts/package_expert.py <expert-dir> [output-dir]
```

注册后在【专家中心 → 我的专家】可见。打包生成的 zip 可用于分享。
