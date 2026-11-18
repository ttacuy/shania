# 高龄急诊预检：文献图表与讲义底稿

40 页顺序按拟定目录的 1–37 项保留，第 38–40 页补上数字溯源、文献和铺正文核对。图中的数来自所列原始文献，替换模板里的英文和示意数字。

- WPS 文字直接打开：[`高龄患者急诊预检讲义.docx`](高龄患者急诊预检讲义.docx)
- 讲义源稿：[`讲义.md`](讲义.md)
- 图：[`figures/`](figures/)（PNG 与 SVG）
- 表 3-3：[`tables/table_3_3_performance.csv`](tables/table_3_3_performance.csv)
- 可复核的汇总数：[`data/cited_figures.json`](data/cited_figures.json)

用 WPS 文字打开 `高龄患者急诊预检讲义.docx`。重新生成：

```bash
pip install -r docs/geriatric-triage/requirements.txt
python3 docs/geriatric-triage/scripts/build_docx.py
```

重画图：

```bash
pip install -r docs/geriatric-triage/requirements.txt
python3 docs/geriatric-triage/scripts/build_figures.py
```

误差线若来自 NHAMCS，画的是公布的标准误，不是 95% 置信区间。不同工具的 AUC 对应不同结局，讲义里分开引用，不排成一张“谁更准”的横比图。
