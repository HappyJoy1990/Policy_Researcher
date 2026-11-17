---
name: policy-report-h5
description: "Render a contract-validated final_report.json into a single-file, offline-readable interactive H5 policy report. Load at the delivery stage after the final report JSON is produced, to give the user a ready-to-view HTML report instead of raw JSON."
---

# H5 政策报告渲染器

本 Skill 把「政研智库团」流水线产出的 `final_report.json` 渲染为**单文件、离线可读的可交互 H5 报告页**。它只做展示层搬运，不新增任何分析结论、政策条款或数值。

## 何时使用

仅在主理人完成 Phase 6 汇编、拿到通过契约校验的 `final_report.json` 之后使用。在此之前（收集证据、推理、校验阶段）不要调用。

## 如何使用

1. 把 Phase 6 产出的完整 `final_report.json` 保存到本地文件（例如工作目录下的 `final_report.json`）。
2. 运行渲染脚本（纯 Python 标准库，无需安装依赖）：

```bash
python <本skill目录>/scripts/render_h5.py <final_report.json 路径> [输出 html 路径]
```

- 第一个参数：final_report.json 路径（必填）。
- 第二个参数：输出 html 路径（可选，省略则输出到 json 同目录的 `report.html`）。
- 成功时终端打印 `H5_REPORT_OK` 和 `OUTPUT=<html路径>`。

3. 用 present_files 把生成的 html 展示给用户预览，并在回复里给出文件路径。

## 依赖与约束

- 脚本仅依赖 Python 标准库（json / io / os / html / re / sys / argparse），任何 Python 3 环境均可运行。
- 输入必须是符合 `final_report.schema.json` 的 JSON；字段缺失时渲染器按内置降级规则显示，不会编造内容。
- 渲染器不会修改、补充或"修正"报告中的任何事实或数值。数据准确性由前序 Phase 0-5 的联网检索与契约校验保证。
- 报告含 16 节标准版式（执行摘要、政策全景、沿革、六层传导链、机会风险、量化、行动清单、证据附录等），并自带 A/B 证据分级与来源徽章。

## 常见问题

- **用户只看数据、不需要 H5**：可跳过本 Skill，直接交付 JSON + 文字报告。
- **渲染报错**：先确认 JSON 能被 `json.load` 解析、编码为 UTF-8；确认输出目录可写。
- **中文乱码**：用 UTF-8 保存 JSON；生成的 html 本身是 UTF-8，浏览器会自动识别。
