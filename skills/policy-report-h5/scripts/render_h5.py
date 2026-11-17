# -*- coding: utf-8 -*-
"""通用 H5 政策报告渲染器：把 final_report.json 渲染为单文件、离线可读的交互报告页。
只做展示层搬运，不新增任何分析结论。

章节结构：section_layout_contract v3（2026-11-16）——16 节 + s1/s5/s8/s11 四条 patch：
  s1  执行摘要（指标卡不含内部质控分；关键判断强制来源徽章）
  s2  研究范围与主体核验（阶段一·上）
  s3  赛道拆分与研究问题（阶段一·下）
  s4  政策全景与 A/B 证据（阶段二·上）
  s5  政策解读与拆解（阶段二·下；多流派四卡 + 多流派分析结论）
  s6  政策沿革与版本比对（阶段二·沿革）
  s7  六层传导链与情景推演（阶段三）
  s8  机会与风险清单（阶段四·上；矩阵 + 行动交叉链接 + 干系人矩阵）
  s9  财务影响速览（阶段四·下；三情景量化 M4）
  s10 申报条件与免责声明（阶段五·上；免责声明去重）
  s11 申报落地行动清单（阶段五·下；时间轴路线图 + 双向链接）
  s12 关键不确定性与监测信号
  s13 反向盲算与契约校验
  s14 质量控制与局限（完整度等内部质控分只在此节出现）
  s15 证据附录与来源
  s16 报告使用须知
所有规则只「摆放已有字段」；所需字段缺失时按各 patch 的 fallback 执行，不编造数据。
"""
import json, io, os, html, re

CSS = """
:root{--bg:#f4f6f9;--card:#fff;--ink:#1b2531;--muted:#5d6a7a;--line:#e2e8f0;
--primary:#1f4e79;--primary2:#2f6fb0;--soft:#eef3f9;--accent:#b3402f;--teal:#0f766e;--gold:#a9740b;--violet:#5b4b9e}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
a{color:var(--primary2);text-decoration:none}a:hover{text-decoration:underline}
.app{display:flex}
.side{width:236px;position:fixed;top:0;left:0;height:100vh;overflow:auto;background:#fff;border-right:1px solid var(--line);padding:20px 13px;z-index:5}
.side .brand{font-size:11px;letter-spacing:.14em;color:var(--muted);font-weight:700}
.side h1{font-size:16px;color:var(--primary);margin:6px 0 12px;line-height:1.45}
.side nav a{display:block;padding:6px 9px;border-radius:6px;color:var(--muted);font-size:12.6px;border-left:3px solid transparent}
.side nav a:hover,.side nav a.active{background:var(--soft);color:var(--primary);text-decoration:none}
.side nav a.active{border-left-color:var(--primary2);font-weight:700}
.side .foot{margin-top:16px;padding-top:12px;border-top:1px solid var(--line);font-size:11px;color:#8b97a6}
.main{margin-left:236px;padding:0 36px 80px;width:calc(100% - 236px);max-width:1480px}
.hero{background:linear-gradient(120deg,#eaf1f9,#f7fafc 55%,#eef6f4);border:1px solid var(--line);border-radius:15px;padding:34px 38px;margin:26px 0 22px}
.hero .eyebrow{font-size:11.5px;letter-spacing:.18em;color:var(--primary2);font-weight:700}
.hero h2{font-size:29px;color:#153b60;margin:8px 0 10px;line-height:1.35}
.hero .lead{color:#42556b;margin:0 0 16px;max-width:800px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{background:rgba(255,255,255,.85);border:1px solid #d5e0ec;border-radius:999px;padding:5px 12px;font-size:11.8px;color:var(--primary);font-weight:600}
.chip.ok{background:#e9f5f1;border-color:#c7e5dc;color:var(--teal)}
.chip.warn{background:#fdf5e6;border-color:#eddcba;color:var(--gold)}
.demo-banner{background:#fdf3e3;border:1px solid #e9cf9e;color:#7a5a18;border-radius:10px;padding:13px 16px;margin-bottom:18px;font-weight:600}
.legend{display:flex;flex-wrap:wrap;gap:12px;background:#fff;border:1px solid var(--line);border-radius:9px;padding:11px 15px;font-size:12px;color:var(--muted);margin-bottom:22px}
.legend i{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px}
section{margin-bottom:38px;scroll-margin-top:18px}
.sec-head{display:flex;align-items:baseline;gap:11px;border-bottom:2px solid var(--line);padding-bottom:8px;margin-bottom:16px}
.sec-head .num{background:var(--primary);color:#fff;border-radius:6px;padding:2px 8px;font-size:11.5px;font-weight:800}
.sec-head h3{margin:0;font-size:19px;color:#153b60}
.sec-head .hint{margin-left:auto;font-size:11.8px;color:var(--muted)}
h4{font-size:14.5px;color:var(--primary);border-left:3px solid var(--primary2);padding-left:9px;margin:22px 0 10px}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:15px 17px;margin-bottom:12px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.small{font-size:12.5px}.xsmall{font-size:11.5px}.muted{color:var(--muted)}
.mono{font-family:ui-monospace,Consolas,monospace;font-size:11.4px}
.tag{display:inline-block;background:var(--soft);color:var(--primary);border:1px solid #dce6f1;border-radius:5px;padding:1px 7px;font-size:11px;margin:0 4px 4px 0}
.tag.a{background:#e9f1fb}.tag.b{background:#f2f3f5;color:#6b7380;border-color:#e0e3e8}
.tag.opp{background:#e9f5f1;color:var(--teal);border-color:#c9e7dd}
.tag.risk{background:#fbeceb;color:var(--accent);border-color:#f0d2ce}
.tag.gold{background:#fdf5e6;color:var(--gold);border-color:#ecd9b4}
.tag.violet{background:#f0eef9;color:var(--violet);border-color:#ddd7f0}
.tag.gray{background:#f3f5f7;color:#5d6a7a;border-color:#e2e8ee}
table{width:100%;border-collapse:collapse;font-size:12.4px;background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden}
th{background:#eef3f9;color:var(--primary);text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:8px 10px;border-bottom:1px solid #eef1f5;vertical-align:top}
tr:last-child td{border-bottom:none}
.scroll{overflow-x:auto}
details{background:#fff;border:1px solid var(--line);border-radius:8px;margin-bottom:8px}
details[open] summary{background:#fbfcfe;border-bottom:1px solid var(--line)}
summary{cursor:pointer;padding:10px 13px;font-size:12.9px;font-weight:600;list-style:none;display:flex;gap:8px;align-items:flex-start}
summary::-webkit-details-marker{display:none}
summary:before{content:"▸";color:var(--primary2);flex:none}
details[open] summary:before{content:"▾"}
.dbody{padding:12px 15px 15px;font-size:12.6px}
.kv{display:grid;grid-template-columns:104px 1fr;gap:4px 10px;font-size:12.4px;margin-bottom:8px}
.kv .k{color:var(--muted)}
.quote{background:#f7f9fc;border-left:3px solid #b9cde2;padding:8px 11px;border-radius:0 6px 6px 0;font-size:12.3px;margin:8px 0;color:#364859}
.notice{background:#fdf8ec;border:1px solid #eddcba;border-radius:8px;padding:11px 14px;color:#6c551f;font-size:12.4px;margin-bottom:12px}
.okbox{background:#eaf6f2;border:1px solid #c9e7dd;border-radius:8px;padding:11px 14px;color:#0f5d55;font-size:12.4px;margin-bottom:12px}
.controls{display:flex;flex-wrap:wrap;gap:9px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:9px;padding:10px 13px;margin-bottom:12px}
input,select{border:1px solid #d9e1ea;border-radius:6px;padding:6px 9px;font-size:12.4px;font-family:inherit;color:var(--ink);background:#fff}
.btn{border:1px solid #d9e1ea;background:#fff;color:var(--primary);border-radius:6px;padding:6px 12px;font-size:12.3px;cursor:pointer;font-family:inherit}
.btn:hover{background:var(--soft)}
.count{margin-left:auto;font-size:12px;color:var(--muted)}
.layer{padding:9px 11px;border-left:2px solid #dbe5f0;margin-left:8px}
.layer .lb{display:inline-block;background:var(--primary);color:#fff;border-radius:4px;padding:1px 6px;font-size:10.5px;font-weight:700;margin-right:6px}
.layer .nm{font-size:11px;color:var(--muted);font-family:ui-monospace,Consolas,monospace}
.layer .st{margin-top:5px;font-size:12.5px}
.trans{font-size:11.7px;color:var(--violet);background:#f6f4fc;border:1px dashed #ddd7f0;border-radius:6px;padding:5px 9px;margin:6px 0 6px 22px}
.footer{text-align:center;color:#8b97a6;font-size:11.4px;border-top:1px solid var(--line);padding-top:20px;margin-top:32px}
@media(max-width:900px){.side{position:static;width:100%;height:auto;border-right:none;border-bottom:1px solid var(--line)}.side nav{display:flex;flex-wrap:wrap}.side .foot{display:none}.app{display:block}.main{margin-left:0;width:100%;padding:0 15px 60px}.hero{padding:22px 18px}.hero h2{font-size:22px}}
/* ---------- 收敛层：每节一个主视觉，其余折叠 ---------- */
.lead-card{background:#fff;border:1px solid var(--line);border-left:4px solid var(--primary);
  border-radius:10px;padding:15px 18px;margin-bottom:14px;font-size:13.4px;line-height:1.85;color:#22303f}
.lead-card p{margin:0 0 8px}.lead-card p:last-child{margin:0}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.stat{background:#fff;border:1px solid var(--line);border-radius:8px;padding:6px 12px;font-size:12.2px;color:var(--muted)}
.stat b{color:var(--primary);font-size:15px;margin-right:3px}
.stat.a{border-color:#cfe0f3;background:#f2f7fd}.stat.a b{color:var(--primary2)}
.stat.b{border-color:#e0e3e8;background:#f6f7f9}.stat.b b{color:#6b7380}
.pri{display:inline-block;background:#fbeceb;color:var(--accent);border:1px solid #f0d2ce;
  border-radius:999px;padding:1px 9px;font-size:10.8px;font-weight:700}
.secnote{font-size:12.2px;color:var(--muted);margin:-4px 0 12px}
/* ---------- s1 客观指标卡与来源徽章（契约 v3 patch-1） ---------- */
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}
.metric{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 15px}
.metric .v{font-size:24px;font-weight:800;color:var(--primary);font-variant-numeric:tabular-nums}
.metric .l{font-size:11.5px;color:var(--muted);margin-top:2px}
.kj{padding:7px 0;border-bottom:1px dashed var(--line)}
.cite{display:inline-block;background:#e9f1fb;color:#1f4e79;border:1px solid #cfe0f3;border-radius:4px;
  padding:0 6px;font-family:ui-monospace,Consolas,monospace;font-size:10.8px;font-weight:600;margin:0 3px;vertical-align:1px}
.cite.missing{background:#fdf3e3;color:#8a5a00;border-color:#e9cf9e}
/* ---------- s5 多流派卡片与结论条（契约 v3 patch-2） ---------- */
.ms-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-bottom:12px}
.ms-card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.ms-card .h{display:flex;align-items:center;gap:8px;font-weight:700;color:var(--primary);margin-bottom:8px}
.ms-card .h i{width:9px;height:9px;border-radius:3px;background:var(--primary2);flex:none}
.ms-concl{background:#eaf6f2;border:1px solid #c9e7dd;border-radius:8px;padding:12px 15px;color:#0f5d55;
  font-size:12.5px;margin:12px 0}
.ms-concl .tt{font-weight:800}
.ms-concl.fallback{background:#fdf8ec;border-color:#eddcba;color:#6c551f}
.ms-concl .row{margin-top:4px}
/* ---------- s6 政策沿革时间线 ---------- */
.lin-card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:12px}
.lin-head{display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin-bottom:8px}
.lin-tl{display:flex;flex-wrap:wrap;align-items:stretch;gap:0;margin:10px 0}
.lin-ver{flex:1 1 180px;min-width:170px;position:relative;padding:8px 12px 8px 26px;border-left:2px solid #c3d4e6}
.lin-ver:before{content:"";position:absolute;left:-6px;top:14px;width:10px;height:10px;border-radius:50%;
  background:#fff;border:3px solid var(--primary2)}
.lin-ver .d{font-size:11.3px;color:var(--muted);font-family:ui-monospace,Consolas,monospace}
.lin-ver .t{font-size:12.6px;font-weight:600;color:var(--ink);margin:2px 0}
.lin-arrow{display:flex;align-items:center;padding:0 4px;color:var(--primary2);font-weight:800}
/* ---------- s8 矩阵与行动交叉链接（契约 v3 patch-3） ---------- */
.mx{display:grid;grid-template-columns:110px repeat(3,1fr);gap:6px;margin:12px 0}
.mx .hd{background:#eef3f9;border:1px solid var(--line);border-radius:7px;padding:6px 9px;
  font-size:11.8px;font-weight:700;color:var(--primary);text-align:center}
.mx .hd.rowhd{display:flex;align-items:center;justify-content:center}
.mx-cell{background:#fff;border:1px solid var(--line);border-radius:7px;padding:7px 9px;min-height:56px}
.mx-cell.empty{background:#fafbfd;color:#a9b3c0;display:flex;align-items:center;justify-content:center;font-size:11.5px}
.mx-item{display:flex;flex-wrap:wrap;align-items:center;gap:5px;padding:3px 0;border-bottom:1px dashed #eef1f5;font-size:11.8px}
.mx-item:last-child{border-bottom:none}
.alink{background:#e9f1fb;border:1px solid #cfe0f3;color:#1f4e79;border-radius:5px;
  padding:0 6px;font-size:10.8px;font-weight:700;font-family:ui-monospace,Consolas,monospace;white-space:nowrap}
.alink:hover{background:#dfeaf6;text-decoration:none}
.noact{background:#fdf3e3;border:1px solid #e9cf9e;color:#8a5a00;border-radius:5px;
  padding:0 6px;font-size:10.6px;font-weight:700;white-space:nowrap}
.orref{display:flex;flex-wrap:wrap;align-items:center;gap:5px;margin-top:7px;padding-top:7px;
  border-top:1px dashed var(--line);font-size:11.6px}
/* ---------- s11 行动路线图（契约 v3 patch-4） ---------- */
.roadmap{position:relative;margin:14px 0}
.roadmap .track{position:absolute;left:0;right:0;top:15px;height:3px;background:linear-gradient(90deg,#b3402f,#2f6fb0,#0f766e);border-radius:2px;opacity:.75}
.phase{margin-bottom:20px;position:relative}
.phase-head{display:flex;align-items:center;gap:10px;margin-bottom:10px;position:relative;z-index:2}
.phase-head .dot{width:13px;height:13px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 0 2px currentColor;flex:none;background:currentColor}
.phase-head .pt{font-weight:800;font-size:13.5px;color:var(--ink)}
.phase-head .pd{font-size:11.6px;color:var(--muted)}
.phase.now .dot{color:#b3402f}.phase.mid .dot{color:#2f6fb0}.phase.long .dot{color:#0f766e}
.act-card{background:#fff;border:1px solid var(--line);border-left:4px solid #2f6fb0;border-radius:9px;padding:11px 14px;margin-bottom:10px}
.act-card.pri-high{border-left-color:#b3402f}
.act-card .hd{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.act-card .nm{font-weight:700;font-size:13px;color:var(--ink)}
.act-card .row{margin-top:6px;font-size:12px}
.act-card .pri{background:#fbeceb;color:var(--accent);border:1px solid #f0d2ce;border-radius:999px;padding:1px 9px;font-size:10.8px;font-weight:700}
.act-card .pri.mid{background:#e9f1fb;color:#1f4e79;border-color:#cfe0f3}
@media(max-width:900px){.roadmap .track{left:8px;right:auto;top:0;bottom:0;width:3px;height:auto;background:linear-gradient(180deg,#b3402f,#2f6fb0,#0f766e)}
.roadmap{padding-left:22px}.phase-head .dot{margin-left:-22px}}
/* ---------- 三情景量化指标：结论与证明过程分层（既有契约） ---------- */
.qi-note{background:#f7f9fc;border:1px solid var(--line);border-radius:9px;padding:10px 14px;
  font-size:12.2px;color:var(--muted);line-height:1.75;margin:0 0 12px}
.qi-legend{display:flex;flex-wrap:wrap;gap:16px;background:#fff;border:1px solid var(--line);
  border-radius:9px;padding:10px 14px;font-size:12px;color:var(--muted);margin-bottom:14px}
.qi-legend i{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:6px;vertical-align:middle}
.qi-list{margin-bottom:16px}
.qi-card{background:#fff;border:1px solid var(--line);border-radius:11px;
  box-shadow:0 1px 3px rgba(28,45,70,.07);margin-bottom:13px;overflow:hidden}
.qi-head{padding:14px 17px 11px}
.qi-title{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.qi-rank{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;flex:none;
  background:var(--primary);color:#fff;border-radius:6px;font-size:11px;font-weight:800}
.qi-name{font-size:14px;font-weight:700;color:var(--primary)}
.qi-type,.qi-badge{font-size:11px;border-radius:999px;padding:2px 9px;font-weight:600;white-space:nowrap}
.qi-type.delta{background:#e9f1fb;border:1px solid #cfe0f3;color:#1f4e79}
.qi-type.level{background:#f0eef9;border:1px solid #ddd7f0;color:var(--violet)}
.qi-badge.assume{background:#fdf5e6;border:1px solid #ecd9b4;color:var(--gold)}
.qi-badge.official{background:#e9f5f1;border:1px solid #c9e7dd;color:var(--teal)}
.qi-vals{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.qi-val{flex:1 1 132px;min-width:128px;background:#f8fafc;border:1px solid var(--line);border-radius:8px;padding:8px 12px}
.qi-val .lb{font-size:11px;color:var(--muted)}
.qi-val .n{font-size:19px;font-weight:800;line-height:1.35;font-variant-numeric:tabular-nums;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.qi-val.opt .n{color:var(--primary2)}
.qi-val.base .n{color:#5d6a7a}
.qi-val.pes .n{color:var(--accent)}
.qi-chart{padding:0 17px 8px}
.qi-chart svg{display:block;width:100%;height:auto}
.qi-caption{font-size:11.2px;color:#8b97a6;line-height:1.65;margin:2px 0 0}
.qi-details{border-top:1px solid var(--line)}
.qi-details>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:8px;
  padding:9px 17px;font-size:12.3px;color:var(--primary);font-weight:600;background:#fbfcfe}
.qi-details>summary::-webkit-details-marker{display:none}
.qi-details>summary:hover{background:var(--soft)}
.qi-details .arw{display:inline-block;color:var(--primary2);font-size:12px;
  transition:transform .22s ease;transform-origin:50% 50%}
.qi-details[open] .arw{transform:rotate(90deg)}
.qi-body{border-top:1px solid var(--line);padding:11px 17px 15px;font-size:12px;
  color:var(--muted);line-height:1.75}
.qi-body p{margin:0 0 9px}
.qi-body .lb{font-weight:700;color:var(--ink);font-size:12px}
.qi-chips{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:4px}
.qi-chips .lb{font-weight:700;color:var(--ink);font-size:12px;margin-right:4px}
.qchip{position:relative;display:inline-block;background:#eef3f9;border:1px solid #d5e0ec;
  color:var(--primary);border-radius:999px;padding:2px 10px;font-size:11.4px;font-weight:600;
  cursor:help;outline:none}
.qchip:hover,.qchip:focus{background:#dfeaf6;border-color:#b9cde2}
.qchip:hover::after,.qchip:focus::after{content:attr(data-tip);position:absolute;left:0;
  top:calc(100% + 8px);z-index:25;width:300px;max-width:80vw;background:#1b2531;color:#fff;
  border-radius:7px;padding:9px 11px;font-size:11.4px;font-weight:400;line-height:1.65;
  white-space:normal;box-shadow:0 6px 20px rgba(20,35,55,.22);pointer-events:none}
.qi-basis{font-size:11.3px;color:#8b97a6;margin-top:8px;word-break:break-all}
/* =====================================================================
   v4 视觉系统（对齐用户确认过的能源行业 demo）：暖白极简、单栏聚焦、
   每节「阶段眉标 → 标题 → 核心结论条 → 一个主组件 → 明细折叠」
   —— 只覆盖样式，不改任何渲染逻辑与数据。
   ===================================================================== */
:root{
  --bg:#faf8f3;--card:#fff;--ink:#1e1d1a;--muted:#6f6a61;--line:#e8e4da;
  --primary:#2c5f46;--primary2:#3f7d5c;--soft:#f2efe7;
  --accent:#a9422f;--teal:#2f6f57;--gold:#9a6b12;--violet:#5b4b8e;
  --mint:#eef5ef;--mintline:#cfe3d4;--cream:#fdf6e8;--creamline:#ecdcb8;
  --blush:#fbeeec;--blushline:#f0d5d0;
}
body{background:var(--bg);color:var(--ink);font-size:14.5px;line-height:1.85;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
a{color:#2f6f57}
/* 侧栏：更轻、更少存在感 */
.side{width:248px;background:#f7f4ed;border-right:1px solid var(--line);padding:26px 16px}
.side .brand{font-size:10.5px;letter-spacing:.16em;color:#a09889}
.side h1{font-size:17px;color:var(--ink);font-weight:700;margin:8px 0 14px}
.side nav a{padding:7px 10px;font-size:12.6px;border-left:2px solid transparent;border-radius:0;color:#6f6a61}
.side nav a:hover{background:#efebe1;color:var(--ink);text-decoration:none}
.side nav a.active{background:#fff;color:var(--primary);border-left-color:var(--primary2);font-weight:700}
.side .foot{border-top:1px solid var(--line);font-size:10.5px;color:#a09889;line-height:1.7}
/* 正文单栏：内容宽度收敛，避免长行与横向漂移 */
.main{margin-left:248px;width:calc(100% - 248px);max-width:1080px;padding:0 40px 110px}
/* 封面 */
.hero{background:#fff;border:1px solid var(--line);border-radius:16px;padding:34px 36px;margin:32px 0 22px}
.hero .eyebrow{font-size:11px;letter-spacing:.2em;color:#a09889;font-weight:700}
.hero h2{font-size:30px;line-height:1.32;color:var(--ink);font-weight:700;margin:10px 0 12px;letter-spacing:-.01em}
.hero .lead{font-size:14px;color:#5c574e;max-width:760px;margin:0 0 20px;line-height:1.85}
.chip{background:#f7f4ed;border:1px solid var(--line);color:#5c574e;font-weight:600;font-size:11.8px;padding:4px 12px}
.chip.ok{background:var(--mint);border-color:var(--mintline);color:var(--primary)}
.chip.warn{background:var(--cream);border-color:var(--creamline);color:var(--gold)}
.demo-banner{background:var(--cream);border:1px solid var(--creamline);color:#7b5c16;border-radius:10px;
  padding:12px 16px;font-size:12.6px;font-weight:400;line-height:1.8;margin-bottom:18px}
.legend{background:transparent;border:none;padding:0 2px;margin-bottom:30px;gap:18px}
.legend span{font-size:11.6px;color:#8b8577}
.legend i{width:7px;height:7px;border-radius:50%;margin-right:6px}
/* 节：眉标 + 大标题 + 细横线 */
section{margin-bottom:52px;scroll-margin-top:28px}
.sec-head{display:block;border-bottom:1px solid var(--line);padding-bottom:13px;margin-bottom:20px}
.sec-head .eb{display:flex;align-items:center;gap:7px;font-size:11.6px;color:#8b8577;letter-spacing:.04em;margin-bottom:5px}
.sec-head .eb i{width:6px;height:6px;border-radius:50%;background:#4c8b68;flex:none}
.sec-head h3{display:flex;align-items:baseline;gap:12px;font-size:21px;font-weight:700;color:var(--ink);margin:0;letter-spacing:-.01em}
.sec-head .num{background:none;color:#bdb5a6;font-size:12.5px;font-weight:700;padding:0;border-radius:0;
  font-variant-numeric:tabular-nums;letter-spacing:.06em}
.sec-head .hint{margin-left:auto;font-size:11.8px;color:#a09889;font-weight:400}
/* 核心结论条（每节唯一强调块） */
.okbox{background:var(--mint);border:1px solid var(--mintline);border-radius:12px;padding:16px 20px 16px 50px;
  color:#1f4f3b;font-size:14px;line-height:1.82;margin:0 0 22px;position:relative}
.okbox:before{content:"✓";position:absolute;left:18px;top:15px;width:20px;height:20px;border-radius:50%;
  background:#4c8b68;color:#fff;font-size:12px;font-weight:800;line-height:20px;text-align:center}
.okbox b{color:#1b4632}
/* 卡片：大留白、无阴影、细边 */
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:14px}
.grid2{gap:14px;grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}
.grid3{gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
/* 小标题降权：不再与节标题争视觉 */
h4{font-size:13px;font-weight:700;color:#8b8577;letter-spacing:.06em;text-transform:none;
  border-left:none;padding-left:0;margin:26px 0 11px}
h4:first-child{margin-top:0}
details{background:#fff;border:1px solid var(--line);border-radius:10px;margin-bottom:10px}
summary{padding:12px 16px;font-size:13px;font-weight:600;color:#5c574e}
.dbody{padding:14px 18px 18px;font-size:13px}
/* 指标卡：大号绿色数字 + 下方说明（对齐 demo 统计条） */
.metrics{gap:14px;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));margin-bottom:22px}
.metric{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.metric .v{font-size:30px;font-weight:800;color:var(--primary);line-height:1.15;letter-spacing:-.02em}
.metric .l{font-size:12px;color:#8b8577;margin-top:6px}
.stats{gap:10px;margin-bottom:20px}
.stat{background:#fff;border:1px solid var(--line);border-radius:10px;padding:9px 14px;font-size:12.2px;color:#6f6a61}
.stat b{color:var(--primary);font-size:17px;font-weight:800;margin-right:4px}
.stat.a,.stat.b{background:#fff}
/* 关键判断：行距拉开、来源徽章靠右 */
.kj{padding:14px 0;border-bottom:1px solid #f2efe7;font-size:13.4px;line-height:1.85}
.kj:first-child{padding-top:2px}
.kj:last-child{border-bottom:none;padding-bottom:2px}
.kjhd{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:5px}
.kjhd .xsmall{margin-left:auto}
.kjt{font-size:13.6px;line-height:1.85;color:#33302b}
.okbox .clrow{margin:6px 0;font-size:13.6px;line-height:1.8}
.okbox .clrow:first-child{margin-top:2px}
.okbox .clrow .tag{vertical-align:1px;margin-right:8px}
.okbox .cite{margin-left:4px}
.tag{white-space:nowrap}
th{white-space:nowrap}
.ordlist td:nth-child(4),.ordlist td:nth-child(5){white-space:nowrap}
.ordlist td:nth-child(3){min-width:320px}
.polist th:nth-child(n+4),.polist td:nth-child(n+4){white-space:nowrap}
.scent td:nth-child(1),.scent td:nth-child(3),.scent td:nth-child(4){white-space:nowrap}
.scent td:nth-child(2){min-width:440px}
.conlist td:nth-child(1){white-space:nowrap}
.conlist td:nth-child(3){min-width:280px}
.cardx{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 16px;font-size:12.6px;color:#6f6a61;margin-bottom:12px}
.cite{background:#eef5ef;color:#2c5f46;border:1px solid var(--mintline);border-radius:4px;font-size:10.5px;padding:1px 6px}
.cite.missing{background:var(--cream);color:#8a5f00;border-color:var(--creamline)}
/* 表格：去重边、行高放宽 */
table{font-size:12.8px;border-color:var(--line)}
th{background:#f7f4ed;color:#6f6a61;font-weight:700;padding:11px 12px;font-size:11.8px;letter-spacing:.02em}
td{padding:11px 12px;border-bottom:1px solid #f2efe7}
tr:hover td{background:#fdfcf8}
/* 多流派卡片（demo 同款：2×2、大留白） */
.ms-grid{gap:16px;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));margin-bottom:16px}
.ms-card{border-radius:12px;padding:20px 22px;border-color:var(--line)}
.ms-card .h{font-size:15px;font-weight:700;color:var(--ink);margin-bottom:10px}
.ms-card .h i{width:7px;height:7px;border-radius:50%;background:#4c8b68}
.ms-card .b,.ms-card p{font-size:13.4px;color:#5c574e;line-height:1.9}
/* 矩阵：浅色底、无粗边 */
.mx{gap:8px;margin:6px 0 18px}
.mx .hd{background:#f7f4ed;border:1px solid var(--line);border-radius:8px;color:#6f6a61;font-size:11.6px;padding:9px}
.mx-cell{background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-size:12.4px}
.mx-cell.empty{background:#fbfaf6;color:#c3bcae}
.alink{background:#eef5ef;border:1px solid var(--mintline);color:#2c5f46;border-radius:4px;font-size:10.5px}
.noact{background:var(--cream);border:1px solid var(--creamline);color:#8a5f00;border-radius:4px}
/* 时间轴路线图 */
.roadmap .track{background:#e3ddd0;height:2px;top:16px;opacity:1}
.phase-head .pt{font-size:14px}
.phase-head .pd{font-size:11.8px;color:#a09889}
.act-card{border-radius:10px;padding:14px 16px;margin-bottom:11px;border-left-width:3px;border-color:var(--line)}
.act-card.pri-high{border-left-color:var(--accent)}
.act-card .nm{font-size:13.4px}
/* 三情景量化卡 */
.qi-card{border-radius:12px;box-shadow:none;border-color:var(--line)}
.qi-head{padding:18px 20px 14px}
.qi-name{font-size:15px;color:var(--ink)}
.qi-rank{background:var(--primary2);border-radius:5px}
.qi-val{background:#faf9f4;border-color:var(--line);border-radius:9px;padding:10px 14px}
.qi-val .n{font-size:21px}
.qi-val .lb{font-size:11.4px;color:#8b8577}
.qi-note,.qi-legend{background:#fff;border-color:var(--line);border-radius:10px;font-size:12.4px}
/* 其他零散块统一风格 */
.quote{background:#faf9f4;border-left:3px solid #d8d2c4;color:#4d483f;font-size:12.8px}
.notice{background:var(--cream);border:1px solid var(--creamline);border-radius:10px;color:#7b5c16;font-size:12.6px;padding:12px 16px}
.lead-card{border-radius:12px;border-left-width:3px;padding:18px 20px;font-size:14px;line-height:1.9}
.secnote,.sec-note{font-size:12.4px;color:#8b8577;line-height:1.75;margin-bottom:12px;background:#f7f9fb;border:1px solid #e6ecf3;border-radius:8px;padding:9px 13px}
.footer{color:#a09889;font-size:11.4px;border-top:1px solid var(--line);padding-top:22px;margin-top:44px}
/* PESTEL 固定六维卡（3×2） */
.pestel-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:6px 0 14px}
.pcard{background:#fff;border:1px solid var(--line);border-radius:10px;padding:13px 15px;min-height:88px}
.pcard .ph{display:flex;align-items:center;justify-content:space-between;gap:6px;margin-bottom:8px}
.pcard .ph b{font-size:13.6px;color:var(--ink)}
.pcard .ps{font-size:12.2px;color:#5c574e;line-height:1.7}
.pcard .tag{margin:0}
.pcard.gap{background:#f4f5f6;border-style:dashed;border-color:#dfe3e8}
.pcard.gap .ph b,.pcard.gap .ps{color:#9aa0a8}
.tag.ok{background:#e9f5f1;color:var(--teal);border-color:#c9e7dd}
.tag.warn{background:#fdf5e6;color:var(--gold);border-color:#ecd9b4}
.ms-concl.front{margin:0 0 14px;background:var(--mint);border-color:var(--mintline);border-radius:10px;padding:14px 18px}
.ms-concl.front .tt{color:#1b4632}
.ms-insight{font-size:13.4px;line-height:1.85;color:#1b4632;font-weight:600}
.resrow{font-size:12px;line-height:1.7;color:#5c574e;margin:5px 0}
.resrow b{color:var(--primary)}
/* 政策数据三维度（赛道/时间/类型）——三种不同可视化：热力卡 / 竖向柱 / 环形 */
.dim-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:14px}
.dim-grid .chartbox{margin-bottom:0;height:100%}
.chart-note{font-size:11.4px;color:#9aa0a8;line-height:1.6;margin:-6px 0 10px}
/* 原文来源标注 */
.src-tag{display:inline-block;font-size:10.5px;font-weight:700;padding:1px 7px;border-radius:10px;white-space:nowrap;vertical-align:middle}
.src-tag.ok{background:#e4f2ea;color:#1b6b45;border:1px solid #bfe0cd}
.src-tag.mid{background:#fdf3dc;color:#8a6d1f;border:1px solid #efe0b0}
.src-tag.warn{background:#f4f1ea;color:#8d877b;border:1px solid #e2ddd2}
.dim-grid .barrow{gap:6px}
.dim-grid .barrow .bl{width:104px}
/* 维度一：赛道热力卡片 */
.seg-heat{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
.seg-cell{position:relative;border-radius:8px;padding:9px 10px;min-height:58px;display:flex;flex-direction:column;justify-content:center;overflow:hidden}
.seg-cell.lv1{background:#eef4ef;border:1px solid #d8e7dc}
.seg-cell.lv2{background:#cfe4d5;border:1px solid #aecfb9}
.seg-cell.lv3{background:#2c5f46;border:1px solid #244e38;color:#fff}
.seg-cell .sc-id{font-size:10px;font-weight:800;letter-spacing:.03em;opacity:.7}
.seg-cell .sc-nm{font-size:11.3px;font-weight:600;line-height:1.3;margin-top:2px;color:inherit}
.seg-cell .sc-n{position:absolute;right:9px;top:7px;font-size:16px;font-weight:800;color:var(--primary);font-variant-numeric:tabular-nums}
.seg-cell.lv3 .sc-n{color:#fff}
/* 维度二：年份竖向柱状 */
.vbar{display:flex;align-items:flex-end;gap:6px;height:196px;padding-top:4px}
.vb-col{flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;height:100%}
.vb-n{font-size:11px;font-weight:800;color:var(--primary);font-variant-numeric:tabular-nums;margin-bottom:3px}
.vb-track{flex:1;width:100%;display:flex;align-items:flex-end;justify-content:center;border-bottom:1px solid var(--line)}
.vb-fill{width:66%;max-width:32px;background:linear-gradient(180deg,#4c8b68,#2c5f46);border-radius:5px 5px 0 0;min-height:4px}
.vb-col.unk .vb-fill{background:linear-gradient(180deg,#b9b2a4,#8d877b)}
.vb-col.unk .vb-n{color:#8d877b}
.vb-lb{font-size:10px;color:#6f6a61;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
/* 维度三：类型环形占比 */
.pie-wrap{display:flex;align-items:center;gap:14px;min-height:196px}
.pie-donut{width:108px;height:108px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center}
.pie-hole{width:62px;height:62px;border-radius:50%;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center}
.pie-hole b{font-size:19px;color:var(--primary);line-height:1}
.pie-hole span{font-size:9px;color:#9aa0a8;margin-top:3px}
.pie-legend{flex:1;min-width:0;display:flex;flex-direction:column;gap:5px}
.pie-lg{display:flex;align-items:center;gap:6px;font-size:11px}
.pie-lg i{width:9px;height:9px;border-radius:2px;flex:none}
.pl-nm{flex:1;color:#6f6a61;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pl-n{font-weight:800;color:var(--primary);font-variant-numeric:tabular-nums}
/* 政策沿革分析分组 */
.lg-group{border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:12px;background:#fff}
.lg-group .lg-head{display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.lg-group .lg-head b{font-size:13px;color:var(--ink)}
.lg-group.valid{border-left:3px solid #4c8b68}
.lg-group.direction{border-left:3px solid var(--gold)}
.lg-group .sec-note{margin-bottom:10px}
@media(max-width:1100px){.dim-grid{grid-template-columns:1fr}}
@media(max-width:920px){.pestel-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.tag{border-radius:4px;font-size:11px;padding:1px 7px;font-weight:600}
.layer{border-left:2px solid #e3ddd0;padding:11px 13px}
.layer .lb{background:#4c8b68;border-radius:3px;font-size:10px}
.trans{background:#f7f4ed;border:1px dashed #dfd8c8;color:#6f6a61}
/* 行动路线图：单条横轴 + 三段并列（契约 patch-4 的"横向时间轴"） */
.rm3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;position:relative;margin:10px 0 4px;align-items:start}
.rm3:before{content:"";position:absolute;left:5px;right:5px;top:5px;height:2px;background:#e3ddd0;z-index:0}
.rm3 .phase{margin:0;position:relative;z-index:1}
.rm3 .phase-head{display:block;margin-bottom:12px}
.rm3 .phase-head .dot{display:block;box-shadow:0 0 0 3px #faf8f3;margin:0}
.rm3 .phase-head .pt{display:block;margin-top:7px;font-size:13.6px;color:var(--ink)}
.rm3 .phase-head .pd{display:block;font-size:11.4px;color:#a09889;line-height:1.65;margin-top:2px}
.act-card .row{font-size:12.4px;line-height:1.8;color:#5c574e;margin-top:6px}
details.mini{border:none;background:none;margin:10px 0 0;border-radius:0}
details.mini>summary{padding:0;font-size:11.5px;color:#a09889;background:none;border:none;font-weight:600}
details.mini>summary:before{content:"▸";color:#c3bcae}
details.mini[open]>summary:before{content:"▾"}
details.mini .dbody{padding:8px 0 0;background:none}
@media(max-width:920px){.rm3{grid-template-columns:1fr;gap:16px}.rm3:before{display:none}}
@media(max-width:920px){
  .main{margin-left:0;width:100%;padding:0 18px 70px;max-width:none}
  .side{width:100%;position:sticky;top:0;height:auto;z-index:50;border-bottom:1px solid var(--line);
    box-shadow:0 2px 10px rgba(28,45,70,.08);padding:10px 14px}
  .side h1{margin:4px 0 6px;font-size:14px}
  .side nav{flex-wrap:nowrap;overflow-x:auto;gap:4px;padding-bottom:2px}
  .side nav a{flex:none;white-space:nowrap;font-size:11.5px;padding:4px 9px;border-left:none;
    border-bottom:2px solid transparent;background:#fff}
  .side nav a.active{border-left-color:transparent;border-bottom-color:var(--primary2)}
  section[id]{scroll-margin-top:118px}
  .sec-head h3{font-size:18px;flex-wrap:wrap;gap:8px}
  .sec-head .hint{display:none}
}
/* ---------- 五阶段新版面组件 ---------- */
.roadmap.visual{position:relative;margin:16px 0 6px;padding-top:6px}
.roadmap.visual:before{content:"";position:absolute;left:5%;right:5%;top:20px;height:3px;
  background:linear-gradient(90deg,#a9422f 0%,#3f7d5c 50%,#2c5f46 100%);border-radius:3px;opacity:.85}
.rm-milestone{display:flex;align-items:center;height:30px;position:relative;z-index:1}
.rm-dot{width:16px;height:16px;border-radius:50%;background:#fff;border:3px solid currentColor;flex:none;
  box-shadow:0 0 0 4px var(--bg)}
.rm-line{flex:1}
.phase.now{color:#a9422f}.phase.mid{color:#3f7d5c}.phase.long{color:#2c5f46}
.phase-head{display:block;margin:8px 0 4px}
.phase-head .pt{display:block;font-size:14px;color:var(--ink);font-weight:700}
.rm-ms{display:inline-block;margin-top:3px;font-size:10.8px;color:currentColor;font-weight:700;
  background:#fff;border:1px solid var(--line);border-radius:999px;padding:1px 9px}
.phase>.pd{font-size:11.6px;color:#a09889;line-height:1.65;margin-bottom:10px}
.phase-cards .card{margin-bottom:10px}
@media(max-width:920px){.roadmap.visual:before{display:none}.rm-line{display:none}}

.mxpair{display:grid;grid-template-columns:1fr;gap:16px}
.mxcol h4{margin:0 0 8px}
.calc-mx{grid-template-columns:78px repeat(3,minmax(0,1fr));gap:6px}
.calc-mx .hd{font-size:11px;padding:7px 6px}
.calc-mx .mx-cell{padding:8px 9px;font-size:11.8px;min-height:58px}
.mx-cell.hot{background:#fbeaea;border-color:#f0cfcb}
.mx-cell.warm{background:#fdf5e6;border-color:#eddcba}
.mx-method{background:#fff;border:1px solid var(--line);border-radius:9px;padding:10px 14px;
  font-size:12px;color:var(--muted);margin:8px 0 16px}
@media(min-width:1180px){.mxpair{grid-template-columns:1fr 1fr}.calc-mx{grid-template-columns:64px repeat(3,minmax(0,1fr))}}

.kjf{margin-top:7px}
.chainname{font-size:13.4px;font-weight:700;color:var(--ink)}
.chainflow{display:grid;grid-template-columns:minmax(0,1fr) 26px minmax(0,1fr) 26px minmax(0,1.1fr);
  gap:0;align-items:stretch;margin:12px 0}
.cnode{background:#faf8f3;border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-height:86px}
.cnode.risk{background:#fdf3e8;border-color:var(--creamline)}
.cn{font-size:11.4px;font-weight:700;color:#8b8577;margin-bottom:6px}
.cnode.risk .cn{color:#a2691d}
.cb{font-size:12.8px;color:#33302b;line-height:1.8}
.carr{display:flex;align-items:center;justify-content:center;color:#bdb5a6;font-size:18px;font-weight:700}
@media(max-width:920px){.chainflow{grid-template-columns:1fr;gap:6px}.carr{transform:rotate(90deg);height:18px}}

.kjwrap{padding:4px 20px}
.kjd{padding:14px 0;border-bottom:1px solid #f2efe7}
.kjd:last-child{border-bottom:none}
.kjh{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:6px}
.kn{display:inline-flex;align-items:center;justify-content:center;min-width:28px;height:20px;
  background:var(--primary);color:#fff;border-radius:4px;font-size:11px;font-weight:800;padding:0 6px}
.kp{font-size:11.6px;color:#8b8577}
.kjt{font-size:13.4px;line-height:1.85;color:#33302b}
.chartbox{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:14px}
.chartbox h5{margin:0 0 12px;font-size:13px;color:var(--primary);font-weight:700}
.barrow{display:flex;align-items:center;gap:10px;margin-bottom:8px;font-size:12.4px}
.barrow .bl{width:170px;flex:none;color:#6f6a61;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.barrow .bt{flex:1;background:#f2efe7;border-radius:4px;height:14px;overflow:hidden}
.barrow .bf{display:block;height:100%;background:linear-gradient(90deg,#4c8b68,#2c5f46);border-radius:4px}
.barrow .bv{width:28px;flex:none;font-weight:800;color:var(--primary);font-variant-numeric:tabular-nums}
.chaincard .chh{display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin-bottom:9px}
.lay{padding:9px 0;border-bottom:1px dashed #f2efe7}
.lay:last-of-type{border-bottom:none}
.layh{display:flex;align-items:center;gap:9px}
.layh .lb{display:inline-block;background:#4c8b68;color:#fff;border-radius:3px;padding:1px 7px;font-size:10.5px;font-weight:700}
.layh .nm{font-size:12.6px;color:var(--ink);font-weight:600}
.lay .st{font-size:12.6px;color:#5c574e;line-height:1.8;margin-top:4px}
.sc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:16px}
.sc-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.sc-card.opt{border-top:3px solid #6f9c85}
.sc-card.base{border-top:3px solid #2c5f46}
.sc-card.pes{border-top:3px solid #a9422f}
.sc-card .sch{font-size:15px;font-weight:700;color:var(--ink);display:flex;gap:8px;align-items:center;margin-bottom:8px}
.sc-card .sct{font-size:13px;line-height:1.85;color:#5c574e}
@media print{.side,.controls,.btn{display:none!important}.main{margin-left:0;width:100%;padding:0}body{background:#fff}details>.dbody{display:block!important}.qi-details>.qi-body{display:block!important}.qchip:hover::after,.qchip:focus::after{display:none}}
"""

JS = """
const navs=[].slice.call(document.querySelectorAll('.side nav a'));
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)navs.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id))}),{rootMargin:'-10% 0px -80% 0%'});
document.querySelectorAll('section').forEach(s=>io.observe(s));
function flt(){
 const q=(document.getElementById('pq').value||'').toLowerCase(),g=document.getElementById('pg').value,s=document.getElementById('ps').value;
 let n=0;
 document.querySelectorAll('#plist .pitem').forEach(el=>{
  const ok=(!q||el.dataset.search.indexOf(q)>=0)&&(!g||el.dataset.group===g)&&(!s||el.dataset.segs.indexOf(s)>=0);
  el.style.display=ok?'':'none';if(ok)n++;
 });
 document.getElementById('pcount').textContent='显示 '+n+' 条';
}
document.addEventListener('DOMContentLoaded',()=>{
 ['pq','pg','ps'].forEach(id=>document.getElementById(id).addEventListener(id==='pq'?'input':'change',flt));
 document.getElementById('preset').addEventListener('click',()=>{document.getElementById('pq').value='';document.getElementById('pg').value='';document.getElementById('ps').value='';flt();});
});
"""


def esc(v):
    return html.escape('' if v is None else str(v), quote=True)


def txt(v):
    if v is None:
        return ''
    if isinstance(v, bool):
        return '是' if v else '否'
    if isinstance(v, list):
        return '；'.join(txt(x) for x in v)
    if isinstance(v, dict):
        return '；'.join('%s：%s' % (k, txt(x)) for k, x in v.items())
    return str(v)


def arr(v):
    if isinstance(v, list):
        return [str(x) for x in v]
    if not v:
        return []
    if isinstance(v, str):
        try:
            o = json.loads(v.replace("'", '"'))
            if isinstance(o, list):
                return [str(x) for x in o]
        except Exception:
            pass
        return [x.strip() for x in v.split(',') if x.strip()]
    return [str(v)]


def tags(v, cls=''):
    return ''.join('<span class="tag %s">%s</span>' % (cls, esc(x)) for x in arr(v))


def link(u, label=None):
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(u), esc(label or u)) if u else '<span class="muted">未核实</span>'


def para(v):
    return ''.join('<p>%s</p>' % esc(x) for x in txt(v).split('\n') if x.strip())


def brief(v, n):
    s = ' '.join(txt(v).split())
    return s[:n] + '…' if len(s) > n else s


def split_tag(v):
    """把正文开头的【证据分级｜判断类型】前缀拆成独立标签，正文不再带重复前缀。"""
    s = ' '.join(txt(v).split())
    tag = ''
    for _ in range(2):
        if s.startswith('【') and '】' in s[:60]:
            tag = s[1:s.index('】')]
            s = s[s.index('】') + 1:].lstrip('：: ')
        else:
            break
    return tag, s


def kv(pairs):
    return '<div class="kv">' + ''.join(
        '<div class="k">%s</div><div>%s</div>' % (esc(k), v) for k, v in pairs if v) + '</div>'


def card(inner):
    return '<div class="card">%s</div>' % inner


def details(sum_, body):
    return '<details><summary>%s</summary><div class="dbody">%s</div></details>' % (sum_, body)


# ===== 人话化辅助：把结构化字段转成「用户看得懂的自然语言」，避免列表/字典原文与字段名泄漏 =====
_PESTEL_CN = {'P': '政治', 'E': '经济', 'S': '社会', 'T': '技术', 'Env': '环境', 'L': '法律'}


def dim_cn(v):
    """把 PESTEL 维度数组/字符串转成中文维度名，如 ['P','E','L'] → 政治、经济、法律。"""
    codes = arr(v)
    names = []
    for c in codes:
        key = str(c).strip()
        names.append(_PESTEL_CN.get(key, _PESTEL_CN.get(key.capitalize(), key)))
    return '、'.join(dict.fromkeys(names)) if names else '综合'


def clean_sentence(v, n=200):
    """去除技术噪声后的自然语言短句：去掉方括号列表、字段名、HTML 实体，保留可读正文。"""
    s = ' '.join(txt(v).split())
    s = re.sub(r'\[[^\]]*\]', '', s)          # 去掉 ['P','E'] 这类列表残片
    s = re.sub(r'\b[a-zA-Z_]{4,}\b(?=为|是|：|取|按)', '', s)  # 去掉 effect_level 为 / stability_weight 取 等字段名
    s = re.sub(r'\s{2,}', ' ', s).strip(' ；;。')
    return brief(s, n)


def certainty_rank(v):
    """确定性排序权重：高>中>低。用于主视图优先显示相对更可信的条目。"""
    return {'高': 0, '中': 1, '低': 2}.get(str(v or '').strip(), 3)


def qc_chip(val, final):
    """把内部校验状态（validated/rejected 等）转成人话标签，不把内部术语暴露给业务用户。
    完整驳回记录仍在 s13「反向盲算与契约校验」折叠区如实展示，此处只做措辞转换。"""
    s = str((val or {}).get('status') or (final or {}).get('status') or '').strip().lower()
    if s in ('validated', 'done', 'passed', 'ok', ''):
        return ('数据核验 · 已完成', 'ok')
    n = len((val or {}).get('rejections') or []) + len((val or {}).get('local_rule_rejections') or [])
    return ('数据核验 · %d 项待完善（详见质控说明）' % n if n else '数据核验 · 详见质控说明', 'warn')


def table(heads, rows):
    return '<div class="scroll"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        ''.join('<th>%s</th>' % esc(h) for h in heads),
        ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows))


SECTION_CONCLUSIONS = {}
RENDER_ISSUES = []   # 渲染层核对发现的缺口（契约 v3：来源待补等计入 known_issues 类展示）

# 节 → 流水线阶段眉标（对应契约 stage_to_section_map：阶段二独立成节、阶段三先于阶段四）
STAGE_MAP = {
    '1': '摘要', '2': '阶段一 · 范围界定与主体核验', '3': '阶段一 · 赛道拆分与研究问题',
    '4': '阶段二 · 政策扫描与证据分级', '5': '阶段二 · 政策解读', '6': '阶段二 · 政策沿革',
    '7': '阶段三 · 传导推演', '8': '阶段四 · 机会与风险', '9': '阶段四 · 量化影响',
    '10': '阶段五 · 落地条件', '11': '阶段五 · 行动清单',
    '12': '阶段六 · 不确定性与监测', '13': '阶段六 · 契约审校',
    '14': '附录 · 质量控制', '15': '附录 · 证据来源', '16': '附录 · 使用须知',
}


def sec(num, title, hint, body):
    concl = SECTION_CONCLUSIONS.get(str(num))
    head = '<div class="okbox"><b>核心结论</b>：%s</div>' % concl if concl else ''
    stage = STAGE_MAP.get(str(num))
    eb = '<div class="eb"><i></i>%s</div>' % esc(stage) if stage else ''
    return ('<section id="s%s"><div class="sec-head">%s<h3><span class="num">%02d</span>%s</h3>'
            '<span class="hint">%s</span></div>%s</section>') % (
        num, eb, int(num), esc(title), esc(hint), head + body)


def h4(t):
    return '<h4>%s</h4>' % esc(t)


# ============================== 契约 v3 · patch-1：执行摘要 ==============================

def _metric_cards(opps, risks, pols, segs):
    """客观指标卡：只放可核对的计数类客观指标；内部质控分（完整度评分等）绝不在此出现。"""
    m = [('政策条目数', len(pols)), ('核心赛道数', len(segs)),
         ('机会条目数', len(opps)), ('风险条目数', len(risks))]
    return ('<div class="metrics">' + ''.join(
        '<div class="metric"><div class="v">%s</div><div class="l">%s</div></div>' % (esc(v), esc(l))
        for l, v in m) + '</div>')


def _cite_badge(ids):
    """来源徽章：默认可见、小号等宽、浅底深字；缺来源显示「来源待补」并计入渲染层缺口。"""
    ids = arr(ids)
    if ids:
        return '<span class="cite">依据 %s</span>' % esc('·'.join(ids))
    RENDER_ISSUES.append('s1 关键判断存在缺来源标注条目（evidence_policy_ids 为空），已按契约显示「来源待补」。')
    return '<span class="cite missing">来源待补</span>'


def _key_judgements(opps, risks, visible=3):
    picks = ([('机会', x) for x in opps if (x.get('certainty') or '') == '高'][:3] +
             [('风险', x) for x in risks if (x.get('certainty') or '') == '高'][:2])
    if not picks:
        picks = ([('机会', x) for x in opps[:3]] + [('风险', x) for x in risks[:2]])
    if not picks:
        return ''

    def item(kind, x):
        tg, body = split_tag(x.get('description'))
        return ('<div class="kj"><div class="kjhd"><span class="tag %s">%s %s</span>%s'
                '<span class="xsmall muted">确定性 %s</span></div>'
                '<div class="kjt">%s%s</div></div>'
                % ('opp' if kind == '机会' else 'risk', esc(x.get('id')), kind,
                   '<span class="tag gray">%s</span>' % esc(tg) if tg else '',
                   esc(x.get('certainty')), esc(brief(body, 108)),
                   _cite_badge(x.get('evidence_policy_ids'))))

    head = h4('关键判断（摘录式汇编，非新增研判）')
    if len(picks) <= visible:
        return head + card(''.join(item(*p) for p in picks))
    return (head + card(''.join(item(*p) for p in picks[:visible])) +
            details('<span class="xsmall muted">其余 %d 条关键判断（含来源徽章）</span>' % (len(picks) - visible),
                    ''.join(item(*p) for p in picks[visible:])))


# ============================== 契约 v3 · patch-2：多流派分析结论 ==============================

MS_FIELDS = [('problem_stream', '问题流'), ('policy_stream', '政策流'),
             ('politics_stream', '政治流'),
             ('window_and_policy_entrepreneur', '窗口与政策企业家'),
             ('primary_region_context', '主区域语境')]


def _pestel_card(code, pp):
    """渲染固定六维中的一维：维度名 + 稳定性标签 + 一句话结论。无对应条款的维度灰化显示「证据缺口」。"""
    cn = _PESTEL_CN.get(code, code)
    hits = [x for x in pp if code in [str(c) for c in arr(x.get('dimension') or x.get('pestel_dimension'))]]
    if not hits:
        return ('<div class="pcard gap"><div class="ph"><b>%s %s</b></div>'
                '<div class="ps small">证据缺口，不作现行约束——本次无经核实的对应专项条款。</div></div>'
                % (esc(code), esc(cn)))
    # 稳定性判定：综合多个命中条目的 stability_weight
    stabs = [str(x.get('stability_weight') or x.get('historical_stability') or '') for x in hits]
    label, cls = '有据可查', ''
    if any('收紧' in s for s in stabs):
        label, cls = '持续收紧', 'warn'
    elif all(('高' in s) for s in stabs if s):
        label, cls = '高稳定', 'ok'
    elif any(('中' in s) for s in stabs):
        label, cls = '中高稳定', 'ok'
    # 取最具代表性的一条结论（优先 rationale 更完整者），清洗为自然语言
    best = max(hits, key=lambda x: len(str(x.get('rationale') or x.get('statement') or '')))
    line = clean_sentence(best.get('rationale') or best.get('statement'), 120)
    return ('<div class="pcard"><div class="ph"><b>%s %s</b><span class="tag %s">%s</span></div>'
            '<div class="ps small">%s</div></div>'
            % (esc(code), esc(cn), cls, esc(label), esc(line or '见下方完整依据')))


def _ms_block(R):
    ms = R.get('multiple_streams') or {}

    def one(key, label):
        t = txt(ms.get(key))
        if not t:
            return ''
        if len(t) > 300:
            body = ('<div class="small">%s</div>' % para(brief(t, 260)) +
                    details('<span class="xsmall muted">展开原文（%d 字）</span>' % len(t), para(t)))
        else:
            body = '<div class="small">%s</div>' % para(t)
        return '<div class="ms-card"><div class="h"><i></i>%s</div>%s</div>' % (esc(label), body)

    cards = ''.join(one(k, l) for k, l in MS_FIELDS)
    if not cards:
        return ''
    msc = (R.get('multiple_streams_conclusion') or ms.get('conclusion') or {})
    if not isinstance(msc, dict):
        msc = {'summary': txt(msc)}
    if msc:
        merged = txt(msc.get('streams_merged'))
        win = txt(msc.get('window_status'))
        # 核心洞察前置：一句话说人话——问题是否被确认、政策是否已落地、窗口是否开着、该不该现在动
        _merged_raw = str(msc.get('streams_merged') or '').strip()
        _merge_cn = {'是': '问题、方案与执行主体已经形成合力', '部分': '关键问题已获确认，但仍有环节未完全落地',
                     '否': '三条线索尚未汇合'}.get(_merged_raw, '三流汇合状态待判定')
        _win_cn = ('政策窗口正处「%s」' % win) if win else '政策窗口状态待判定'
        _action_cn = ('建议把握当前窗口抓紧布局' if win == '开启中' else
                      ('窗口已关闭，宜转向储备与观察' if win == '关闭' else '窗口尚未打开，先做前期准备'))
        rows = ('<div class="ms-insight">%s；%s。%s。</div>' % (esc(_merge_cn), esc(_win_cn), esc(_action_cn)))
        # 支撑依据折叠在洞察之后
        basis = []
        if msc.get('merged_basis'):
            basis.append('<div class="row">汇合依据：%s</div>' % esc(brief(msc.get('merged_basis'), 200)))
        if msc.get('window_basis'):
            basis.append('<div class="row">窗口依据：%s</div>' % esc(brief(msc.get('window_basis'), 200)))
        if msc.get('remaining_window'):
            basis.append('<div class="row">剩余时间窗口：%s</div>' % esc(brief(msc.get('remaining_window'), 160)))
        if msc.get('summary'):
            basis.insert(0, '<div class="row">%s</div>' % esc(brief(msc.get('summary'), 300)))
        if basis:
            rows += details('<span class="xsmall muted">判定依据（原文摘录）</span>',
                            '<div class="ms-concl">%s</div>' % ''.join(basis))
        concl = '<div class="ms-concl front"><span class="tt">多流派核心洞察</span>：%s</div>' % rows
    else:
        RENDER_ISSUES.append('s5 多流派分析缺少 multiple_streams_conclusion 字段，三流汇合与窗口判定未展示（待上游补充）。')
        concl = ('<div class="ms-concl fallback"><span class="tt">多流派核心洞察</span>：'
                 '本次上游输出未包含窗口判定字段（multiple_streams_conclusion 缺失），'
                 '三流汇合状态与政策窗口判定待推演阶段补充；下方仅为各流原文，未做汇合研判，'
                 '相关缺口已计入「质量控制与局限」。</div>')
    return h4('多流派分析') + concl + '<div class="ms-grid">%s</div>' % cards


# ============================== 契约 v3 · patch-3：矩阵 + 行动交叉链接 ==============================

CAT_CN = {'no_regret': 'no-regret · 三情景共用', 'option_preserving': 'option-preserving · 保留选择权',
          'contingent': 'contingent · 视触发条件'}


def _action_index(sc):
    """{机会/风险 id: [行动 id,...]}——由行动条目的 related_*_ids 字段算出的派生关系。"""
    idx = {}
    for a in sc.get('action_paths') or []:
        aid = a.get('action_id') or a.get('id') or ''
        if not aid:
            continue
        for rid in arr(a.get('related_risk_ids')) + arr(a.get('related_opportunity_ids')):
            idx.setdefault(rid, []).append(aid)
    return idx


def _mx_links(oid, aidx):
    acts = aidx.get(oid) or []
    if acts:
        return ''.join('<a class="alink" href="#act-%s" title="跳转到行动 %s">→%s</a>'
                       % (esc(a), esc(a), esc(a)) for a in acts)
    return '<span class="noact">无对应行动</span>'


def _matrix_block(opps, risks, aidx):
    """确定性 × 影响度矩阵；数据缺二维分类字段时走 fallback（卡片列表 + 交叉链接）。"""
    items = ([('机会', x) for x in opps] + [('风险', x) for x in risks])
    lv = ('高', '中', '低')
    cells = {(c, i): [] for c in lv for i in lv}
    unclassified = []
    for kind, x in items:
        c, i = x.get('certainty'), x.get('impact_level')
        mc = str(x.get('matrix_cell') or '')
        if '-' in mc and all(p in lv for p in mc.split('-', 1)):
            c, i = mc.split('-', 1)
        if c in lv and i in lv:
            cells[(c, i)].append((kind, x))
        else:
            unclassified.append((kind, x))
    if not any(cells.values()) and unclassified:
        # fallback：无合法二维分类字段，不臆造评级，改为清单式表格 + 行动交叉链接（信息必须可见，不折叠）
        RENDER_ISSUES.append('s8 机会/风险条目缺合法 certainty×impact 分类字段，按契约 fallback 保留清单展示（未臆造矩阵评级）。')
        rows = []
        for kind, lst in (('机会', opps), ('风险', risks)):
            for x in lst:
                rows.append([
                    '<a class="mono" href="#or-%s">%s</a>' % (esc(x.get('id')), esc(x.get('id'))),
                    '<span class="tag %s">%s</span>' % ('opp' if kind == '机会' else 'risk', kind),
                    esc(brief(split_tag(x.get('description'))[1], 96)),
                    esc(x.get('certainty')), esc(x.get('impact_level') or '—'),
                    _mx_links(x.get('id'), aidx)])
        head = ('<div class="notice xsmall">本批数据未包含可核实的确定性×影响度二维分类字段（certainty / impact_level / matrix_cell），'
                '按版式契约 fallback 不臆造矩阵评级；「是否已有对应行动」不依赖该字段，仍按行动清单 related ids 如实标注。</div>')
        return head + '<div class="ordlist">' + table(['ID', '类型', '条目', '确定性', '影响度', '对应行动'], rows) + '</div>' + (
            '<div class="xsmall muted" style="margin:-4px 0 6px"><span class="alink">→A{n}</span> 表示该条已被第 11 节行动清单引用，'
            '点击跳转；<span class="noact">无对应行动</span> 为决策者视角的缺口标记，非扣分项。</div>')
    h = ('<div class="mx"><div class="hd rowhd"></div>'
         + ''.join('<div class="hd">影响 · %s</div>' % i for i in lv))
    for c in lv:
        h += '<div class="hd rowhd">确定性 · %s</div>' % c
        for i in lv:
            cell = cells[(c, i)]
            if not cell:
                h += '<div class="mx-cell empty">—</div>'
                continue
            h += '<div class="mx-cell">%s</div>' % ''.join(
                '<div class="mx-item"><span class="tag %s">%s</span>'
                '<a class="mono" href="#or-%s">%s</a>%s</div>'
                % ('opp' if kind == '机会' else 'risk', kind, esc(x.get('id')), esc(x.get('id')),
                   _mx_links(x.get('id'), aidx))
                for kind, x in cell)
    h += '</div>'
    h += ('<div class="xsmall muted" style="margin:2px 0 10px">单元格内 <span class="alink">→A{n}</span> 表示该条已被 '
          's11 行动清单引用，点击跳转；<span class="noact">无对应行动</span> 为决策者视角的缺口标记，非扣分项。</div>')
    if unclassified:
        h += ('<div class="notice xsmall">另有 %d 条未含合法分类字段，未入矩阵（不臆造评级）：%s</div>'
              % (len(unclassified), '、'.join(esc(x.get('id') or '—') for kind, x in unclassified)))
    return h


def _orcard(x, kind, aidx):
    return ('<div class="card" id="or-%s"><span class="tag %s">%s</span><span class="mono muted">%s</span>'
            '<div style="margin:8px 0;font-weight:600">%s</div>'
            '<div>%s%s</div><div class="xsmall muted" style="margin-top:6px">确定性 %s · 影响度 %s · 优先级 %s · 区域 %s</div>'
            '<div class="orref"><span class="xsmall muted">对应行动：</span>%s</div>'
            '<details><summary class="xsmall">反例检验 / 证据依据</summary><div class="dbody xsmall">'
            '<div><b>反例检验</b>：%s</div><div style="margin-top:5px"><b>依据政策</b>：%s</div>'
            '<div style="margin-top:5px"><b>影响要素</b>：%s</div></div></details></div>'
            % (esc(x.get('id')), 'opp' if kind == '机会' else 'risk', kind, esc(x.get('id')),
               esc(x.get('description')),
               tags(x.get('segment_tags'), 'a'), tags(x.get('evidence_policy_ids'), 'gray'),
               esc(x.get('certainty')), esc(x.get('impact_level')), esc(x.get('auto_priority')),
               esc(x.get('region_applicability')), _mx_links(x.get('id'), aidx),
               esc(x.get('counter_evidence')),
               esc(txt(x.get('evidence_basis'))), esc(txt(x.get('impacted_firm_element')))))


_STK_VERDICT = {'高': '具备实质否决或显著延缓该政策方向的能力',
                '中': '难以单独否决，但可能延缓落地节奏',
                '低': '不构成实质否决威胁'}


def _stakeholders_block(R):
    stks = R.get('stakeholders') or []
    if not stks:
        return ''
    lv = ('高', '中', '低')
    rows = {}
    for s in stks:
        st = s.get('stance') or '未标注'
        rows.setdefault(st, []).append(s)
    h = h4('干系人立场 × 影响力矩阵')
    h += '<div class="mx"><div class="hd rowhd"></div>' + ''.join(
        '<div class="hd">影响力 · %s</div>' % i for i in lv)
    for st in ('支持', '中立', '反对', '未标注'):
        if st not in rows:
            continue
        h += '<div class="hd rowhd">立场 · %s</div>' % esc(st)
        for i in lv:
            cell = [s for s in rows[st] if s.get('influence') == i]
            if not cell:
                h += '<div class="mx-cell empty">—</div>'
                continue
            h += '<div class="mx-cell">%s</div>' % ''.join(
                '<div class="mx-item"><b>%s</b>%s</div>'
                % (esc(brief(s.get('name') or s.get('id') or '—', 20)),
                   '、'.join('<a class="mono" href="#or-%s">%s</a>' % (esc(r), esc(r))
                             for r in arr(s.get('related_risk_ids'))))
                for s in cell)
    h += '</div>'
    notes = []
    for s in stks:
        if (s.get('stance') or '') == '反对':
            lvl = s.get('influence') or '未标注'
            verdict = _STK_VERDICT.get(lvl, '影响力未标注，无法给出否决判断')
            rel = arr(s.get('related_risk_ids')) or arr(s.get('related_ids'))
            rels = ('、'.join('<a class="mono" href="#or-%s">%s</a>' % (esc(r), esc(r)) for r in rel)
                    if rel else '<span class="muted">（该干系人未标注关联条目）</span>')
            notes.append('<div class="small" style="margin-top:6px">%s的影响力为%s，意味着%s，可能影响的是%s%s。</div>'
                         % (esc(s.get('name') or '—'), esc(lvl), esc(verdict), rels,
                            '（%s）' % esc(brief(s.get('note'), 90)) if s.get('note') else ''))
    if notes:
        h += '<div class="notice"><b>落地含义</b>%s</div>' % ''.join(notes)
    return h


# ============================== 契约 v3 · patch-4：行动时间轴路线图 ==============================

def _phase_of(a):
    cat = str(a.get('category') or '').lower()
    tl = txt(a.get('timeline'))
    if 'no_regret' in cat or '立即' in tl:
        return 'now', '短期 · 立即启动', '三情景共用的 no-regret 动作'
    if 'option' in cat or '保留' in tl or '1年' in tl or '一年' in tl:
        return 'mid', '中期 · 1年内', '小成本保留选择权'
    return 'long', '长期 · 机制化', '视触发条件启动 / 持续跟踪'


def _act_priority(a):
    p = str(a.get('priority') or a.get('auto_priority') or '')
    if p in ('高', '1', '1级'):
        return '高', 'pri-high'
    if p in ('中', '2', '3', '2级', '3级'):
        return '中', 'pri-mid'
    return None, 'pri-mid'   # 缺失不编造，默认边框但无徽章


def _roadmap_block(sc, known_ids):
    acts = sc.get('action_paths') or []
    if not acts:
        return '<div class="notice">本次输出未包含行动清单（action_paths 为空），无法绘制路线图。</div>'
    phases = {'now': [], 'mid': [], 'long': []}
    for a in acts:
        phases[_phase_of(a)[0]].append(a)
    cols = ''
    for idx_, (key, cls, title, desc, milestone) in enumerate([
            ('now', 'now', '短期 · 立即启动', '三情景共用的 no-regret 动作', 'M1 · 立即'),
            ('mid', 'mid', '中期 · 1年内', '小成本保留选择权（时间区间以行动自带时间信息为准）', 'M2 · 1年内'),
            ('long', 'long', '长期 · 机制化', '视触发条件启动 / 持续跟踪', 'M3 · 机制化')]):
        cards = ''.join(_act_card(a, known_ids) for a in phases[key])
        if not cards:
            cards = '<div class="notice xsmall">该时段暂无行动。</div>'
        cols += ('<div class="phase %s"><div class="rm-milestone"><span class="rm-dot"></span>'
                 '<span class="rm-line"></span></div>'
                 '<div class="phase-head"><span class="pt">%s</span><span class="rm-ms">%s</span></div>'
                 '<div class="pd">%s</div><div class="phase-cards">%s</div></div>'
                 % (cls, esc(title), esc(milestone), esc(desc), cards))
    return ('<div class="roadmap rm3 visual">%s</div>'
            '<div class="xsmall muted" style="margin-top:10px">路线图按行动的三情景属性分三段（no-regret 立即启动 / '
            'option-preserving 中期 / contingent 视触发条件）；时间标注一律取行动自带的时间信息，无明确时间的不编造具体月数。'
            '卡片底部「对应条目」与上方矩阵的 →A{n} 互为双向链接。</div>' % cols)


def _act_card(a, known_ids):
    known_ids = known_ids or set()
    aid = a.get('action_id') or a.get('id') or ''
    pri, pcls = _act_priority(a)
    hd = '<div class="hd">'
    if aid:
        hd += '<span class="mono muted">%s</span>' % esc(aid)
    hd += '<span class="nm">%s</span>' % esc(brief(a.get('action') or a.get('name'), 120))
    if pri:
        hd += '<span class="pri%s">%s优先</span>' % ('' if pri == '高' else ' mid', esc(pri))
    hd += '</div>'
    rows = ''
    if a.get('acceptance_criteria'):
        rows += '<div class="row"><span class="xsmall muted">验收标准：</span>%s</div>' % esc(
            brief(a.get('acceptance_criteria'), 120))
    extra = ''
    if a.get('category'):
        extra += '<div class="row xsmall muted">属性：%s</div>' % esc(CAT_CN.get(a.get('category'), a.get('category')))
    if a.get('timeline'):
        extra += '<div class="row xsmall muted">时间：%s</div>' % esc(a.get('timeline'))
    if a.get('resource_input'):
        extra += '<div class="row xsmall muted">资源投入：%s</div>' % esc(brief(a.get('resource_input'), 120))
    if a.get('responsible_body'):
        extra += '<div class="row xsmall muted">责任部门：%s</div>' % esc(brief(a.get('responsible_body'), 140))
    if a.get('acceptance_criteria') and len(txt(a.get('acceptance_criteria'))) > 120:
        extra += '<div class="row xsmall muted">验收标准全文：%s</div>' % esc(a.get('acceptance_criteria'))
    if extra:
        rows += '<details class="mini"><summary class="xsmall">展开条件与责任部门</summary><div class="dbody">%s</div></details>' % extra
    # 对应 R/O 双向链接：无 related 字段不编造对应关系，只显示依据政策 id；
    # 未收入本批机会/风险数据的 id 不生成锚链接（避免死链），显示纯文本
    rel = arr(a.get('related_risk_ids')) + arr(a.get('related_opportunity_ids'))
    basis = arr(a.get('basis_policy_ids')) + arr(a.get('related_policy_ids')) + arr(a.get('evidence_policy_ids'))
    foot = '<div class="orref">'
    if basis:
        foot += '<span class="xsmall muted">依据政策：</span>%s' % tags(basis, 'gray')
    if rel:
        foot += ('　<span class="xsmall muted">对应条目：</span>%s'
                 % ''.join(('<a class="alink" href="#or-%s">%s</a>' % (esc(r), esc(r))
                            if r in known_ids else
                            '<span class="mono muted" title="该条目未收入本批机会/风险数据">%s</span>' % esc(r))
                           for r in rel))
    foot += '</div>'
    if not basis and not rel:
        foot = ''
    return '<div class="act-card %s" id="act-%s">%s%s%s</div>' % (pcls, esc(aid), hd, rows, foot)


# ============================== s6 政策沿革（lineage） ==============================

def _lineage_block(land, pols):
    lg = land.get('lineage') or []
    if not lg:
        return ('<div class="notice">本次输出未包含政策沿革数据（上游未提供 lineage 字段）；'
                '政策版本信息以 s4 政策全集中各条 status / effective_date 为准。</div>')
    pmap = {p.get('id'): p for p in pols}
    out = []
    for l in lg:
        vids = arr(l.get('node_ids'))
        closed = l.get('closed')
        vers = []
        for vid in vids:
            p = pmap.get(vid) or {}
            _d = str(p.get('publish_date') or l.get('date') or '').strip()
            if _d in ('未核实', '未标注', '日期未标注', '—', ''):
                _d = str(p.get('issuing_body') or '').strip() or p.get('effect_level') or '版本'
            vers.append('<div class="lin-ver"><div class="d">%s</div><div class="t">%s</div>'
                        '<div class="xsmall muted">%s%s</div></div>'
                        % (esc(brief(_d, 26)),
                           esc(brief(p.get('title') or vid, 64)),
                           esc(p.get('status') or '状态未标注'),
                           (' · <a href="%s" target="_blank" rel="noopener">官方原文</a>' % esc(p['source_url']))
                           if p.get('source_url') else ''))
        tl = '<div class="lin-tl">%s</div>' % '<span class="lin-arrow">→</span>'.join(vers) if len(vers) > 1 else (
            '<div class="lin-tl">%s</div>' % ''.join(vers))
        head = ('<div class="lin-head"><span class="tag %s">%s</span><b>%s</b>'
                '<span class="xsmall muted">%s</span>%s</div>'
                % ('opp' if closed else 'risk', '链闭合' if closed else '存在空档/未闭合',
                   esc(l.get('name') or l.get('chain_id') or '未命名沿革链'),
                   esc(l.get('direction') or ''),
                   (' <span class="xsmall">%s</span>' % esc(l.get('policy_gap'))) if l.get('policy_gap') else ''))
        body = ('<div class="kv"><div class="k">版本链</div><div class="mono">%s</div></div>'
                % esc(' → '.join(vids)))
        more = kv([('版本依据', esc(brief(l.get('evidence'), 300))),
                   ('变化要点', esc(brief(l.get('change_note'), 300))),
                   ('延续信号', esc(brief(l.get('continuity_signal'), 300))),
                   ('政策空档', esc(l.get('policy_gap') or '未标注'))])
        body += ('<details class="mini"><summary class="xsmall">展开依据、变化要点与延续信号</summary>'
                 '<div class="dbody">%s</div></details>' % more)
        out.append('<div class="lin-card">%s%s%s</div>' % (head, tl, body))
    if len(out) > 4:
        return (''.join(out[:4]) + details(
            '<span class="xsmall muted">其余 %d 条政策沿革链</span>' % (len(out) - 4), ''.join(out[4:])))
    return ''.join(out)


# ============================== 既有契约：三情景量化指标（M4） ==============================

QI_SCEN = ('optimistic', 'baseline', 'pessimistic')
QI_DELTA = (('optimistic', '乐观', '#2f6fb0'), ('baseline', '基准', '#8b97a6'),
            ('pessimistic', '悲观', '#b3402f'))
QI_LEVEL = (('optimistic', '乐观', '#9dc2e0'), ('baseline', '基准', '#4b8bc4'),
            ('pessimistic', '悲观', '#1f4e79'))


def _qi_num(x, k):
    v = (x.get('numeric_values') or {}).get(k)
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return float(v)


def _qi_gap(x):
    a, b = _qi_num(x, 'optimistic'), _qi_num(x, 'pessimistic')
    return 0.0 if a is None or b is None else abs(a - b)


def _qi_sorted(items):
    """默认排序：|乐观值 − 悲观值| 绝对差值降序，不按 JSON 原始顺序或名称。"""
    return sorted(items, key=lambda x: -_qi_gap(x))


def _qi_ref(x, pid):
    ref = next((r for r in (x.get('policy_references') or [])
                if isinstance(r, dict) and r.get('id') == pid), {})
    t = ref.get('title') or ref.get('policy_title') or ''
    q = ref.get('source_excerpt') or ''
    if t and q:
        return '【%s】%s：%s' % (pid, t, q)
    if t:
        return '【%s】%s' % (pid, t)
    if q:
        return '【%s】%s' % (pid, q)
    return '【%s】该政策 id 在政策全集中未找到标题／原文条目' % pid


def _qi_chips(x):
    ids = arr(x.get('anchor_policy_ids'))
    if not ids:
        return ''  # 空数组：整行不渲染，不显示「无」或空白徽章
    return '<div class="qi-chips"><span class="lb">锚点政策</span>' + ''.join(
        '<span class="qchip" tabindex="0" title="%s" data-tip="%s">%s</span>'
        % (esc(_qi_ref(x, i)), esc(_qi_ref(x, i)), esc(i)) for i in ids) + '</div>'


def _qi_evidence(x):
    """证明过程：仅展开后可见，12px 小字、带上边框分隔线。"""
    parts = [('测算公式', x.get('methodology_formula')),
             ('方法论说明', x.get('methodology_note')),
             ('基准口径', x.get('baseline_note')),
             ('敏感性区间', x.get('sensitivity_note')),
             ('数值口径', x.get('numeric_value_basis'))]
    h = '<div class="qi-body">' + ''.join(
        '<p><span class="lb">%s</span>：%s</p>' % (esc(k), esc(v).replace('\n', '<br>'))
        for k, v in parts if v is not None and str(v).strip())
    h += _qi_chips(x)
    basis = arr(x.get('basis_policy_ids')) + arr(x.get('basis_anchor_ids'))
    if basis:
        h += '<div class="qi-basis">口径依据（非锚点）：%s</div>' % esc('、'.join(basis))
    if all(_qi_num(x, k) is None for k in QI_SCEN):
        h += '<div class="qi-basis">该指标无可核实数值，按原口径不绘制图表（不编造数值）。</div>'
    return h + '</div>'


def _qi_lbl(px, py, t, anchor, fill, size, bold=False):
    return ('<text x="%.1f" y="%.1f" text-anchor="%s" fill="%s" font-size="%s"%s '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,PingFang SC,Microsoft YaHei,sans-serif" '
            'stroke="#fff" stroke-width="2.4" paint-order="stroke">%s</text>'
            % (px, py, anchor, fill, size, ' font-weight="700"' if bold else '', esc(t)))


def _qi_svg(inner, height):
    return '<svg viewBox="0 0 680 %d" role="img" xmlns="http://www.w3.org/2000/svg">%s</svg>' % (height, inner)


def _qi_diverging(x):
    """delta：发散条形图，0 为基准线，三情景各一根条；本图独立数值轴。"""
    vals = [_qi_num(x, k[0]) for k in QI_DELTA]
    if any(v is None for v in vals):
        return ''
    lo, hi = min(0, min(vals)), max(0, max(vals))
    pad = ((hi - lo) or 1) * 0.14
    L, R = 96.0, 632.0
    dlo, dhi = lo - pad, hi + pad

    def mp(v):
        return L + (v - dlo) / (dhi - dlo) * (R - L)

    x0 = mp(0)
    s = ('<line x1="%.1f" y1="15" x2="%.1f" y2="112" stroke="#9aa6b4" '
         'stroke-width="1" stroke-dasharray="4 3"/>' % (x0, x0))
    s += _qi_lbl(x0, 11, '0 基准', 'middle', '#8b97a6', 10.5)
    for i, (k, name, color) in enumerate(QI_DELTA):
        y = 26 + i * 32
        v, xp = vals[i], mp(vals[i])
        dv = txt((x.get('display_values') or {}).get(k))
        s += _qi_lbl(86, y + 16, name, 'end', '#5d6a7a', 12)
        bx, bw = min(x0, xp), max(2.0, abs(xp - x0))
        s += ('<rect x="%.1f" y="%d" width="%.1f" height="18" rx="3" fill="%s" opacity="0.92"/>'
              % (bx, y + 3, bw, color))
        if v >= 0:
            tx, anc, fill = (xp - 6, 'end', '#fff') if xp > 492 else (xp + 6, 'start', color)
        else:
            tx, anc = (xp + 6, 'start') if xp < 178 else (xp - 6, 'end')
            fill = color
        s += _qi_lbl(max(10, min(670, tx)), y + 16, dv, anc, fill, 12.5, True)
    return _qi_svg(s, 126)


def _qi_dumbbell(x):
    """level：哑铃图，一条数值轴三个并列估计值，同色相浅→深；本图独立数值轴。"""
    vals = [_qi_num(x, k[0]) for k in QI_LEVEL]
    if any(v is None for v in vals):
        return ''
    lo, hi = min(vals), max(vals)
    pad = ((hi - lo) or max(1.0, abs(hi) * 0.2)) * 0.18
    L, R, y = 70.0, 618.0, 68
    dlo, dhi = lo - pad, hi + pad

    def mp(v):
        return (L + R) / 2 if hi == lo else L + (v - dlo) / (dhi - dlo) * (R - L)

    xs = [mp(v) for v in vals]
    s = '<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#dbe5f0" stroke-width="2"/>' % (L, y, R, y)
    s += ('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#c3d4e6" stroke-width="1.5"/>'
          % (min(xs), y, max(xs), y))
    for i, (k, name, color) in enumerate(QI_LEVEL):
        xp, above = xs[i], i != 1
        dv = txt((x.get('display_values') or {}).get(k))
        anc = 'start' if xp < 132 else ('end' if xp > 556 else 'middle')
        s += _qi_lbl(xp, 30 if above else 100, name, anc, '#5d6a7a', 11)
        s += _qi_lbl(xp, 46 if above else 116, dv, anc, color, 12.5, True)
        s += '<circle cx="%.1f" cy="%d" r="8" fill="%s" stroke="#fff" stroke-width="2"/>' % (xp, y, color)
    return _qi_svg(s, 136)


def _qi_card(x, idx):
    dv = x.get('display_values') or {}
    delta = x.get('value_type') == 'delta'
    badge = ('<span class="qi-badge assume">含假设</span>' if x.get('is_assumption') is True
             else '<span class="qi-badge official">有官方数据依据</span>')
    typ = ('<span class="qi-type delta">delta · 相对基准变化率（发散条形图）</span>' if delta
           else '<span class="qi-type level">level · 独立估计值（哑铃图）</span>')
    vals = ''.join('<div class="qi-val %s"><div class="lb">%s</div><div class="n">%s</div></div>'
                   % (cls, name, esc(txt(dv.get(k))))
                   for k, name, cls in (('optimistic', '乐观', 'opt'),
                                        ('baseline', '基准', 'base'),
                                        ('pessimistic', '悲观', 'pes')))
    chart = _qi_diverging(x) if delta else _qi_dumbbell(x)
    cap = ('以 0 为基准线，向右为正向、向左为负向；三根条形分别对应乐观／基准／悲观，数值标于条形末端。'
           if delta else
           '同一数值轴上三个并列估计值，同一色相由浅至深；细线仅示意同组，不代表变化趋势。')
    h = '<div class="qi-card" data-vtype="%s" data-gap="%.3f">' % (esc(x.get('value_type')), _qi_gap(x))
    h += ('<div class="qi-head"><div class="qi-title"><span class="qi-rank">%d</span>'
          '<span class="qi-name">%s</span>%s%s</div><div class="qi-vals">%s</div></div>'
          % (idx + 1, esc(x.get('indicator_name')), typ, badge, vals))
    if chart:
        h += ('<div class="qi-chart">%s<div class="qi-caption">%s 单位：%s；本图独立数值轴，不与其它指标共用。</div></div>'
              % (chart, esc(cap), esc(x.get('unit') or '—')))
    h += ('<details class="qi-details"><summary><span class="arw">▸</span>查看测算依据</summary>'
          '%s</details>' % _qi_evidence(x))
    return h + '</div>'


def qi_block(final):
    """M4 三情景量化指标模块：结论优先、证明折叠、两类指标各自独立成图。"""
    R = final.get('reasoning') or {}
    qi = final.get('quantitative_impact') or R.get('quantitative_impact') or []
    if not qi:
        return ''
    ordered = _qi_sorted(qi)
    nd = sum(1 for x in ordered if x.get('value_type') == 'delta')
    nl = len(ordered) - nd
    head = ('<div class="qi-note"><b>阅读方式</b>：默认只显示结论数值、证据徽章与图表；'
            '<b>测算公式、方法论说明、敏感性区间文字与锚点政策引用</b>统一收在每张卡片底部的'
            '「查看测算依据」中，默认收起。列表按各指标自身口径下 <b>|乐观值 − 悲观值|</b> 的绝对差值降序排列，'
            '不按 JSON 原始顺序或名称排序；两类指标口径不同，<b>各自独立成图、不共享坐标轴</b>，跨指标数值不可直接比较。</div>')
    legend = ('<div class="qi-legend">'
              '<span><i style="background:#2f6fb0"></i><b>delta · 发散条形图</b>（%d 项）：0 为基准线，乐观蓝 / 基准灰 / 悲观红。</span>'
              '<span><i style="background:#4b8bc4"></i><b>level · 哑铃图</b>（%d 项）：三档并列估计值，同色相浅→深。</span>'
              '<span><i style="background:#fdf5e6;border:1px solid #ecd9b4"></i>含假设</span>'
              '<span><i style="background:#e9f5f1;border:1px solid #c9e7dd"></i>有官方数据依据</span></div>') % (nd, nl)
    cards = ''.join(_qi_card(x, i) for i, x in enumerate(ordered))
    return (h4('M4 · 三情景量化影响（结论优先 · %d 项指标）' % len(ordered))
            + head + legend + '<div class="qi-list">%s</div>' % cards)


# ============================== 主渲染 ==============================

def render_legacy(final, out_path):
    meta = final.get('meta') or {}
    scope = final.get('scope') or {}
    land = final.get('policy_landscape') or {}
    pols = land.get('policies') or []
    opps = final.get('opportunities') or []
    risks = final.get('risks') or []
    R = final.get('reasoning') or {}
    sc = R.get('scenarios') or {}
    rev = final.get('reverse_check') or {}
    val = final.get('validation') or {}
    issues = list(final.get('known_issues') or [])
    demo = bool(meta.get('demo_mode'))
    primary = ((meta.get('regions') or {}).get('primary') or {})
    title = (meta.get('input_text') or '政策研究')[:40]
    aidx = _action_index(sc)
    RENDER_ISSUES.clear()

    # 各节核心结论：数值全部来自已产出 JSON，仅搬运不新增研判；s1 有独立关键判断卡不注入
    _scene = sc.get('scenario_outcomes') or []
    _paths = sc.get('action_paths') or []
    _anchors = land.get('quantitative_anchors') or []
    _qi = final.get('quantitative_impact') or R.get('quantitative_impact') or []
    _qi_delta = sum(1 for x in _qi if x.get('value_type') == 'delta')
    _lg = land.get('lineage') or []
    _ms = R.get('multiple_streams') or {}
    _pmap = {p.get('id'): p for p in pols}
    SECTION_CONCLUSIONS.clear()
    SECTION_CONCLUSIONS.update({
        '2': '主区域 %s %s；核心赛道 %d 条，边界置信度 %s。' % (
            esc(primary.get('province')), esc(primary.get('city')),
            len(scope.get('core_segments') or []), esc(meta.get('boundary_confidence'))),
        '3': 'S1–Sn 赛道边界、关键词与时间窗取自 Phase 1；赛道拆分是后续双轨检索与机会风险覆盖率的分母。',
        '4': '政策全集 %d 条、量化锚点 %d 个；A/B 分级与官方原文可逐条筛选。' % (len(pols), len(_anchors)),
        '5': ('政策解读覆盖 PESTEL %d 维与多流派 %s；'
              '多流派分析结论独立成条（见四卡下方）。' % (
                  len(R.get('pestel_positioning') or []),
                  '、'.join(k for k in ('问题流', '政策流', '政治流') if _ms)))
             if _ms else '政策解读覆盖 PESTEL %d 维；本次未输出多流派分析字段。' % len(R.get('pestel_positioning') or []),
        '6': ('政策沿革 %d 条版本链，%d 条闭合；版本节点均可在 s4 政策全集回溯。' % (
            len(_lg), sum(1 for x in _lg if x.get('closed'))))
            if _lg else '本次未输出政策沿革数据（lineage 为空），版本信息以政策全集 status 字段为准。',
        '7': '六层传导链 %d 条；M3 情景推演给出 %d 个情景结论与路径动作。' % (
            len(R.get('logic_chains') or []), len(_scene)),
        '8': '机会 %d 条 / 风险 %d 条；矩阵格与卡片均标注「是否已有对应行动」（→A{n} 跳转 / 无对应行动缺口标记）。' % (
            len(opps), len(risks)),
        '9': '三情景量化指标 %d 项（delta %d / level %d），按 |乐观 − 悲观| 降序、结论与测算依据分层；'
             '标注为假设的数值不作事实依据。申报条件与免责声明见 s10。' % (
                 len(_qi), _qi_delta, len(_qi) - _qi_delta),
        '10': '申报条件以行动清单与政策官方原文为准；免责声明与全局声明去重后集中在本节。',
        '11': '行动 %d 条按短期 / 中期 / 长期三段时间轴排布，优先级两档配色，底部与 s8 双向链接；'
              '无明确时间信息的行动用定性表述，不编造月数。' % len(_paths),
        '12': '关键不确定性 %d 条；领先监测信号 %d 条（仅 contingent 动作）。' % (
            len(R.get('key_uncertainties') or []), len(sc.get('monitoring_signals') or [])),
        '13': '契约校验状态 %s；反向盲算隔离违规 = %s。' % (
            esc(val.get('status') or final.get('status')), esc(txt(rev.get('isolation_violated')))),
        '14': '已知问题 %d 条%s；内部质控分（如完整度评分）只在本节出现，不进入执行摘要。' % (
            len(issues), '＋渲染层核对缺口 %d 条' % len(RENDER_ISSUES) if RENDER_ISSUES else ''),
        '15': '官方来源 URL 去重 %d 个；量化锚点 %d 个集中列示，可逐条回溯。' % (
            len({p.get('source_url') for p in pols if p.get('source_url')}), len(_anchors)),
        '16': '本页为展示层渲染，不新增任何事实、政策条款或数值；结论与依据分层展示，附录备查。',
    })

    H = []
    H.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width,initial-scale=1">'
             '<title>%s · 政策研究报告</title><style>%s</style></head><body><div class="app">' % (esc(title), CSS))
    H.append('<aside class="side"><div class="brand">POLICY RESEARCH AGENT · v2.0</div><h1>%s<br>政策研究报告</h1><nav>' % esc(title))
    navs = [
        ('1', '执行摘要'), ('2', '研究范围与主体核验'), ('3', '赛道拆分与研究问题'),
        ('4', '政策全景与 A/B 证据'), ('5', '政策解读与拆解'), ('6', '政策沿革与版本比对'),
        ('7', '六层传导链与情景推演'), ('8', '机会与风险清单'), ('9', '财务影响速览'),
        ('10', '申报条件与免责声明'), ('11', '申报落地行动清单'), ('12', '关键不确定性'),
        ('13', '反向盲算与契约校验'), ('14', '质量控制与局限'), ('15', '证据附录与来源'),
        ('16', '报告使用须知')]
    for i, n in navs:
        H.append('<a href="#s%s">%s. %s</a>' % (i, i, esc(n)))
    H.append('</nav><div class="foot">版式契约 v3（16 节）<br>仅展示已产出 JSON，不新增结论</div></aside><main class="main">')

    H.append('<div class="hero"><div class="eyebrow">POLICY RESEARCH REPORT / H5</div>'
             '<h2>%s<br>适用的政策研究报告</h2>'
             '<p class="lead">由「总控协调官 → 6 个独立子智能体」串行流水线生成，按 16 节版式契约（v3）组织：'
             '范围口径 → 政策证据与沿革 → 机会风险 → 推演与量化 → 契约审校；含 A/B 证据分级、'
             '六层传导链、多流派分析、政策沿革版本链、行动路线图与三情景量化指标。</p><div class="chips">' % esc(title))
    _region = ' · '.join(dict.fromkeys(x for x in (primary.get('province'), primary.get('city')) if x)) or '未标注'
    chips = [('主区域 · %s' % _region, ''),
             ('输入类型 · %s' % (meta.get('input_type') or '未标注'), ''),
             ('主体置信度 · %s' % (meta.get('boundary_confidence') or '未标注'), ''),
             ('工作流 · %s' % (meta.get('workflow') or 'full'), ''),
             qc_chip(val, final)]
    if demo:
        chips.append(('演示模式 · 样例数据', 'warn'))
    if meta.get('web_search'):
        chips.append(('已启用联网检索', 'ok'))
    else:
        chips.append(('未启用联网检索 · 结论受限', 'warn'))
    for t, c in chips:
        H.append('<span class="chip %s">%s</span>' % (c, esc(t)))
    H.append('</div></div>')
    if demo:
        H.append('<div class="demo-banner">演示模式：本报告为内置样例数据，仅用于预览 H5 界面与报告样式，'
                 '<b>并非针对本次输入实时生成的政策结论</b>。填入 LLM API Key 并关闭演示模式即可实时生成。</div>')

    H.append('<div class="legend"><span><i style="background:#1f4e79"></i><b>已核实事实</b></span>'
             '<span><i style="background:#0f766e"></i><b>A 组判断</b></span>'
             '<span><i style="background:#6b7380"></i><b>B 组趋势参考</b></span>'
             '<span><i style="background:#a9740b"></i><b>推演／假设／演示占位</b></span></div>')

    # ---- s1 执行摘要（patch-1：客观指标卡 + 关键判断来源徽章；不放内部质控分） ----
    # 核心结论只搬运已产出条目（最高确定性机会 + 首要风险 + 首个高优先级行动），不做新研判
    _o1 = sorted([x for x in opps if x.get('description')],
                 key=lambda x: 0 if (x.get('certainty') or '') == '高' else 1)
    _r1 = sorted([x for x in risks if x.get('description')],
                 key=lambda x: 0 if (x.get('certainty') or '') == '高' else 1)
    _a1 = [a for a in (sc.get('action_paths') or []) if str(a.get('priority') or '') == '高']
    _c = []
    if _o1:
        _tg, _txt0 = split_tag(_o1[0].get('description'))
        _c.append('<div class="clrow"><span class="tag opp">机会 %s</span>%s%s</div>' % (
            esc(_o1[0].get('id')), esc(brief(_txt0, 76)),
            '　<span class="cite">依据 %s</span>' % esc('·'.join(arr(_o1[0].get('evidence_policy_ids'))))
            if arr(_o1[0].get('evidence_policy_ids')) else '　<span class="cite missing">来源待补</span>'))
    if _r1:
        _tg, _txt1 = split_tag(_r1[0].get('description'))
        _c.append('<div class="clrow"><span class="tag risk">风险 %s</span>%s%s</div>' % (
            esc(_r1[0].get('id')), esc(brief(_txt1, 76)),
            '　<span class="cite">依据 %s</span>' % esc('·'.join(arr(_r1[0].get('evidence_policy_ids'))))
            if arr(_r1[0].get('evidence_policy_ids')) else '　<span class="cite missing">来源待补</span>'))
    if _a1:
        _c.append('<div class="clrow"><span class="tag gray">先启动 %s</span>%s</div>' % (
            esc(_a1[0].get('action_id') or _a1[0].get('id') or '—'),
            esc(_qbrief(split_tag(_a1[0].get('action'))[1], 84))))
    if _c:
        SECTION_CONCLUSIONS['1'] = ''.join(_c)
    es = final.get('executive_summary') or ''
    b = []
    b.append(_metric_cards(opps, risks, pols, scope.get('core_segments') or []))
    b.append(_key_judgements(opps, risks, visible=3))
    high_acts = [a for a in (sc.get('action_paths') or [])
                 if str(a.get('priority') or '') == '高'][:3]
    if high_acts:
        b.append(h4('立即行动（高优先级前 3 项）') + '<div class="grid3">' + ''.join(
            '<div class="card"><span class="pri">高优先</span><div class="small" style="margin-top:8px;font-weight:600">%s</div></div>'
            % esc(brief(a.get('action'), 70)) for a in high_acts) + '</div>')
    if not demo and not meta.get('web_search'):
        b.append('<div class="notice">本次未启用联网检索：政策来源与条款未经官方详情页核实，'
                 '报告中标注「未核实」的内容不得作为申报或决策依据。</div>')
    if val.get('unresolved_divergence'):
        b.append('<div class="notice">存在未解决的反向盲算分歧（unresolved_divergence=true），详见第 13 节。</div>')
    if es:
        pass  # Phase 5 自检原文归入第 14 节（质量控制），不在执行摘要占用版面
    b.append(details('<span class="xsmall muted">报告元信息与数据口径</span>', kv([
        ('输入', esc(title)), ('输入类型', esc(meta.get('input_type'))),
        ('主区域', esc('%s %s' % (primary.get('province', ''), primary.get('city', '')))),
        ('主区域依据', esc(primary.get('basis'))), ('主体置信度', esc(meta.get('boundary_confidence'))),
        ('生成时间', esc(meta.get('generated_at'))), ('智能体版本', esc(meta.get('agent_version'))),
        ('校验状态', esc(val.get('status') or final.get('status')))])))
    H.append(sec(1, '执行摘要', '回答：这份报告最重要的判断是什么', ''.join(b)))

    # ---- s2 研究范围与主体核验 ----
    b = [h4('核验主体')]
    re_ = scope.get('resolved_entity') or {}
    b.append(card(kv([('企业/行业', esc(re_.get('company_name') or scope.get('industry_input'))),
                      ('统一社会信用代码', '<span class="mono">%s</span>' % esc(re_.get('unified_social_credit_code'))),
                      ('注册地', esc('%s %s' % (re_.get('registered_province', ''), re_.get('registered_city', '')))),
                      ('官方来源', link(re_.get('source'), '打开')),
                      ('边界置信度', '<span class="tag gold">%s</span>' % esc(scope.get('boundary_confidence'))),
                      ('模糊点', esc(scope.get('boundary_confidence_reason'))),
                      ('备注', esc(scope.get('note')))])))
    tw = scope.get('time_window') or {}
    b.append(h4('区域与时间窗') + '<div class="grid2">' +
             card('<b>regions.primary</b><div class="small muted" style="margin-top:5px">%s</div>' % esc(txt(primary))) +
             card('<b>%s ~ %s</b>' % (esc(tw.get('start')), esc(tw.get('end')))) + '</div>')
    H.append(sec(2, '研究范围与主体核验', '回答：这家主体是谁？政策适用口径对不对？', ''.join(b)))

    # ---- s3 赛道拆分与研究问题 ----
    segs_ = scope.get('core_segments') or []
    b = [h4('核心赛道（%d 条）' % len(segs_))]
    b.append(table(['ID', '赛道', '边界', '政策敏感度'], [
        ['<span class="mono">%s</span>' % esc(s.get('id')), '<b>%s</b>' % esc(s.get('name')),
         esc(brief(s.get('boundary'), 110)), esc(s.get('sensitivity'))] for s in segs_]))
    sub = []
    if scope.get('research_questions'):
        sub.append('<div style="margin-top:10px"><b class="small">研究问题</b>' +
                   ''.join('<div class="small">· %s</div>' % esc(x) for x in scope['research_questions']) + '</div>')
    if scope.get('metrics_dictionary'):
        sub.append('<div style="margin-top:10px"><b class="small">量化指标口径字典（%d 项，用于复核 s9）</b>' % len(scope['metrics_dictionary']) +
                   table(['指标', '口径/定义', '单位', '数据来源'],
                         [[esc(x.get('metric') or x.get('name')), esc(brief(x.get('definition'), 90)),
                           esc(x.get('unit')), esc(brief(x.get('data_source'), 90))] for x in scope['metrics_dictionary']]) + '</div>')
    if scope.get('clarification_options'):
        sub.append('<div style="margin-top:10px"><b class="small">澄清选项</b>' +
                   ''.join('<div class="small">· %s</div>' % esc(x) for x in scope['clarification_options']) + '</div>')
    if sub:
        b.append(details('<span class="xsmall muted">研究问题、指标口径与关键词（%d 项）</span>' % len(scope.get('metrics_dictionary') or []),
                         ''.join(sub) + '<div class="xsmall muted" style="margin-top:8px">关键词：' +
                         '；'.join('%s %s' % (esc(s.get('id')), tags(s.get('keywords'), 'gray')) for s in segs_) + '</div>'))
    H.append(sec(3, '赛道拆分与研究问题', '回答：研究边界画在哪里？用什么指标衡量？', ''.join(b)))

    # ---- s4 政策全景与 A/B 证据 ----
    b = []
    segs = sorted({x for p in pols for x in arr(p.get('segment_tags'))})
    a_cnt = sum(1 for p in pols if (p.get('group') or ('A' if p.get('applicability') == '直接适用' else 'B')) == 'A')
    b_cnt = len(pols) - a_cnt
    nat_cnt = sum(1 for p in pols if 'national' in str(p.get('region_scope') or ''))
    high_cnt = sum(1 for p in pols if p.get('relevance') == '高')
    b.append('<div class="metrics">' + ''.join(
        '<div class="metric"><div class="v">%s</div><div class="l">%s</div></div>' % (esc(v), esc(l))
        for l, v in [('政策条目', len(pols)), ('A 组直接适用', a_cnt), ('B 组趋势参考', b_cnt),
                     ('高相关', high_cnt), ('量化锚点', len(_anchors)),
                     ('国家级 / 主区域', '%d / %d' % (nat_cnt, len(pols) - nat_cnt))]) + '</div>')
    top = sorted(pols, key=lambda p: (0 if p.get('relevance') == '高' else 1,
                                      0 if (p.get('group') or 'A') == 'A' else 1))[:8]
    if top:
        b.append(h4('最相关的前 %d 条（其余见下方全部政策）' % len(top)) + '<div class="polist">' + table(
            ['ID', '政策', '发文机关', '组别', '相关性', '状态', '来源'],
            [['<span class="mono">%s</span>' % esc(p.get('id')), esc(brief(p.get('title'), 60)),
              esc(brief(p.get('issuing_body'), 34)),
              '<span class="tag %s">%s</span>' % ('a' if (p.get('group') or 'A') == 'A' else 'b',
                                                  esc(p.get('group') or 'A')),
              esc(p.get('relevance')), esc(p.get('status')), link(p.get('source_url'), '原文')] for p in top]) + '</div>')
    items = []
    for p in pols:
        g = p.get('group') or ('A' if p.get('applicability') == '直接适用' else 'B')
        searchable = ' '.join(txt(p.get(k)) for k in ('id', 'title', 'issuing_body', 'source_excerpt', 'effect_level')).lower()
        _stxt, _scls = _excerpt_source(p)
        body = (kv([('发文机关', esc(p.get('issuing_body'))), ('效力层级', esc(p.get('effect_level'))),
                    ('区域 / 适用性', esc(p.get('region_scope')) + ' / ' + esc(p.get('applicability'))),
                    ('状态 / 相关性', esc(p.get('status')) + ' / ' + esc(p.get('relevance'))),
                    ('发布 / 生效', esc(p.get('publish_date')) + ' / ' + esc(p.get('effective_date'))),
                    ('证据分级', esc(p.get('certainty_tier'))), ('来源', link(p.get('source_url'), '官方详情页'))])
                + '<div>%s%s <span class="src-tag %s">%s</span></div>'
                  '<div class="xsmall muted" style="margin-top:6px">原文摘录：</div>'
                  '<div class="quote">%s</div>'
                % (tags(p.get('segment_tags'), 'a'), tags(p.get('pestel_dimension'), 'violet'),
                   _scls, _stxt, esc(_excerpt_body(p, 220))))
        if g == 'B':
            body += '<div class="notice xsmall">来源 %s，仅为趋势参考，不得作为主判断或主测算依据。</div>' % esc(p.get('source_region'))
        items.append('<div class="pitem" data-search="%s" data-group="%s" data-segs="%s">%s</div>' %
                     (esc(searchable), esc(g), esc(','.join(arr(p.get('segment_tags')))),
                      details('<span class="tag %s">%s 组</span><span class="mono muted">%s</span> <b>%s</b>' %
                              ('a' if g == 'A' else 'b', esc(g), esc(p.get('id')), esc(p.get('title'))), body)))
    b.append(details('<span>全部政策明细（%d 条，可搜索 / 按组别与赛道筛选）</span><span class="xsmall muted">'
                     '点击展开后使用筛选</span>' % len(pols),
                     '<div class="controls"><input id="pq" type="text" placeholder="搜索政策 / 发文机关 / 原文…">'
                     '<select id="pg"><option value="">全部组别</option><option value="A">A 组</option><option value="B">B 组</option></select>'
                     '<select id="ps"><option value="">全部赛道</option>%s</select>'
                     '<button class="btn" id="preset">重置</button><span class="count" id="pcount">显示 %d 条</span></div>'
                     '<div id="plist">%s</div>' %
                     (''.join('<option value="%s">%s</option>' % (esc(s), esc(s)) for s in segs),
                      len(pols), ''.join(items))))
    if land.get('region_coverage_note'):
        b.append(card('<b class="small">主区域检索结论</b>' + para(land['region_coverage_note'])))
    if land.get('platform_attempts'):
        b.append(details('<span class="xsmall muted">官方平台尝试清单（%d 个）</span>' % len(land['platform_attempts']),
                         table(['平台', '栏目', '方式', '结果', '核实文件'], [
                             [esc(x.get('platform')), esc(x.get('column')), esc(x.get('attempt_method')),
                              esc(x.get('result')), esc(x.get('verified_files'))]
                             for x in land['platform_attempts']])))
    H.append(sec(4, '政策全景与 A/B 证据', '回答：有哪些政策？哪条能直接用？', ''.join(b)))

    # ---- s5 政策解读与拆解（patch-2：多流派分析结论） ----
    b = []
    pp = R.get('pestel_positioning') or []
    b.append(_ms_block(R))
    if pp:
        b.append(details('<span class="xsmall muted">PESTEL 六维定位（%d 条，含驱动性质与历史稳定性）</span>' % len(pp),
                         '<div class="grid2">' + ''.join(
                             '<div class="card"><span class="tag violet">%s</span>'
                             '<div class="small" style="margin-top:6px">%s</div>'
                             '<div class="xsmall muted" style="margin-top:6px">驱动性质：%s · 稳定性权重：%s</div>'
                             '<div class="xsmall muted" style="margin-top:5px">历史稳定性：%s</div>'
                             '<div class="xsmall muted" style="margin-top:5px">反例：%s</div></div>' % (
                                 esc(x.get('dimension') or x.get('policy_id')),
                                 esc(brief(x.get('rationale') or x.get('statement'), 260)),
                                 esc(x.get('policy_nature')), esc(x.get('stability_weight')),
                                 esc(brief(x.get('historical_stability'), 160)),
                                 esc(brief(x.get('counter_evidence'), 160)))
                             for x in pp) + '</div>'))
    H.append(sec(5, '政策解读与拆解', '回答：政策指向什么结构变化？窗口在哪？', ''.join(b)))

    # ---- s6 政策沿革与版本比对 ----
    b = [_lineage_block(land, pols)]
    H.append(sec(6, '政策沿革与版本比对', '回答：政策怎么变的？哪一版现在还管用？', ''.join(b)))

    # ---- s7 六层传导链与情景推演 ----
    b = []
    chains = R.get('logic_chains') or []
    if chains:
        blocks = []
        for c in chains:
            layers = c.get('logic_chain') or c.get('layers') or []
            inner = ''
            for i, L in enumerate(layers):
                inner += '<div class="layer"><span class="lb">L%d</span><span class="nm">%s</span>' \
                         '<div class="st">%s</div><div class="xsmall muted" style="margin-top:4px">条款依据：%s</div></div>' % (
                             i + 1, esc(L.get('node') or L.get('name')), esc(L.get('content') or L.get('statement')),
                             esc(L.get('clause_evidence') or L.get('transmission_variable')))
                tv = L.get('transmission_variable')
                if tv:
                    inner += '<div class="trans">↳ 层间传导变量：%s</div>' % esc(tv)
            blocks.append(details('<span class="tag a">%s</span> 六层传导链 <span class="tag gray">%d 层</span>' %
                                  (esc(c.get('policy_id')), len(layers)), inner))
        b.append(h4('六层传导链（%d 条，点击展开逐层看）' % len(chains)) + ''.join(blocks))
    sub = []
    if sc.get('swing_variable_analysis'):
        sub.append('<div style="margin-top:10px"><b class="small">摆动变量</b>' + kv([
            ('变量', esc(brief(sc['swing_variable_analysis'].get('swing_variable'), 120))),
            ('为何够格', esc(brief(sc['swing_variable_analysis'].get('why_qualifies'), 160))),
            ('已排除', esc(txt(sc['swing_variable_analysis'].get('excluded_uncertainties'))))]) + '</div>')
    if sc.get('divergence_mapping'):
        dm = sc['divergence_mapping']
        sub.append('<div style="margin-top:10px"><b class="small">分歧映射</b>' + kv([
            ('一致层', esc(txt(dm.get('shared_layers')))),
            ('分歧起始层', esc(dm.get('divergence_start_layer'))),
            ('各情景分叉', para(dm.get('divergence_by_scenario')))]) + '</div>')
    lk = sc.get('scenario_linkage') or []
    if lk:
        sub.append('<div style="margin-top:10px"><b class="small">情景联动（默认滑向基准）</b>' + table(
            ['情景', '未触发时的落点'],
            [[esc(x.get('scenario_id')), esc(x.get('fallback_if_not_triggered'))] for x in lk]) + '</div>')
    if sub:
        b.append(details('<span class="xsmall muted">推演参数：摆动变量、分歧映射与情景联动</span>', ''.join(sub)))
    H.append(sec(7, '六层传导链与情景推演', '回答：政策怎么一层层传到企业？', ''.join(b)))

    # ---- s8 机会与风险清单（patch-3） ----
    b = [_matrix_block(opps, risks, aidx), _stakeholders_block(R)]
    if opps or risks:
        b.append(details('<span class="xsmall muted">机会与风险完整卡片（%d 条，含反例检验与证据依据）</span>'
                         % (len(opps) + len(risks)),
                         '<div class="grid2">' + ''.join(_orcard(x, '机会', aidx) for x in opps)
                         + ''.join(_orcard(x, '风险', aidx) for x in risks) + '</div>'))
    ms = final.get('matrix_summary') or {}
    if ms:
        b.append(details('<span class="xsmall muted">上游矩阵汇总（matrix_summary）</span>', '<div class="grid3">' + ''.join(
            '<div class="card"><b>%s</b><div class="small muted" style="margin-top:6px">%s</div></div>'
            % (esc(k), esc(txt(v))) for k, v in ms.items()) + '</div>'))
    H.append(sec(8, '机会与风险清单', '回答：哪些机会风险最该管？有没有人管？', ''.join(b)))

    # ---- s9 财务影响速览 ----
    b = [qi_block(final)]
    if R.get('sensitivity'):
        b.append(details('<span class="xsmall muted">敏感性分析（完整表述）</span>', card(para(R['sensitivity']))))
    if not (final.get('quantitative_impact') or R.get('quantitative_impact')):
        b.append('<div class="notice">本次输出未包含三情景量化指标（quantitative_impact 为空），'
                 '财务影响以各政策量化锚点为准（见 s15）。</div>')
    H.append(sec(9, '财务影响速览', '回答：三种情景下影响差多少？', ''.join(b)))

    # ---- s10 申报条件与免责声明（dedup） ----
    b = []
    acts = sc.get('action_paths') or []
    cond_rows = []
    for a in acts:
        cond = (a.get('eligibility') or a.get('acceptance_criteria')
                or a.get('required_documents') or a.get('window') or a.get('responsible_body'))
        if cond:
            cond_rows.append([esc(a.get('action_id') or a.get('id') or '—'),
                              esc(brief(a.get('action'), 46)),
                              esc(brief(cond, 110)),
                              esc(brief(a.get('responsible_body') or '—', 44)),
                              esc(brief(a.get('window') or a.get('timeline') or '—', 40))])
    if cond_rows:
        b.append(h4('申报条件 / 责任部门 / 时间节点（按行动汇总）') + '<div class="conlist">' + table(
            ['行动 id', '行动', '条件/验收', '责任部门', '时间'], cond_rows) + '</div>')
    else:
        b.append('<div class="notice">本次行动输出未附申报条件明细（action_paths 未提供 eligibility / '
                 'required_documents / window 字段）；申报条件以 s4 各政策官方原文与 s15 来源 URL 为准，'
                 '本页不代替官方申报口径。</div>')
    # 免责声明去重：与 legend / 全局声明重复的文本只保留一次
    disclaimers = []
    _seen = set()
    for t in (['未启用联网检索：政策来源与条款未经官方详情页核实，不得作为申报或决策依据。'
                if not meta.get('web_search') else None] +
              [str(x) for x in issues if '未' in str(x) and '核实' in str(x)]):
        if t and t not in _seen:
            _seen.add(t)
            disclaimers.append(t)
    if disclaimers:
        b.append(details('<span class="xsmall muted">免责声明（%d 条，已与其他章节去重）</span>' % len(disclaimers),
                         ''.join('<div class="small">· %s</div>' % esc(x) for x in disclaimers) +
                         '<div class="xsmall muted" style="margin-top:6px">与全局声明相同的文本不在此重复展示；'
                         '财务影响测算口径与假设见 s9，局限全文见 s14。</div>'))
    H.append(sec(10, '申报条件与免责声明', '回答：申报要什么条件？边界在哪？', ''.join(b)))

    # ---- s11 申报落地行动清单（patch-4：时间轴路线图） ----
    b = [_roadmap_block(sc, {x.get('id') for x in opps} | {x.get('id') for x in risks})]
    sig = sc.get('monitoring_signals') or []
    if sig:
        b.append(details('<span class="xsmall muted">领先监测信号（%d 条，仅 contingent 动作）</span>' % len(sig),
                         table(['contingent 动作', '监测指标', '为何是最早代理信号'],
                               [[esc(x.get('contingent_action')), esc(x.get('monitoring_indicator')),
                                 esc(x.get('why_earliest_proxy'))] for x in sig])))
    H.append(sec(11, '申报落地行动清单', '回答：先做什么、什么时候做？', ''.join(b)))

    # ---- s12 关键不确定性与情景结果 ----
    b = []
    outs = sc.get('scenario_outcomes') or []
    if outs:
        b.append(h4('三情景结论（%d 个）' % len(outs)) + '<div class="scent">' + table(['情景', 'L5/L6 结果', '资源含义', '路径关键词'], [
            [esc(x.get('scenario_id')), esc(brief(x.get('l5_l6_outcome'), 160)),
             esc('稀缺：%s；贬值：%s；暴露：%s' % (
                 brief(txt((x.get('resource_implication') or {}).get('scarce_and_valuable')), 40),
                 brief(txt((x.get('resource_implication') or {}).get('devaluing')), 40),
                 brief(txt((x.get('resource_implication') or {}).get('risk_exposed')), 40))),
             esc(x.get('path_keyword'))] for x in outs]) + '</div>')
    ku = R.get('key_uncertainties') or []
    sub = []
    acts = sc.get('action_paths') or []
    if acts:
        sub.append('<div><b class="small">路径动作总表（%d 条）</b>' % len(acts) + table(['id', '动作', '类别', '时间线', '资源投入'], [
            ['<span class="mono">%s</span>' % esc(x.get('action_id') or x.get('id') or '—'),
             esc(brief(x.get('action'), 90)),
             '<span class="tag gold">%s</span>' % esc(CAT_CN.get(x.get('category'), x.get('category') or '—')),
             esc(x.get('timeline')), esc(brief(x.get('resource_input'), 60))] for x in acts]) + '</div>')
    if ku:
        sub.append('<div style="margin-top:10px"><b class="small">关键不确定性（%d 条）</b>%s</div>' % (
            len(ku), ''.join(details(
                '<span class="mono">%s</span> %s' % (esc(x.get('id')), esc(brief(x.get('statement'), 90))),
                kv([('需补证据', esc(x.get('evidence_needed'))), ('来源阶段', esc(x.get('source_phase'))),
                    ('关联政策', tags(x.get('related_policy_ids'), 'gray')),
                    ('可由主区域文件解决', esc(x.get('resolvable_by_primary_region_files')))])) for x in ku)))
    if sub:
        b.append(details('<span class="xsmall muted">路径动作总表与关键不确定性</span>', ''.join(sub)))
    H.append(sec(12, '关键不确定性与情景结果', '回答：什么会改变结论？该盯什么信号？', ''.join(b)))

    # ---- s13 反向盲算与契约校验 ----
    b = []
    b.append('<div class="%s">反向盲算严格隔离：仅输入 scope + policies，绝不接受推演或机会风险结论。%s</div>' %
             ('cardx' if not rev.get('isolation_violated') else 'notice',
              '本次隔离未被破坏。' if rev.get('reverse_swing_variable') else '本次未运行反向盲算（字段为空）。'
              if not rev.get('isolation_violated') else '本次隔离被破坏，结果作废。'))
    rn = rev.get('reverse_policy_natures') or []
    rn_rows = [[esc(x.get('policy_id')), esc(x.get('reverse_policy_nature')), esc(brief(x.get('reverse_rationale'), 120))] for x in rn]
    checks = val.get('checks') or {}
    rejs = (val.get('rejections') or []) + (val.get('local_rule_rejections') or [])
    sub = [kv([('独立摆动变量', esc(brief(rev.get('reverse_swing_variable'), 120))),
               ('独立判断依据', esc(brief(rev.get('reverse_why_qualifies'), 140))),
               ('分歧已解决', esc(not val.get('unresolved_divergence')))])]
    if rn_rows:
        sub.append('<div style="margin-top:8px"><b class="small">独立驱动性质（%d 条）</b>' % len(rn_rows) +
                   table(['政策', '独立驱动性质', '独立理由'], rn_rows) + '</div>')
    if R.get('divergence_note'):
        sub.append('<div style="margin-top:8px"><b class="small">分歧回应</b>' + para(R['divergence_note']) + '</div>')
    if checks:
        sub.append('<div style="margin-top:8px"><b class="small">契约检查（%d 项）</b>' % len(checks) +
                   ''.join('<span class="tag %s">%s · %s</span>' % ('opp' if v == 'PASS' else 'risk', esc(k), esc(v))
                           for k, v in checks.items()) + '</div>')
    if rejs:
        sub.append('<div style="margin-top:8px"><b class="small">驳回 / 待修正项（%d 条）</b>' % len(rejs) +
                   table(['责任 Agent', '字段', '规则', '详情'],
                         [[esc(x.get('source_agent')), esc(x.get('field')), esc(x.get('rule_violated')), esc(x.get('detail'))]
                          for x in rejs]) + '</div>')
    b.append(details('<span class="xsmall muted">独立推演结果、契约检查明细与驳回记录</span>', ''.join(sub)))
    H.append(sec(13, '反向盲算与契约校验', '回答：换个独立视角重算，结论还成立吗？', ''.join(b)))

    # ---- s14 质量控制与局限（内部质控分只在此出现） ----
    b = []
    qc = final.get('completeness_score') or meta.get('completeness_score')
    if qc is not None:
        SECTION_CONCLUSIONS['14'] = (
            '内部质控自评分 %s 属生成侧自评，不代表结论可信度；已知局限 %d 条、渲染层缺口 %d 条，'
            '均在下方逐条列出。' % (esc(qc), len(issues), len(RENDER_ISSUES)))
    if issues:
        b.append(h4('已知问题与局限（%d 条）' % len(issues)) + '<div class="notice">' +
                 ''.join('<div>· %s</div>' % esc(x) for x in issues) + '</div>')
    if RENDER_ISSUES:
        b.append(h4('渲染层核对发现的缺口（%d 条）' % len(RENDER_ISSUES)) + '<div class="notice">' +
                 ''.join('<div>· %s</div>' % esc(x) for x in RENDER_ISSUES) +
                 '<div class="xsmall muted" style="margin-top:6px">按版式契约 v3：规则所需字段缺失时走 fallback、'
                 '显示「来源待补」并在此登记，不编造数据。</div></div>')
    if es:
        b.append(details('<span class="xsmall muted">生成侧契约审校结论（Phase 5 自检原文）</span>', para(es)))
    H.append(sec(14, '质量控制与局限', '回答：这份报告哪里还不可靠？', ''.join(b)))

    # ---- s15 证据附录与来源 ----
    b = []
    urls = {}
    for p in pols:
        u = p.get('source_url')
        if u:
            urls.setdefault(u, []).append(p.get('id'))
    b.append(h4('官方来源 URL（去重 %d 个）' % len(urls)) + table(['#', '官方详情页', '引用政策'],
        [[i + 1, link(u, u), tags(v, 'a')] for i, (u, v) in enumerate(sorted(urls.items()))]))
    qa = land.get('quantitative_anchors') or []
    if qa:
        b.append(h4('量化锚点（%d 个）' % len(qa)) + table(['ID', '锚点', '数值', '单位', '政策', '组别', '原文 / 来源'], [
            ['<span class="mono">%s</span>' % esc(x.get('anchor_id') or x.get('id')),
             esc(x.get('anchor') or x.get('name')), '<b>%s</b>' % esc(x.get('value')),
             esc(x.get('unit')), esc(x.get('policy_id')),
             '<span class="tag %s">%s</span>' % ('a' if x.get('group') == 'A' else 'b', esc(x.get('group'))),
             '<div class="xsmall">%s</div>%s' % (esc(x.get('quote') or x.get('evidence_quote')),
                                                link(x.get('source_url'), '官方原文'))] for x in qa[:80]]))
    b.append(h4('各阶段原始 JSON') + ''.join(details('<span>%s.json</span>' % esc(n),
        '<div class="xsmall muted">可在「下载最终 JSON」与各阶段原文接口中获取完整结构；本页只做展示层搬运。</div>')
        for n in ['scope', 'policies', 'opportunities_risks', 'reasoning', 'reverse_check', 'validation', 'final_report']))
    H.append(sec(15, '证据附录与来源', '回答：每条结论能追到哪个官方来源？', ''.join(b)))

    # ---- s16 报告使用须知 ----
    b = [card(''.join([
        '<div>· 本页为展示层渲染，<b>不新增任何事实、政策条款或数值</b>；全部内容来自本次流水线已产出并经契约校验的 JSON。</div>',
        '<div>· 结论与依据分层：三情景量化卡片默认只显示结论数值，公式与说明收在「查看测算依据」；'
        '多流派、反例检验、政策原文同理按需展开。</div>',
        '<div>· 证据分级：A 组（直接适用）为主判断依据；B 组（其他省市）仅作趋势参考；'
        '标注「未核实／待核实／演示占位」的内容不得作为申报或决策依据。</div>',
        '<div>· 章节导航：s1 摘要 → s4/s5/s6 政策证据·解读·沿革 → s8/s9 机会风险·财务影响 → '
        's10/s11 申报条件与行动路线图 → s12–s15 不确定性·校验·局限·证据。</div>',
        '<div>· 交叉链接：s8 矩阵中的 →A{n} 与 s11 卡片底部的「对应 R/O」互为双向跳转。</div>']))]
    H.append(sec(16, '报告使用须知', '回答：这份报告该怎么用、不能怎么用？', ''.join(b)))

    H.append('<div class="footer">政策研究智能体 v2.0 · H5 报告｜版式契约 v3（16 节）｜生成时间 %s｜'
             '仅渲染已产出 JSON，不新增任何分析结论'
             '<div style="margin-top:5px">可用浏览器打印为 PDF；<button class="btn" onclick="window.print()">打印 / 另存 PDF</button></div></div>' %
             esc(meta.get('generated_at')))
    H.append('</main></div><script>%s</script></body></html>' % JS)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write(''.join(H))
    return out_path


# ============ 新版面 render：五阶段叙事线（参照《能源电力政策研判（新版面）》） ============
# 结构：核心洞察 → 01 扫描分类 → 02 解读拆解(PESTEL+多流派) → 03 传导链(政策→行业→企业)
#       → 04 风险机会矩阵(干系人) → 05 情景分支与实施路径(三情景) → 06 行动路线 → 质量与局限
# 只搬运已产出 JSON，不新增事实、条款与数值；字段缺失走 fallback 不臆造。

_MINI_JS = """
const navs=[].slice.call(document.querySelectorAll('.side nav a'));
if(navs.length){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)navs.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id))}),{rootMargin:'-10% 0% -80% 0%'});
document.querySelectorAll('section[id]').forEach(s=>io.observe(s));}
"""

_BLOCKS = [
    ('s-summary', '', '执行摘要', '汇总全部阶段的关键判断，不新增结论'),
    ('s-landscape', '阶段一', '政策扫描与分类', '数据源：policy_landscape.policies'),
    ('s-interpret', '阶段二', '政策解读与拆解', 'PESTEL 六维 + 多流派研判'),
    ('s-lineage', '阶段二 · 下', '政策沿革与版本比对', '政策怎么改、现在哪版有效'),
    ('s-chain', '阶段三', '传导链分析', '政策 → 行业 → 企业 逐层推演'),
    ('s-risk', '阶段四', '风险机会矩阵', '数据源：opportunities + risks + stakeholders'),
    ('s-scenario', '阶段五', '情景分支与实施路径', '数据源：scenarios + key_uncertainties'),
    ('s-actions', '阶段五 · 下', '行动路线图', '数据源：scenarios.action_paths'),
]


def _tidy(s):
    """结论文本收尾清理：合并重复句号/分号，避免「。。」「；。」。"""
    s = re.sub(r'([。；]){2,}', lambda m: m.group(1)[0], str(s or ''))
    return s


def _blk(sid, stage, title, src, concl, body, label='核心结论'):
    eb = '<div class="eb"><i></i>%s</div>' % esc(stage) if stage else ''
    concl = _tidy(concl) if concl else concl
    head = ('<div class="okbox"><b>%s</b>：%s</div>' % (esc(label), concl)) if concl else ''
    return ('<section id="%s"><div class="sec-head">%s<h3>%s</h3><span class="hint">%s</span></div>%s</section>'
            % (sid, eb, esc(title), esc(src), head + body))


def _qbrief(v, n):
    s = brief(v, n)
    if s.count('「') > s.count('」'):
        s += '」'
    return s


def _excerpt_source(p):
    """返回政策的原文来源类型标签：官方原文 / 检索片段 / 未取得原文。"""
    note = str(p.get('_fetch_note') or '')
    if p.get('full_excerpt'):
        return ('官方原文', 'ok')
    if '检索摘要片段' in note:
        return ('检索片段', 'mid')
    if note:
        return ('未取得原文', 'warn')
    return ('来源未标注', 'warn')


def _excerpt_body(p, limit=46):
    """正文优先取抓取的 full_excerpt，退回检索片段 source_excerpt；占位符视为无。"""
    v = clean_sentence(p.get('full_excerpt') or p.get('source_excerpt'), limit + 40)
    if _is_placeholder_text(v):
        return ''
    return brief(v, limit)


def _is_placeholder_text(v):
    s = str(v or '').strip()
    return (not s) or any(ph in s for ph in ('未联网检索', '未取得官方原文', '未核实', '未标注'))


def _k_block(opps, risks):
    """执行摘要 K1–Kn 关键判断：只展示确定性「高」的条目，中/低一律不在此展示。"""
    # 严格按用户要求：仅确定性为「高」才展示；无高确定性条目时整块不显示
    picks = ([('机会', x) for x in sorted(opps, key=lambda o: certainty_rank(o.get('certainty')))
              if (x.get('certainty') or '').strip() == '高'][:3] +
             [('风险', x) for x in sorted(risks, key=lambda o: certainty_rank(o.get('certainty')))
              if (x.get('certainty') or '').strip() == '高'][:3])
    if not picks:
        return ''
    out = []
    for i, (kind, x) in enumerate(picks):
        tg, body = split_tag(x.get('description'))
        out.append(('<div class="kjd"><div class="kjh"><span class="kn">K%d</span>'
                    '<span class="kp">确定性 高</span>%s</div>'
                    '<div class="kjt">%s</div>'
                    '<div class="kjf"><span class="tag %s">%s %s</span></div></div>'
                    % (i + 1, _cite_badge(x.get('evidence_policy_ids')),
                       esc(_qbrief(clean_sentence(body, 170), 150)),
                       'opp' if kind == '机会' else 'risk', kind, esc(x.get('id') or ''))))
    return '<div class="card kjwrap">%s</div>' % ''.join(out)


def _dist_bars(rows, title, note=''):
    """通用横向条形图：rows=[(标签, 数值)]。纯 CSS，不引图表库。"""
    rows = [(str(a), int(b)) for a, b in rows if b]
    if not rows:
        return ''
    mx = max(b for _, b in rows) or 1
    h = ['<div class="chartbox"><h5>%s</h5>' % esc(title)]
    if note:
        h.append('<div class="chart-note">%s</div>' % esc(note))
    for label, n in rows:
        w = int(round(n * 100.0 / mx))
        h.append('<div class="barrow"><span class="bl">%s</span><span class="bt">'
                 '<span class="bf" style="width:%d%%"></span></span><span class="bv">%d</span></div>'
                 % (esc(brief(label, 18)), max(4, w), n))
    h.append('</div>')
    return ''.join(h)


def _seg_bars(pols, segs):
    """维度一 · 赛道：覆盖条数热力卡片（数量越多颜色越深）。"""
    rows = [(('%s %s' % (s.get('id'), s.get('name') or '')).strip(),
             sum(1 for p in pols if s.get('id') in arr(p.get('segment_tags')))) for s in segs]
    rows = [(a, int(b)) for a, b in rows if b]
    if not rows:
        return ''
    mx = max(b for _, b in rows) or 1
    h = ['<div class="chartbox"><h5>维度一 · 各赛道政策覆盖</h5>',
         '<div class="chart-note">颜色越深覆盖越多 · 数字为该赛道条数</div><div class="seg-heat">']
    for label, n in rows:
        lvl = 1 if n <= mx * 0.34 else (2 if n <= mx * 0.67 else 3)
        parts = label.split(' ', 1)
        sid = parts[0]
        nm = parts[1] if len(parts) > 1 else ''
        h.append('<div class="seg-cell lv%d"><span class="sc-id">%s</span>'
                 '<span class="sc-nm">%s</span><span class="sc-n">%d</span></div>'
                 % (lvl, esc(sid), esc(brief(nm, 14)), n))
    h.append('</div></div>')
    return ''.join(h)


def _time_bars(pols):
    """维度二 · 时间：按发布/生效年份统计的竖向柱状图；无年份的归入「时间未核实」。"""
    from collections import Counter
    c = Counter()
    for p in pols:
        d = str(p.get('publish_date') or p.get('effective_date') or '').strip()
        m = re.search(r'(20\d{2})', d)
        c[m.group(1) if m else '时间未核实'] += 1
    order = [k for k in sorted(c) if k != '时间未核实'] + (['时间未核实'] if '时间未核实' in c else [])
    rows = [(k, c[k]) for k in order]
    if not rows:
        return ''
    mx = max(b for _, b in rows) or 1
    h = ['<div class="chartbox"><h5>维度二 · 政策发布时间分布</h5>',
         '<div class="chart-note">按发布/生效年份统计 · 无确切时间单列</div><div class="vbar">']
    for label, n in rows:
        hpct = max(8, int(round(n * 100.0 / mx)))
        unk = '未核实' in label or '未标' in label
        h.append('<div class="vb-col%s"><span class="vb-n">%d</span>'
                 '<div class="vb-track"><div class="vb-fill" style="height:%d%%"></div></div>'
                 '<span class="vb-lb">%s</span></div>'
                 % (' unk' if unk else '', n, hpct, esc(brief(label, 7))))
    h.append('</div></div>')
    return ''.join(h)


def _type_bars(pols):
    """维度三 · 政策类型：按效力层级统计的环形占比图 + 图例。"""
    from collections import Counter
    c = Counter()
    for p in pols:
        c[str(p.get('effect_level') or '未标注').strip()] += 1
    rows = sorted(c.items(), key=lambda x: -x[1])
    if not rows:
        return ''
    total = sum(b for _, b in rows) or 1
    palette = ['#2c5f46', '#4c8b68', '#7fb492', '#a8cdb5', '#c9dfd0', '#8d877b', '#b9b2a4', '#5c8570']
    segs_css, legend = [], []
    acc = 0.0
    for i, (label, n) in enumerate(rows):
        pct = n * 100.0 / total
        color = palette[i % len(palette)]
        segs_css.append('%s %.2f%% %.2f%%' % (color, acc, acc + pct))
        acc += pct
        legend.append('<div class="pie-lg"><i style="background:%s"></i>'
                      '<span class="pl-nm">%s</span><span class="pl-n">%d</span></div>'
                      % (color, esc(brief(label, 12)), n))
    h = ['<div class="chartbox"><h5>维度三 · 政策类型分布</h5>',
         '<div class="chart-note">按效力层级统计 · 环形为各类占比</div>',
         '<div class="pie-wrap"><div class="pie-donut" style="background:conic-gradient(%s)">'
         '<div class="pie-hole"><b>%d</b><span>政策总数</span></div></div>'
         '<div class="pie-legend">%s</div></div></div>'
         % (','.join(segs_css), len(pols), ''.join(legend))]
    return ''.join(h)


def _lvl_line(pols):
    d = {}
    for p in pols:
        k = p.get('effect_level') or '未标注'
        d[k] = d.get(k, 0) + 1
    if not d:
        return ''
    return card('<div class="small"><b>效力层级分布</b>：' + ' · '.join(
        '%s %d' % (esc(k), v) for k, v in sorted(d.items(), key=lambda x: -x[1])) + '</div>')


def _short_name(x, n=16):
    """从条目描述里取短名（去掉【…】证据前缀），供矩阵格内展示。"""
    _tg, body = split_tag(x.get('description'))
    body = ' '.join(body.split())
    # 优先取第一个逗号/分号前的短语
    for sep in ('，', '；', ',', '、'):
        part = body.split(sep)[0].strip()
        if 4 <= len(part) <= n:
            return brief(part, n)
    return brief(body, n)


def _rating_index(final, opps, risks):
    """合并显式评级：优先取 report_data.risk_matrix.items（成员产出的可追溯评级），
    其次取条目自带 likelihood/impact；返回 {id: (likelihood, impact, basis)}。"""
    idx = {}
    rm = final.get('risk_matrix') or {}
    for it in (rm.get('items') or []):
        iid = it.get('id')
        if iid and it.get('likelihood') and it.get('impact'):
            idx[iid] = (txt(it['likelihood']), txt(it['impact']), txt(it.get('basis')))
    for x in (opps + risks):
        iid = x.get('id')
        if iid and iid not in idx and x.get('likelihood') and x.get('impact'):
            idx[iid] = (txt(x['likelihood']), txt(x['impact']), '条目自带评级')
    return idx, txt(rm.get('method'))


def _matrix_from_ratings(items, aidx, idx, lv=('高', '中', '低')):
    """按「可能性 × 影响度」二维计算落格；每个格子显示条目、短名、→A 行动链接或缺口标记。"""
    cells = {(p, i): [] for p in lv for i in lv}
    uncategorized = []
    for x in items:
        iid = x.get('id')
        r = idx.get(iid)
        if not r or r[0] not in lv or r[1] not in lv:
            uncategorized.append(x)
            continue
        cells[(r[0], r[1])].append((x, r[2]))
    h = ['<div class="mx calc-mx"><div class="hd rowhd"></div>'
         + ''.join('<div class="hd">影响 · %s</div>' % i for i in lv)]
    for p in lv:
        h.append('<div class="hd rowhd">可能性 · %s</div>' % p)
        for i in lv:
            cell = cells[(p, i)]
            cls = 'mx-cell'
            if p == '高' and i == '高':
                cls += ' hot'
            elif (p == '高' and i == '中') or (p == '中' and i == '高'):
                cls += ' warm'
            if not cell:
                h.append('<div class="%s empty">—</div>' % cls)
                continue
            rows = []
            for x, basis in cell:
                iid = x.get('id')
                acts_ = aidx.get(iid) or []
                links = ''.join('<a class="alink" href="#act-%s">→%s</a>' % (esc(a), esc(a)) for a in acts_)
                if not links:
                    links = '<span class="noact">无对应行动</span>'
                rows.append('<div class="mx-item"><b class="mono">%s</b> %s %s'
                            '<div class="xsmall muted" style="width:100%%">%s</div></div>'
                            % (esc(iid), esc(_short_name(x)), links, esc(brief(basis, 66))))
            h.append('<div class="%s">%s</div>' % (cls, ''.join(rows)))
    h.append('</div>')
    return ''.join(h), cells, uncategorized


def _chain_card(c):
    """参照新版面参考图：链名 + 置信 → 三节点横向链（起点/传导变量/若…结果）→ 证据折叠。"""
    layers = c.get('logic_chain') or []
    L = [dict(x) for x in layers]
    head2 = L[1] if len(L) > 1 else (L[0] if L else {})
    tv = c.get('transmission_variables') or []
    if isinstance(tv, dict):
        tv = [v for v in tv.values()]
    tvtxt = '、'.join(brief(x, 36) for x in arr(tv))
    if not tvtxt:
        tvtxt = '；'.join(brief(x.get('content'), 40) for x in L[2:4] if x.get('content'))
    if not tvtxt:
        tvtxt = '层间传导变量见下方 L1–L6 明细'
    _STAGE_CN = {'条款': '政策条款', '直接主体': '直接主体·行业', '结构变化': '结构变化·行业',
                 '价值链': '价值链节点', '企业影响': '企业影响', '战略结果': '战略结果',
                 '行业': '行业变化', '企业要素': '企业影响'}
    _n2 = head2.get('stage') or head2.get('node') or '机制变化'
    start_node = _STAGE_CN.get(_n2, _n2)
    start_txt = (L[0].get('content') if L else '') or ''
    if len(L) > 1 and L[1].get('content'):
        start_txt = (start_txt + '；' + L[1].get('content')).strip('；')
    end_layers = [x for x in L[-2:] if x.get('content')]
    end_head = '；'.join(_STAGE_CN.get(x.get('stage') or x.get('node'), x.get('stage') or x.get('node') or '企业端结果')
                        for x in end_layers) or '企业端结果'
    end_txt = '；'.join(brief(x.get('content'), 88) for x in end_layers) or chain_fallback_text(c)
    name = brief(L[2].get('content') if len(L) > 2 else (L[0].get('content') if L else '传导链'), 26)
    flow = ('<div class="chainflow">'
            '<div class="cnode"><div class="cn">起点 · %s</div><div class="cb">%s</div></div>'
            '<div class="carr">→</div>'
            '<div class="cnode"><div class="cn">传导变量</div><div class="cb">%s</div></div>'
            '<div class="carr">→</div>'
            '<div class="cnode risk"><div class="cn">若 %s</div><div class="cb">%s</div></div>'
            '</div>') % (esc(brief(start_node, 22)), esc(brief(start_txt, 110)),
                         esc(brief(tvtxt, 90)), esc(brief(end_head, 26)), esc(end_txt))
    full = ''
    for i, x in enumerate(L):
        full += ('<div class="lay"><div class="layh"><span class="lb">L%d</span>'
                 '<span class="nm">%s</span></div><div class="st">%s</div>%s</div>'
                 % (i + 1, esc(_STAGE_CN.get(x.get('stage') or x.get('node'), x.get('stage') or x.get('node'))),
                    esc(x.get('content')),
                    ('<div class="xsmall muted" style="margin-top:4px">条款依据：%s</div>'
                     % esc(brief(x.get('clause_evidence'), 160))) if x.get('clause_evidence') else ''))
    conf = c.get('confidence') or '未标注'
    return ('<div class="card chaincard"><div class="chh"><span class="chainname">%s</span>'
            '<span class="tag opp">置信%s</span></div>%s%s</div>'
            % (esc(name or c.get('policy_id') or '传导链'), esc(conf), flow,
               details('<span class="xsmall muted">查看政策原文依据（L1–L6 完整明细）</span>', full) if full else ''))


def chain_fallback_text(c):
    """传导链缺少结果层时的兜底表述，不新增研判。"""
    return '该链条未提供企业端结果文本，详见下方 L1–L6 原始层级。'


def _scn_cards(sc):
    outs = sc.get('scenario_outcomes') or []
    cls = {'乐观': 'opt', '基准': 'base', '悲观': 'pes'}
    order = ['乐观', '基准', '悲观']
    outs = sorted(outs, key=lambda x: order.index(x.get('scenario_id')) if x.get('scenario_id') in order else 9)
    cards = []
    for x in outs:
        sid = x.get('scenario_id') or '未标注'
        tg, body = split_tag(x.get('l5_l6_outcome'))
        res = x.get('resource_implication') or {}
        # 资源含义（稀缺/贬值/暴露）默认收起，让出主视觉；读者按需展开
        res_rows = ''.join('<div class="resrow"><b>%s</b>：%s</div>' % (esc(k), esc(brief(v, 70)))
                           for k, v in (('稀缺且有价值', res.get('scarce_and_valuable')),
                                        ('将贬值', res.get('devaluing')),
                                        ('风险暴露', res.get('risk_exposed'))) if v)
        res_html = (details('<span class="xsmall muted">资源含义（稀缺 / 贬值 / 暴露）</span>', res_rows)
                    if res_rows else '')
        cards.append('<div class="sc-card %s"><div class="sch">%s%s</div><div class="sct">%s</div>%s</div>'
                     % (cls.get(sid, ''), esc(sid),
                        '<span class="tag gold">主推</span>' if sid == '基准' else '',
                        esc(brief(body, 180)), res_html))
    if not cards:
        return '<div class="notice">本次输出未包含三情景结果（scenario_outcomes 为空）。</div>'
    return '<div class="sc-grid">%s</div>' % ''.join(cards)


def render(final, out_path):
    meta = final.get('meta') or {}
    scope = final.get('scope') or {}
    land = final.get('policy_landscape') or {}
    pols = land.get('policies') or []
    opps = final.get('opportunities') or []
    risks = final.get('risks') or []
    R = final.get('reasoning') or {}
    sc = R.get('scenarios') or {}
    # 归一化 scenarios 子字段：兼容模型偶发的字段名漂移（scenario/scenario_id、signal/monitoring_indicator 等）
    _outs = sc.get('scenario_outcomes')
    if isinstance(_outs, list):
        _norm = []
        for _x in _outs:
            if not isinstance(_x, dict):
                _norm.append(_x)
                continue
            _y = dict(_x)
            if not _y.get('scenario_id') and _y.get('scenario'):
                _y['scenario_id'] = _y.get('scenario')
            _ri = _y.get('resource_implication')
            if isinstance(_ri, str):
                _k = _ri if _ri in ('scarce_and_valuable', 'devaluing', 'risk_exposed') else 'scarce_and_valuable'
                _y['resource_implication'] = {_k: _ri}
            _norm.append(_y)
        sc['scenario_outcomes'] = _norm
    _lk = sc.get('scenario_linkage')
    if isinstance(_lk, list):
        _lk2 = []
        for _x in _lk:
            if isinstance(_x, dict):
                _y = dict(_x)
                if not _y.get('scenario_id') and _y.get('scenario'):
                    _y['scenario_id'] = _y.get('scenario')
                _lk2.append(_y)
            else:
                _lk2.append(_x)
        sc['scenario_linkage'] = _lk2
    _sig = sc.get('monitoring_signals')
    if isinstance(_sig, list):
        _sig2 = []
        for _x in _sig:
            if isinstance(_x, dict):
                _y = dict(_x)
                if not _y.get('contingent_action') and _y.get('action_id'):
                    _y['contingent_action'] = _y.get('action_id')
                if not _y.get('monitoring_indicator') and _y.get('signal'):
                    _y['monitoring_indicator'] = _y.get('signal')
                if not _y.get('why_earliest_proxy') and _y.get('leading_rationale'):
                    _y['why_earliest_proxy'] = _y.get('leading_rationale')
                _sig2.append(_y)
            else:
                _sig2.append(_x)
        sc['monitoring_signals'] = _sig2
    _sva = sc.get('swing_variable_analysis')
    if isinstance(_sva, dict) and not _sva.get('swing_variable') and _sva.get('swing_variables'):
        _sva['swing_variable'] = _sva.get('swing_variables')
    val = final.get('validation') or {}
    issues = list(final.get('known_issues') or [])
    demo = bool(meta.get('demo_mode'))
    primary = ((meta.get('regions') or {}).get('primary') or {})
    title = (meta.get('input_text') or '政策研究')[:40]
    aidx = _action_index(sc)
    known_ids = ({x.get('id') for x in opps} | {x.get('id') for x in risks})
    acts = sc.get('action_paths') or []
    RENDER_ISSUES.clear()
    es = final.get('executive_summary') or ''
    tw = scope.get('time_window') or {}
    segs = scope.get('core_segments') or []

    H = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width, initial-scale=1">'
         '<title>%s · 政策研判报告</title><style>%s</style></head><body>' % (esc(title), CSS)]
    # 侧栏
    H.append('<div class="app"><aside class="side"><div class="brand">POLICY RESEARCH AGENT · v2.0</div>'
             '<h1>%s<br>政策研判报告</h1><nav>' % esc(title))
    for sid, stage, name, _src in _BLOCKS:
        H.append('<a href="#%s">%s</a>' % (sid, esc(name)))
    H.append('</nav><div class="foot">仅展示已产出 JSON，不新增结论</div></aside><main class="main">')
    # 封面
    H.append('<div class="hero"><div class="eyebrow">POLICY RESEARCH REPORT / H5</div>'
             '<h2>%s<br>政策研判报告</h2>'
             '<p class="lead">按「扫描分类 → 解读拆解 → 传导链 → 风险机会矩阵 → 情景与路径」五阶段框架生成：'
             '含 A/B 证据分级、PESTEL 与多流派分析、政策沿革、干系人矩阵、三情景量化与行动路线图。</p>'
             '<div class="chips">' % esc(title))
    chips = [('主区域 · %s %s' % (primary.get('province', ''), primary.get('city', '')), ''),
             ('输入类型 · %s' % (meta.get('input_type') or '未标注'), ''),
             ('主体置信度 · %s' % (meta.get('boundary_confidence') or '未标注'), ''),
             qc_chip(val, final)]
    if demo:
        chips.append(('演示模式 · 样例数据', 'warn'))
    if meta.get('web_search'):
        chips.append(('已启用联网检索', 'ok'))
    else:
        chips.append(('未启用联网检索 · 结论受限', 'warn'))
    for t, c in chips:
        H.append('<span class="chip %s">%s</span>' % (c, esc(t)))
    H.append('</div></div>')
    if demo:
        H.append('<div class="demo-banner">演示模式：本报告为内置样例数据，仅用于预览界面与样式，'
                 '<b>并非针对本次输入实时生成的政策结论</b>。</div>')

    # ---- 执行摘要：核心洞察 ----
    b = []
    m = [('政策条目数', '%d（国家%d / 省级%d）' % (
            len(pols),
            sum(1 for p in pols if 'national' in str(p.get('region_scope') or '')),
            sum(1 for p in pols if 'national' not in str(p.get('region_scope') or '')))),
         ('核心赛道', '%d' % len(segs)),
         ('机会 / 风险', '%d / %d' % (len(opps), len(risks))),
         ('高优先级行动', '%d' % sum(1 for a in acts if str(a.get('priority') or '') == '高'))]
    b.append('<div class="metrics">' + ''.join(
        '<div class="metric"><div class="v">%s</div><div class="l">%s</div></div>' % (esc(v), esc(l))
        for l, v in m) + '</div>')
    _o1 = sorted([x for x in opps if x.get('description')], key=lambda x: 0 if (x.get('certainty') or '') == '高' else 1)
    _r1 = sorted([x for x in risks if x.get('description')], key=lambda x: 0 if (x.get('certainty') or '') == '高' else 1)
    _a1 = [a for a in acts if str(a.get('priority') or '') == '高']
    # 核心洞察 = 由总控汇总各子智能体研判后给用户的「最核心建议」，直接说结论与行动，不罗列所用方法/校验方式
    _msc = R.get('multiple_streams_conclusion') or {}
    _wstat = txt(_msc.get('window_status')) if isinstance(_msc, dict) else ''
    _a0raw = split_tag(_a1[0].get('action'))[1] if _a1 else ''
    _a0first = ' '.join(_a0raw.split('，')[0].split('；')[0].split())
    _a0txt = esc(brief(_a0first, 40)) if _a0first else ''
    # 最高优先机会/风险（按确定性排序，取最靠前一条的要点）
    _o_top = _o1[0] if _o1 else None
    _r_top = _r1[0] if _r1 else None
    _o_point = clean_sentence(split_tag(_o_top.get('description'))[1], 70) if _o_top else ''
    _r_point = clean_sentence(split_tag(_r_top.get('description'))[1], 70) if _r_top else ''
    _lead = []
    _lead.append('当前政策窗口%s' % ('正处「%s」阶段' % esc(_wstat) if _wstat else '状态待判定'))
    if _o_point:
        _lead.append('最值得抓的机会是：%s' % _o_point)
    if _r_point:
        _lead.append('最需要防的风险是：%s' % _r_point)
    if _a0txt:
        _lead.append('建议现在就做：%s' % _a0txt)
    _lead.append('完整机会、风险与行动见下方各节。')
    insight = '；'.join(_lead) + '。'
    # 折叠区：支撑本次洞察的政策原文 / 标题 / 发文机关
    _pid_total = {}
    for x in (opps + risks):
        for pid in arr(x.get('evidence_policy_ids')):
            _pid_total[pid] = _pid_total.get(pid, 0) + 1
    _pmap = {p.get('id'): p for p in pols}
    _tops = sorted(_pid_total, key=lambda k: -_pid_total[k])[:6]
    _ev = []
    for pid in _tops:
        p = _pmap.get(pid) or {}
        _stxt, _scls = _excerpt_source(p)
        _ev.append('<div class="card"><div class="small"><b>%s %s</b>　<span class="tag gray">%s</span>'
                   '　<span class="src-tag %s">%s</span></div>'
                   '<div class="xsmall muted" style="margin-top:4px">发文机关：%s　发布：%s　效力：%s</div>'
                   '<div class="quote" style="margin-top:8px">%s</div>%s</div>'
                   % (esc(pid), esc(brief(p.get('title'), 60)), esc(p.get('effect_level') or '—'),
                      _scls, _stxt,
                      esc(p.get('issuing_body') or '—'), esc(p.get('publish_date') or '—'),
                      esc(p.get('region_scope') or '—'),
                      esc(_excerpt_body(p, 220)) or '<span class="muted">未取得原文正文</span>',
                      link(p.get('source_url'), '官方原文')))
    b.append(_k_block(opps, risks))
    b.append(details('<span class="xsmall muted">支撑本次洞察的政策原文（标题 / 发文机关 / 摘录）</span>',
                     ''.join(_ev) if _ev else '<div class="notice">本次未引用可追溯政策条目。</div>'))
    b.append(details('<span class="xsmall muted">报告口径（主区域 / 时间窗）</span>', kv([
        ('主区域', esc('%s %s' % (primary.get('province', ''), primary.get('city', '')))),
        ('时间窗', esc('%s ~ %s' % (tw.get('start', ''), tw.get('end', ''))))])))
    H.append(_blk('s-summary', '', '执行摘要', '综合政策扫描 · PESTEL · 多源流 · 情景推演',
                  insight, ''.join(b), label='核心洞察'))

    # ---- 阶段一 · 扫描与分类：赛道 / 时间 / 政策类型 三维度 ----
    b = ['<div class="sec-note">从赛道、时间、政策类型三个角度俯瞰本次采集的政策全集，帮助判断政策集中在哪些环节、哪些年份、哪类文件。</div>']
    _dim_bars = [_seg_bars(pols, segs), _time_bars(pols), _type_bars(pols)]
    _dim_bars = [x for x in _dim_bars if x]
    b.append('<div class="dim-grid">%s</div>' % ''.join('<div class="dim-cell">%s</div>' % x for x in _dim_bars))
    _with_url = sum(1 for p in pols if p.get('source_url'))
    _full_cnt = sum(1 for p in pols if p.get('full_excerpt'))
    _snippet_cnt = sum(1 for p in pols if (not p.get('full_excerpt')) and '检索摘要片段' in str(p.get('_fetch_note') or ''))
    b.append('<div class="sec-note">原文可验证性说明：本次 %d 条政策中，%d 条附可点击的官方原文链接；'
             '其中 %d 条抓到官方详情页原文、%d 条仅有检索摘要片段、%d 条未取得原文正文。'
             '仅摘要或标题的结论已据此降级，不得作为申报依据。</div>' % (
                 len(pols), _with_url, _full_cnt, _snippet_cnt, len(pols) - _full_cnt - _snippet_cnt))
    def _src_cell(p):
        txt, cls = _excerpt_source(p)
        badge = '<span class="src-tag %s">%s</span>' % (cls, txt)
        return badge + (' ' + link(p.get('source_url'), '链接') if p.get('source_url') else '')
    b.append(details('<span class="xsmall muted">政策明细表（%d 条，含原文摘录与来源标注）</span>' % len(pols),
                     table(['ID', '标题', '层级', '发布', '原文摘录', '来源'],
                           [['<span class="mono">%s</span>' % esc(p.get('id')),
                             esc(brief(p.get('title'), 42)), esc(p.get('effect_level')),
                             esc(p.get('publish_date')),
                             esc(_excerpt_body(p, 46)) or '<span class="muted">未取得原文</span>',
                             _src_cell(p)] for p in pols])))
    _nat = sum(1 for p in pols if 'national' in str(p.get('region_scope') or ''))
    _segdesc = '、'.join('%s %d 条' % (esc(s.get('name') or s.get('id')),
                sum(1 for p in pols if s.get('id') in arr(p.get('segment_tags')))) for s in segs)
    concl = ('本次采集 %s 官方政策 %d 条（国家级 %d 条、%s %d 条），时间窗 %s ~ %s；'
             '覆盖 %d 个核心赛道：%s。效力层级与逐条出处见下方明细。'
             % (esc(primary.get('province') or '主区域'), len(pols), _nat,
                esc(primary.get('city') or '主区域'), len(pols) - _nat,
                esc(tw.get('start') or '—'), esc(tw.get('end') or '—'),
                len(segs), _segdesc))
    H.append(_blk('s-landscape', '阶段一 · 政策扫描与分类', '政策全景与赛道覆盖',
                  '数据源：policy_landscape.policies（%d 条）' % len(pols), esc(concl), ''.join(b)))

    # ---- 阶段二 · 解读与拆解 ----
    b = []
    pp = R.get('pestel_positioning') or []
    if pp:
        b.append('<div class="sec-note">把政策按政治、经济、社会、技术、环境、法律六个角度归类，'
                 '每个角度一句话说清它对行业意味着什么；标「证据缺口」的维度表示本次没有可核实的对应条款，不作现行约束。</div>')
        # 固定六维卡：P → E → S → T → Env → L，不按条数排序（对齐参照版式）
        b.append('<h4>PESTEL 六维定性（固定顺序）</h4><div class="pestel-grid">' + ''.join(
            _pestel_card(code, pp) for code in ('P', 'E', 'S', 'T', 'Env', 'L')) + '</div>')
        b.append(details('<span class="xsmall muted">各维度完整判断依据（含反例检验）</span>', '<div class="grid2">' + ''.join(
            '<div class="card"><span class="tag violet">%s</span><div class="small" style="margin-top:6px">%s</div>'
            '<div class="xsmall muted" style="margin-top:6px">反例：%s</div></div>'
            % (esc(dim_cn(x.get('dimension') or x.get('pestel_dimension'))),
               esc(clean_sentence(x.get('rationale') or x.get('statement'), 220)),
               esc(brief(x.get('counter_evidence'), 160)))
            for x in pp) + '</div>'))
    else:
        b.append('<div class="notice">本次输出未包含 PESTEL 定位（pestel_positioning 为空）。</div>')
    b.append(_ms_block(R))
    # 结论：用自然语言概述六维走向与多流派结论，不拼接维度数组/字段名
    msc = (R.get('multiple_streams_conclusion') or {})
    ws = txt(msc.get('window_status')) if isinstance(msc, dict) else ''
    stable_dims, shifting_dims = [], []
    for x in pp:
        codes = [str(c) for c in arr(x.get('dimension') or x.get('pestel_dimension'))]
        stab = str(x.get('stability_weight') or x.get('historical_stability') or '')
        if '高' in stab or '中' in stab:
            stable_dims.extend(codes)
        elif any(k in stab for k in ('收紧', '转向', '低', '变化')):
            shifting_dims.extend(codes)
    _lead = []
    if stable_dims:
        _lead.append('政策在%s等维度方向稳定、连续性强' % dim_cn(list(dict.fromkeys(stable_dims))))
    if shifting_dims:
        _lead.append('%s维度出现收紧或转向' % dim_cn(list(dict.fromkeys(shifting_dims))))
    if not _lead:
        _lead.append('六个维度的定性判断见下方卡片')
    concl = '%s；政策窗口判定为「%s」。' % ('；'.join(_lead), ws or '待判定')
    H.append(_blk('s-interpret', '阶段二 · 政策解读与拆解', '政策性质定位（PESTEL）与多流派分析',
                  '六维定性 + 多流派研判', esc(concl), ''.join(b)))

    # ---- 阶段二 · 下：政策沿革与版本比对（独立成节，分析式展示，不止列表） ----
    _lg = land.get('lineage') or []
    _lg_closed = sum(1 for x in _lg if x.get('closed'))
    _lg_body = []
    if _lg:
        # 有版本链数据：用既有时间线卡片做版本比对分析
        _lg_concl = ('共梳理 %d 条政策沿革链、其中 %d 条版本关系闭合；下方按时间线逐条展示版本更替、'
                     '变化要点与是否延续，据此判断哪些文件仍现行有效。' % (len(_lg), _lg_closed))
        _lg_body.append(_lineage_block(land, pols))
    else:
        # 无成体系 lineage 时：按效力状态分组做「分析式」展示——硬性有效 vs 方向性规划，
        # 每种状态一段结论 + 时间线卡片，指出当前真正可依赖的是哪一类（纯搬运已有字段，不新增研判）
        _buckets = {}
        for p in pols:
            st = str(p.get('status') or '状态未核实').strip()
            _buckets.setdefault(st, []).append(p)
        def _bucket_kind(st):
            if any(k in st for k in ('规划', '意向', '非强制')):
                return 'direction'
            if any(k in st for k in ('废止', '失效', '过期')):
                return 'invalid'
            if any(k in st for k in ('生效', '有效', '现行')):
                return 'valid'
            return 'unknown'
        _kind_cn = {'valid': '现行有效（硬性约束）', 'direction': '方向性部署（非强制）',
                    'invalid': '已废止/失效', 'unknown': '状态待核实'}
        _valid_n = sum(len(v) for k, v in _buckets.items() if _bucket_kind(k) == 'valid')
        _dir_n = sum(len(v) for k, v in _buckets.items() if _bucket_kind(k) == 'direction')
        _lg_concl = ('本次未取得逐版本的沿革链数据。按效力状态分析：%d 条为现行有效的硬性约束，'
                     '是判断合规义务的主要依据；%d 条为方向性规划、非强制，不能当作已生效的准入条件。'
                     '具体时间线如下，版本更替与是否现行有效仍以官方原文为准。' % (_valid_n, _dir_n))
        _order = sorted(_buckets.items(), key=lambda kv: {'valid': 0, 'direction': 1, 'invalid': 2, 'unknown': 3}[_bucket_kind(kv[0])])
        for st, items in _order:
            kind = _bucket_kind(st)
            _cards = []
            for p in items[:8]:
                # 顶栏优先显示真实日期；无日期时改用发文机关（有意义的信息），不显示「未核实」占位
                _date_raw = str(p.get('publish_date') or p.get('effective_date') or '').strip()
                _has_date = bool(_date_raw) and _date_raw not in ('未核实', '未标注', '时间未核实', '—')
                _top = _date_raw if _has_date else (str(p.get('issuing_body') or '').strip() or p.get('effect_level') or '文件')
                # 次行：有日期时补发文机关+效力；无日期时只显示效力层级，避免重复
                if _has_date:
                    _sub = ' · '.join(x for x in (str(p.get('issuing_body') or '').strip(),
                                                  str(p.get('effect_level') or '').strip()) if x)
                else:
                    _sub = str(p.get('effect_level') or '').strip()
                _cards.append('<div class="lin-ver"><div class="d">%s</div><div class="t">%s %s</div>'
                              '<div class="xsmall muted">%s</div></div>'
                              % (esc(brief(_top, 26)), esc(p.get('id') or ''), esc(brief(p.get('title'), 46)),
                                 esc(_sub or '—')))
            _more = ('其余 %d 条见「政策扫描与分类」明细表。' % (len(items) - 8)) if len(items) > 8 else ''
            _lg_body.append(
                '<div class="lg-group %s"><div class="lg-head"><span class="tag %s">%s</span>'
                '<b>%s</b><span class="xsmall muted">%d 条</span></div>'
                '<div class="sec-note">%s</div><div class="lin-tl">%s</div>%s</div>'
                % (kind, 'opp' if kind == 'valid' else ('warn' if kind == 'direction' else 'gray'),
                   esc(_kind_cn[kind]), esc(st), len(items),
                   esc('这一类可作为现行合规判断的直接依据。' if kind == 'valid' else
                       ('这一类体现政策方向，但不构成强制义务。' if kind == 'direction' else
                        '这一类需进一步核实其现行效力。')),
                   ''.join(_cards), esc(_more)))
    H.append(_blk('s-lineage', '阶段二 · 下', '政策沿革与版本比对',
                  '政策怎么改、现在哪版有效', esc(_lg_concl), ''.join(_lg_body)))

    # ---- 阶段三 · 传导链 ----
    b = []
    chains = R.get('logic_chains') or []
    if chains:
        for c in chains[:3]:
            b.append(_chain_card(c))
        if len(chains) > 3:
            b.append(details('<span class="xsmall muted">其余 %d 条传导链（结构相同）</span>' % (len(chains) - 3),
                             ''.join(_chain_card(c) for c in chains[3:])))
    else:
        b.append('<div class="notice">本次输出未包含传导链（logic_chains 为空）。</div>')
    dm = sc.get('divergence_mapping') or {}
    sub = []
    if sc.get('swing_variable_analysis'):
        sub.append('<div><b class="small">摆动变量</b>' + kv([
            ('变量', esc(brief(sc['swing_variable_analysis'].get('swing_variable'), 120))),
            ('为何够格', esc(brief(sc['swing_variable_analysis'].get('why_qualifies'), 160)))]) + '</div>')
    if dm:
        sub.append('<div><b class="small">分歧映射</b>' + kv([
            ('一致层', esc(txt(dm.get('shared_layers')))),
            ('分歧起始层', esc(dm.get('divergence_start_layer'))),
            ('各情景分叉', para(dm.get('divergence_by_scenario')))]) + '</div>')
    if sc.get('monitoring_signals'):
        _sig_rows = []
        for x in (sc['monitoring_signals'] if isinstance(sc['monitoring_signals'], list) else []):
            if isinstance(x, dict):
                _act = clean_sentence(x.get('contingent_action') or x.get('action_id'), 24)
                _ind = clean_sentence(x.get('monitoring_indicator') or x.get('signal'), 90)
                _sig_rows.append('· 若「%s」：观察 %s' % (esc(_act or '相关动作'), esc(_ind or '领先指标')))
            else:
                _sig_rows.append('· %s' % esc(brief(x, 120)))
        sub.append('<div><b class="small">领先监测信号</b>' + ''.join(
            '<div class="small">%s</div>' % r for r in _sig_rows) + '</div>')
    if sub:
        b.append(details('<span class="xsmall muted">摆动变量、分歧映射与监测信号</span>', ''.join(sub)))
    # 传导链结论：用「政策先改变什么 → 行业怎么变 → 企业最终要做什么」的人话讲清，去掉层名/字段名残片
    _story = []
    if chains:
        c0 = chains[0]
        _lays = c0.get('logic_chain') or []
        _seg = {}
        for L in _lays:
            st = str(L.get('stage') or L.get('node') or '')
            txt_ = clean_sentence(L.get('content'), 90)
            if txt_ and st not in _seg:
                _seg[st] = txt_
        _pick = lambda keys: next((_seg[k] for k in keys if k in _seg), '')
        _start = _pick(['条款', '直接主体', '政策条款'])
        _mid = _pick(['结构变化', '价值链'])
        _endp = _pick(['企业影响', '战略结果'])
        if _start:
            _story.append('政策层面：%s' % _start)
        if _mid:
            _story.append('传到行业与价值链：%s' % _mid)
        if _endp:
            _story.append('落到企业：%s' % _endp)
        if not _story:
            _story.append('政策经条款、行业、价值链逐层传导，最终影响企业的成本、准入与战略选择')
    if dm:
        _div = str(dm.get('divergence_start_layer') or '').strip()
        if _div:
            _story.append('三情景在「%s」这一层开始分叉，此前各情景判断一致' % esc(clean_sentence(_div, 24)))
    concl = ('；'.join(_story) + '。') if _story else '政策如何逐层传导到企业，见下方传导链。'
    H.append(_blk('s-chain', '阶段三 · 传导链分析（政策 → 行业 → 企业）', '传导链推演',
                  '政策 → 行业 → 价值链 → 企业 逐层推演', esc(concl), ''.join(b)))

    # ---- 阶段四 · 机会风险矩阵（由评级计算落格，再由落格反推结论） ----
    b = []
    idx, rmethod = _rating_index(final, opps, risks)
    hm, hcells, hun = _matrix_from_ratings([x for x in opps if (x.get('id') in idx)], aidx, idx)
    rm_, rcells, run = _matrix_from_ratings([x for x in risks if (x.get('id') in idx)], aidx, idx)
    b.append('<div class="mxwrap"><div class="mxpair">'
             '<div class="mxcol"><h4>机会 · 可能性 × 影响</h4>%s</div>'
             '<div class="mxcol"><h4>风险 · 可能性 × 影响</h4>%s</div></div></div>' % (hm, rm_))
    if rmethod:
        b.append('<div class="mx-method"><b>评级方法</b>：%s</div>' % esc(rmethod))
    b.append(_stakeholders_block(R))
    if opps or risks:
        b.append(details('<span class="xsmall muted">机会与风险完整卡片（%d 条，含反例检验与归格依据）</span>'
                         % (len(opps) + len(risks)),
                         '<div class="grid2">' + ''.join(_orcard(x, '机会', aidx) for x in opps)
                         + ''.join(_orcard(x, '风险', aidx) for x in risks) + '</div>'))
    # 结论从矩阵落格计算结果推导（不是直接给条目）
    hot_r = [x for x, _basis in rcells.get(('高', '高'), [])]
    hot_o = [x for x, _basis in hcells.get(('高', '高'), [])]
    _hot_ids = '、'.join(esc(x.get('id')) for x in hot_r[:6]) or '无'
    _hot_o_ids = '、'.join(esc(x.get('id')) for x in hot_o[:6]) or '无'
    covered = sum(1 for x in (opps + risks) if x.get('id') in aidx)
    total = len(opps) + len(risks)
    _gap = [x.get('id') for x in (opps + risks) if x.get('id') and x.get('id') not in aidx]
    _stk = ''
    stks = R.get('stakeholders') or []
    against = [s for s in stks if (s.get('stance') or '') == '反对']
    if against:
        _a0 = against[0]
        _stk = '；反对方 %s 影响力为%s，%s' % (
            esc(_a0.get('name') or '—'), esc(_a0.get('influence') or '未标注'),
            esc(_STK_VERDICT.get(_a0.get('influence'), '否决能力待核实')))
    if hot_r or hot_o:
        _hot = []
        if hot_o:
            _hot.append('机会 %s' % _hot_o_ids)
        if hot_r:
            _hot.append('风险 %s' % _hot_ids)
        concl = ('最该优先处置的是落在「高可能、高影响」格里的%s——这些事一旦发生影响最大，建议先安排。'
                 % '和'.join(_hot))
    else:
        concl = ('本次没有条目落在「高可能、高影响」的最高优先格，说明暂无必须立刻处置的极端事项；'
                 '可按下方各格由高到低依次关注。')
    if covered >= total and total > 0:
        concl += '列出的机会与风险都已匹配到对应行动。'
    elif _gap:
        concl += '另有 %d 条尚未匹配行动（%s），属于需要补位的管理缺口。' % (
            len(_gap), esc('、'.join(_gap[:6])))
    concl += _stk
    H.append(_blk('s-risk', '阶段四 · 机会风险矩阵', '机会与风险清单（矩阵计算）',
                  '数据源：opportunities + risks + 评级矩阵 + stakeholders', concl, ''.join(b)))

    # ---- 阶段五 · 情景与路径 ----
    b = [_scn_cards(sc)]
    ku = R.get('key_uncertainties') or []
    if ku:
        b.append(details('<span class="xsmall muted">全部 %d 条关键不确定性</span>' % len(ku),
                         ''.join('<div class="kj"><b class="small">· %s</b></div>' % esc(brief(x, 140)) for x in ku)))
    qi = final.get('quantitative_impact') or R.get('quantitative_impact') or []
    if qi:
        b.append(details('<span class="xsmall muted">三情景量化指标（%d 项，含测算依据）</span>' % len(qi), qi_block(final)))
    # 结论：把乐观/基准/悲观三种结果用一句话串起来，提炼「该关注什么」，而不是只复述基准
    _outs = sc.get('scenario_outcomes') or []
    _byname = {str(x.get('scenario_id') or x.get('scenario') or '').strip(): x for x in _outs}
    def _gist(name):
        x = _byname.get(name)
        return clean_sentence(split_tag(x.get('l5_l6_outcome'))[1], 90) if x else ''
    _g_opt, _g_base, _g_pes = _gist('乐观'), _gist('基准'), _gist('悲观')
    _sw = txt((sc.get('swing_variable_analysis') or {}).get('swing_variable'))
    _story = []
    if _g_base:
        _story.append('大概率沿基准走：%s' % _g_base)
    if _g_opt:
        _story.append('若条件转好（乐观）：%s' % _g_opt)
    if _g_pes:
        _story.append('若条件恶化（悲观）：%s' % _g_pes)
    if _sw:
        _story.append('决定最终走向哪一档的关键是：%s' % esc(brief(_sw, 55)))
    concl = ('；'.join(_story) + '。') if _story else '三种情景的结果与关键不确定性见下方。'
    H.append(_blk('s-scenario', '阶段五 · 情景分支与实施路径', '三情景与关键不确定性',
                  '乐观 / 基准 / 悲观 三情景对照', esc(concl), ''.join(b)))

    # ---- 阶段五 · 下：行动路线 ----
    b = [_roadmap_block(sc, known_ids)]
    b.append(details('<span class="xsmall muted">全部行动的申报条件 / 责任部门 / 时间节点</span>',
                     '<div class="conlist">' + table(['行动 id', '行动', '条件/验收', '责任部门', '时间'],
        [[esc(a.get('action_id') or '—'), esc(brief(a.get('action'), 46)),
          esc(brief(a.get('eligibility') or a.get('acceptance_criteria') or '—', 110)),
          esc(brief(a.get('responsible_body') or '—', 44)),
          esc(brief(a.get('window') or a.get('timeline') or '—', 40))] for a in acts]) + '</div>'))
    _a0 = next((a for a in acts if str(a.get('priority') or '') == '高'), acts[0] if acts else None)
    _aconcl = ('最高优先级行动是「%s」：%s%s。' % (
        esc(_a0.get('action_id') or '—'),
        _qbrief(split_tag(_a0.get('action'))[1], 70),
        '。验收标准：%s' % esc(brief(_a0.get('acceptance_criteria'), 90)) if _a0.get('acceptance_criteria') else '')) if _a0 else '本次输出未包含行动清单。'
    H.append(_blk('s-actions', '阶段五 · 下：行动路线图', '行动建议路线图',
                  '数据源：scenarios.action_paths（%d 项）' % len(acts), _aconcl, ''.join(b)))

    H.append('<div class="footer">政策研究智能体 v2.0 · H5 报告｜五阶段版面｜生成时间 %s｜'
             '仅渲染已产出 JSON，不新增任何分析结论</div>' % esc(meta.get('generated_at')))
    H.append('</main></div><script>%s</script></body></html>' % _MINI_JS)
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write(''.join(H))
    return out_path



# ===== 命令行入口：python render_h5.py <final_report.json> [output.html] =====
def _main():
    import sys
    if len(sys.argv) < 2:
        print('用法: python render_h5.py <final_report.json> [output.html]')
        sys.exit(1)
    import argparse
    ap = argparse.ArgumentParser(description='把 final_report.json 渲染为单文件离线 H5 报告')
    ap.add_argument('report', help='final_report.json 路径')
    ap.add_argument('output', nargs='?', default=None, help='输出 html 路径（默认与输入同目录 report.html）')
    args = ap.parse_args()
    with io.open(args.report, encoding='utf-8') as f:
        data = json.load(f)
    out = args.output
    if not out:
        import os as _os
        out = _os.path.join(_os.path.dirname(_os.path.abspath(args.report)), 'report.html')
    render(data, out)
    size = os.path.getsize(out)
    print('H5_REPORT_OK')
    print('OUTPUT=%s' % out)
    print('SIZE_BYTES=%d' % size)


if __name__ == '__main__':
    _main()
