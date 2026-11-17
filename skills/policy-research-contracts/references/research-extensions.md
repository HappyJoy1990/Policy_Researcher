# 研究能力扩展契约（政策采集 → 政策研究）

四项新增能力均以**可选扩展字段**挂载在原有五套 Schema 上，不破坏原必填字段；但一旦输出，必须满足下列可追溯规则，否则由 `report-contract-validator` 驳回。

## 1. 政策沿革与版本比对

**挂载位置**：`policy.schema.json` → 单条政策 `lineage`；`final_report.schema.json` → 顶层 `policy_evolution`。

| 字段 | 含义 | 硬规则 |
|------|------|--------|
| version | 版本号 / 文号 / 修订批次 | 必须来自官方详情页 |
| supersedes[] | 本文件替代的既有政策 id 或文件名 | 引用必须存在于 policies，或注明「未纳入本次检索」 |
| superseded_by | 被哪个后续文件替代 | 无则填 null，不得猜测 |
| change_note | 相对上一版的关键变化（支持力度、门槛、覆盖范围、时限） | 逐条给 `evidence_quote` |
| continuity_signal | 连续性 / 转向判断 | 必须区分「已核实事实」与「研判结论」 |
| source_urls[] | 历史版本与现行版本官方链接 | 至少一个可访问的官方详情页 |

时间窗默认近五年（由 `scope.time_window` 定义），用户另有要求从其要求。输出 `policy_evolution` 时按时间轴排列，标注政策接力与空档期。

## 2. 区域横向对比矩阵

**挂载位置**：Phase 2 输出的 `regional_comparison`；`final_report.schema.json` → 顶层 `regional_comparison`。

| 字段 | 含义 | 硬规则 |
|------|------|--------|
| dimension | 对比维度：支持力度 / 适用门槛 / 补贴额度 / 覆盖赛道 / 生效时序 / 申报窗口 | 维度名称统一，便于成表 |
| regions[].region | 区域名 | 必须包含 `regions.primary`；扩展区域来自 `regions.additional` |
| regions[].value | 该维度取值 | 数值必须来自 `quantitative_anchors`，定性描述必须给原文引用 |
| regions[].policy_ids[] | 依据政策 id | 必须存在于 policies |
| regions[].source_url | 官方详情页 | 无核实文件时写「该区域暂无经核实的地方文件」，不得留空或用其他地区数据填充 |

比较时须区分 A 组（主区域/国家级）与 B 组（其他省市），B 组只作趋势参考并注明来源省市。

## 3. 量化影响评估

**输入**：`scope.metrics_dictionary`（口径） + `policy.quantitative_anchors`（官方数值锚点）。
**挂载位置**：`reasoning.schema.json` → `quantitative_impact`、`sensitivity`；`final_report.schema.json` → 顶层 `quantitative_impact`。

| 字段 | 含义 | 硬规则 |
|------|------|--------|
| metric | 指标名 | 必须出现在 `metrics_dictionary` |
| formula | 计算式 | 写明分子/分母与单位换算 |
| baseline / optimistic / base / pessimistic | 基准与三情景取值 | 三情景须与 `scenarios` 的触发条件一致 |
| anchor_policy_ids[] | 数值来源政策 id | 必须存在于 policies，且该政策有对应 `quantitative_anchors` |
| assumption_flag | 是否含假设 | true 时必须在 `note` 中写明假设内容、来源类型与敏感性区间 |
| sensitivity[] | 关键变量变动区间与影响 | 至少覆盖一个对结果影响最大的变量 |

**红线**：禁止编造行业规模、企业营收、补贴兑现率等外部数据；无法从官方原文推出的数值一律标注为假设，不得伪装成事实。B 组政策数值不得作为主测算依据。

## 4. 申报落地行动清单

**挂载位置**：`opportunity_risk.schema.json` → `action_items`；`final_report.schema.json` → 顶层 `action_items`。

| 字段 | 含义 | 硬规则 |
|------|------|--------|
| related_policy_ids[] | 依据政策 id | 必须为 A 组（直接适用）政策 |
| action | 具体动作 | 动宾结构、可执行 |
| eligibility[] | 申报条件 | 逐条来自官方原文 |
| required_documents[] | 材料清单 | 原文未载明时写「待核实：官方原文未载明」 |
| responsible_body | 责任部门 | 必须是发文或受理部门；无出处写「待核实」 |
| window | 开放 / 截止 / 说明 | 日期来自官方原文；无明确窗口写「待核实」 |
| status | 可立即启动 / 待条件成熟 / 待核实 | 裁决明确，不得回避 |
| prerequisites[] | 前置依赖 | 如资质、立项、配套细则 |

## 5. 校验清单（report-contract-validator 必查）

- [ ] `lineage` 的版本链引用闭合，`source_urls` 为官方详情页
- [ ] `regional_comparison` 每格含 policy_ids 与 source_url，含 primary 区域
- [ ] `quantitative_impact` 每个指标有口径、锚点政策 id 或显式假设标记
- [ ] `sensitivity` 覆盖至少一个关键变量
- [ ] `action_items` 每条有责任部门与时间节点（或显式「待核实」）
- [ ] 所有新增字段未破坏原有 A/B 比例、六层链、覆盖率和条数约束
