# 高龄急诊治疗决策原始数据汇编

检索日期：2026 年 11 月 18 日（北京时间）。

`高龄急诊治疗决策原始数据汇编.pdf` 收录能说明急诊高龄患者治疗决定的已发表原始数字，以及按这些数字重绘的 18 张图。`data/` 是同一批表的 CSV，`figures/` 是图的 PNG。`build_report.py` 从这些数字生成 PDF 和图。

数字来自 PubMed 摘要或 PMC 开放全文表格。摘要来源、全文来源和年龄界限写在 PDF 第十二节。这不是新的 Meta 分析，也没有合并不同研究的死亡率。

`高龄急诊预检与综合救治.pptx` 是同一批检索的纯白背景简报，覆盖人口现状、国家卫生健康大会之后的老年诊疗文件、应急救援要求、与年轻患者的差别、预检和高危识别、综合救治细节。政策数字来自国家统计局和国家卫生健康委公开文件，不把国际研究写成中国验证结果。

重新生成：

```bash
python3 evidence/elderly-ed-decision/build_report.py
python3 evidence/elderly-ed-decision/build_pptx.py
```
