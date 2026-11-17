# 头像生成提示词（手动补充用）

本次专家包未自动生成头像（图片生成会额外消耗积分）。需要补齐时，按下面 7 条 prompt 逐张生成到本目录，再重命名即可。

- **尺寸**：1024×1024 生成（市场展示缩放为 512×512）；**格式** PNG/JPG；**单张 ≤500KB**
- **风格锚定前缀（每张都必须一致）**：`Professional cartoon-style illustration avatar, consistent art style with warm lighting and soft shadows,`
- **风格锚定后缀（个人头像）**：`Bust shot, facing forward. Clean simple deep teal with silver accent toned background. High quality, professional, natural.`
- **团队头像后缀**：`Clean simple deep teal with silver accent toned background. High quality, professional, team composition.`
- 色调依据 `categoryId: 12-IndustryConsultant` → deep teal with silver accent

| 目标文件名 | 角色 |
|-----------|------|
| team.png | 政研智库团整体协作场景 |
| policy-research-team-lead.png | 谭策衡 · 首席政策研究官 |
| scope-metrics-analyst.png | 解界明 · 研究范围与口径官 |
| policy-evidence-scanner.png | 查文渊 · 政策证据与沿革研究员 |
| impact-action-analyst.png | 施可行 · 机会风险与落地顾问 |
| logic-scenario-analyst.png | 秦溯因 · 政策逻辑与情景推演官 |
| report-contract-validator.png | 祁核真 · 报告契约审校官 |

---

## 1. team.png

```
Professional cartoon-style illustration, consistent art style with warm lighting and soft shadows, a dynamic policy research think tank team scene, six diverse analysts gathered around a central holographic display showing official policy documents, a regional comparison matrix, a six-layer transmission chain and three scenario curves, documents tagged A and B floating in organized evidence folders, collaborative and rigorous research atmosphere, subtle government building silhouettes and document stamps in background. Clean simple deep teal with silver accent toned background. High quality, professional, team composition.
```

## 2. policy-research-team-lead.png

```
Professional cartoon-style illustration avatar, consistent art style with warm lighting and soft shadows, a male chief policy research officer named Tan, calm authoritative expression, wearing a well-tailored dark suit, holding a bound research briefing folder, subtle background of a five-stage research pipeline diagram, official document seals and a balance scale symbolizing evidence judgment. Bust shot, facing forward. Clean simple deep teal with silver accent toned background. High quality, professional, natural.
```

## 3. scope-metrics-analyst.png

```
Professional cartoon-style illustration avatar, consistent art style with warm lighting and soft shadows, a female research scope and metrics analyst named Xie, wearing stylish glasses and smart casual attire, holding a company registration dossier and a segment boundary map, meticulous and precise expression, subtle background of a magnifying glass, industry segment boundaries, keyword tags and a metrics dictionary table. Bust shot, facing forward. Clean simple deep teal with silver accent toned background. High quality, professional, natural.
```

## 4. policy-evidence-scanner.png

```
Professional cartoon-style illustration avatar, consistent art style with warm lighting and soft shadows, a male policy evidence and evolution researcher named Zha, wearing a shirt and vest, holding an official policy document with a visible seal, focused and skeptical expression, subtle background of stacked official files, a policy timeline with version arrows, a regional map grid and a magnifying glass. Bust shot, facing forward. Clean simple deep teal with silver accent toned background. High quality, professional, natural.
```

## 5. impact-action-analyst.png

```
Professional cartoon-style illustration avatar, consistent art style with warm lighting and soft shadows, a female opportunity, risk and action advisor named Shi, wearing a crisp blazer, holding a clipboard with a checked action list, decisive and practical expression, subtle background of an opportunity-risk balance scale, a calendar with deadline markers, application forms and checklist ticks. Bust shot, facing forward. Clean simple deep teal with silver accent toned background. High quality, professional, natural.
```

## 6. logic-scenario-analyst.png

```
Professional cartoon-style illustration avatar, consistent art style with warm lighting and soft shadows, a male policy logic and scenario analyst named Qin, wearing a slim turtleneck and jacket, thoughtful analytical expression, one hand tracing a chain diagram, subtle background of six connected transmission layers, three diverging scenario curves and quantitative impact charts. Bust shot, facing forward. Clean simple deep teal with silver accent toned background. High quality, professional, natural.
```

## 7. report-contract-validator.png

```
Professional cartoon-style illustration avatar, consistent art style with warm lighting and soft shadows, a female report contract auditor named Qi, wearing neat glasses and a tailored jacket, holding an audit checklist, rigorous and uncompromising expression, subtle background of JSON schema cards, pass and fail check marks, a magnifying glass over structured data fields. Bust shot, facing forward. Clean simple deep teal with silver accent toned background. High quality, professional, natural.
```

---

生成后把文件重命名为上表目标文件名，重新运行 `register_expert.py` 即可（头像变更不需要改 `plugin.json`）。
