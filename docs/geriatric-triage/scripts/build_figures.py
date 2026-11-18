#!/usr/bin/env python3
"""Redraw geriatric ED triage figures from cited primary sources.

Numbers are transcribed from the sources named in each caption.
Standard-error bars are the survey standard errors published by NCHS,
not 95% confidence intervals. Confidence intervals, where drawn, are
the intervals printed by the cited paper.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
TAB = ROOT / "tables"

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
font_manager.fontManager.addfont(FONT_PATH)
plt.rcParams["font.family"] = "WenQuanYi Micro Hei"
plt.rcParams["axes.unicode_minus"] = False

INK = "#1f2933"
MUTED = "#52606d"
GRID = "#e4e7eb"
ACCENT = "#1f4e79"
EMPH = "#8c3a1e"
PALE = "#d9e2ec"
WHITE = "#ffffff"


def _finish(ax, title, xlabel, ylabel, note):
    ax.set_title(title, loc="left", color=INK, fontsize=13, pad=12)
    ax.set_xlabel(xlabel, color=INK, fontsize=10)
    ax.set_ylabel(ylabel, color=INK, fontsize=10)
    ax.tick_params(colors=INK, labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#9aa5b1")
    ax.spines["bottom"].set_color("#9aa5b1")
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    fig = ax.figure
    fig.text(0.01, 0.01, note, ha="left", va="bottom", color=MUTED, fontsize=8, wrap=True)
    fig.tight_layout(rect=(0, 0.08, 1, 1))


def save(fig, stem):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{stem}.png", dpi=160, facecolor=WHITE)
    fig.savefig(FIG / f"{stem}.svg", facecolor=WHITE)
    plt.close(fig)


def fig_visit_rate():
    labels = ["<15", "15–24", "25–44", "45–64", "65–74", "≥75"]
    rate = [44.5, 47.5, 45.3, 43.8, 46.4, 76.0]
    se = [4.8, 4.0, 3.6, 3.1, 3.7, 7.0]
    colors = [ACCENT] * 5 + [EMPH]
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    bars = ax.bar(labels, rate, color=colors, width=0.72, yerr=se, capsize=3,
                  ecolor=MUTED, error_kw={"linewidth": 0.9})
    for bar, value in zip(bars, rate):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 6.2, f"{value:.1f}",
                ha="center", va="bottom", color=INK, fontsize=9)
    ax.set_ylim(0, 100)
    _finish(
        ax,
        "图 3-1  美国急诊就诊率，按年龄",
        "年龄（岁）",
        "每 100 人就诊次数",
        "来源：NCHS，NHAMCS 2022 Emergency Department Summary Tables，表 1。误差线为公布的标准误。2022 年全部就诊 1.554 亿人次，总就诊率 47.3 / 100 人。",
    )
    save(fig, "fig_3_1_visit_rate")


def fig_visit_volume():
    labels = ["<15", "15–24", "25–44", "45–64", "65–74", "≥75"]
    thousands = [26421, 20675, 39568, 35799, 15552, 17383]
    share = [17.0, 13.3, 25.5, 23.0, 10.0, 11.2]
    colors = [ACCENT] * 5 + [EMPH]
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    bars = ax.bar(labels, [v / 1000 for v in thousands], color=colors, width=0.72)
    for bar, value, pct in zip(bars, thousands, share):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f"{value / 1000:.1f}\n{pct:.1f}%", ha="center", va="bottom",
                color=INK, fontsize=8)
    ax.set_ylim(0, 52)
    _finish(
        ax,
        "图 3-1 附  美国急诊就诊量（百万）及占总就诊比重",
        "年龄（岁）",
        "就诊次数（百万）",
        "来源：NHAMCS 2022 表 1，单位为千人次，图中改为百万。65 岁及以上合计 3293.5 万，占 21.2%。柱顶第二行是占全部就诊的百分比。",
    )
    save(fig, "fig_3_1b_visit_volume")


def fig_admission():
    labels = ["<15", "15–24", "25–44", "45–64", "65–74", "≥75"]
    pct = [3.7, 4.1, 6.0, 14.0, 23.2, 28.8]
    se = [0.8, 0.6, 0.7, 1.5, 2.8, 3.0]
    colors = [ACCENT] * 5 + [EMPH]
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    bars = ax.bar(labels, pct, color=colors, width=0.72, yerr=se, capsize=3,
                  ecolor=MUTED, error_kw={"linewidth": 0.9})
    ax.axhline(11.5, color=MUTED, linestyle="--", linewidth=0.9)
    ax.text(5.45, 12.3, "全部就诊 11.5%", color=MUTED, fontsize=8, ha="right")
    for bar, value in zip(bars, pct):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 2.2,
                f"{value:.1f}", ha="center", va="bottom", color=INK, fontsize=9)
    ax.set_ylim(0, 40)
    _finish(
        ax,
        "收入本院的就诊占比，按年龄",
        "年龄（岁）",
        "该年龄就诊中收入本院的百分比",
        "来源：NHAMCS 2022 表 24，Admissions as percent of visits。误差线为标准误。65–74 岁占全部入院的 20.3%，≥75 岁占 28.2%，两组合计约占急诊入院的 48.5%。",
    )
    save(fig, "fig_admission_by_age")


def fig_ambulance():
    labels = ["<15", "15–24", "25–44", "45–64", "65–74", "≥75"]
    pct = [5.0, 11.0, 12.5, 19.4, 26.5, 39.6]
    se = [0.8, 0.9, 0.9, 1.3, 2.2, 2.0]
    colors = [ACCENT] * 5 + [EMPH]
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    bars = ax.bar(labels, pct, color=colors, width=0.72, yerr=se, capsize=3,
                  ecolor=MUTED, error_kw={"linewidth": 0.9})
    ax.axhline(17.0, color=MUTED, linestyle="--", linewidth=0.9)
    ax.text(5.45, 18.2, "全部就诊 17.0%", color=MUTED, fontsize=8, ha="right")
    for bar, value in zip(bars, pct):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 2.6, f"{value:.1f}",
                ha="center", va="bottom", color=INK, fontsize=9)
    ax.set_ylim(0, 52)
    _finish(
        ax,
        "救护车到达占比，按年龄",
        "年龄（岁）",
        "该年龄就诊中救护车到达的百分比",
        "来源：NHAMCS 2022 表 4。误差线为标准误。65 岁及以上合计为 33.4%（标准误 1.6）。未知到达方式未并入救护车。",
    )
    save(fig, "fig_ambulance_by_age")


def fig_esi_levels():
    labels = ["ESI-1", "ESI-2", "ESI-3", "ESI-4", "ESI-5"]
    counts = [18, 176, 461, 100, 18]
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    colors = [EMPH, ACCENT, "#7b8794", "#9aa5b1", "#cbd2d9"]
    bars = ax.bar(labels, counts, color=colors, width=0.72)
    for bar, value in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 8, str(value),
                ha="center", va="bottom", color=INK, fontsize=9)
    ax.set_ylim(0, 560)
    _finish(
        ax,
        "图 3-3 读图：65 岁及以上患者的 ESI 分布",
        "分诊护士给出的 ESI 级别",
        "例数",
        "来源：Platts-Mills 等，Acad Emerg Med 2010，PMID 20370755。连续 782 例中，原文各级例数合计 773，差额 9 例原文未单列，本图不补齐。其中 26 例接受立即救命干预：ESI-1 有 11 例，ESI-2 有 9 例，ESI-3 有 6 例。",
    )
    save(fig, "fig_3_3_esi_distribution")


def fig_lsi_sensitivity():
    labels = ["Platts-Mills 2010\n单中心，782 例", "Grossmann 2012\n单中心，519 例"]
    sens = [42.3, 46.2]
    lo = [42.3 - 23.3, 46.2 - 23.2]
    hi = [61.3 - 42.3, 70.9 - 46.2]
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.bar(labels, sens, color=[EMPH, ACCENT], width=0.55,
           yerr=[lo, hi], capsize=4, ecolor=MUTED, error_kw={"linewidth": 0.9})
    ax.set_ylim(0, 100)
    ax.text(0, 66, "42.3%", ha="center", color=INK, fontsize=10)
    ax.text(1, 76, "46.2%", ha="center", color=INK, fontsize=10)
    _finish(
        ax,
        "ESI-1 识别“立即救命干预”的灵敏度",
        "研究",
        "灵敏度（%）",
        "Platts-Mills 2010：灵敏度 42.3%（95% CI 23.3–61.3），特异度 99.2%。Grossmann 等，Ann Emerg Med 2012：灵敏度 0.462（95% CI 0.232–0.709），特异度 0.998。两研究都说明 ESI-1 很特异，但漏掉半数左右需要立即干预的高龄患者。",
    )
    save(fig, "fig_esi1_sensitivity")


def fig_undertriage():
    labels = ["培训前\n519 例", "一年后\n394 例"]
    under = [22.5, 24.1]
    over = [2.9, 3.6]
    import numpy as np
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    b1 = ax.bar(x - width / 2, under, width, color=EMPH, label="欠分诊")
    b2 = ax.bar(x + width / 2, over, width, color=ACCENT, label="过分诊")
    for bars in (b1, b2):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                    f"{bar.get_height():.1f}", ha="center", va="bottom", color=INK, fontsize=9)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 32)
    ax.legend(frameon=False, labelcolor=INK)
    _finish(
        ax,
        "65 岁及以上：相对专家重评的欠分诊与过分诊",
        "Grossmann 等教学干预前后",
        "占该阶段样本的百分比",
        "来源：Grossmann 等，PLoS One 2014，表 1。培训前欠分诊 117/519（22.5%）、过分诊 15/519（2.9%）；一年后欠分诊 95/394（24.1%）、过分诊 14/394（3.6%）。正文另写 24.2%，与 95/394 的四舍五入一致。差异无统计学意义。",
    )
    save(fig, "fig_undertriage_pre_post")


def fig_isar():
    import numpy as np
    labels = ["6 个月再就诊", "6 个月紧急住院", "6 个月死亡"]
    sens = [80, 82, 87]
    spec = [31, 32, 35]
    sens_err = [[80 - 70, 82 - 74, 87 - 75], [87 - 80, 88 - 82, 94 - 87]]
    spec_err = [[31 - 24, 32 - 24, 35 - 26], [38 - 31, 41 - 32, 44 - 35]]
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8.6, 5.3))
    ax.bar(x - width / 2, sens, width, color=EMPH, label="灵敏度",
           yerr=sens_err, capsize=3, ecolor=MUTED, error_kw={"linewidth": 0.8})
    ax.bar(x + width / 2, spec, width, color=ACCENT, label="特异度",
           yerr=spec_err, capsize=3, ecolor=MUTED, error_kw={"linewidth": 0.8})
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 110)
    ax.legend(frameon=False, labelcolor=INK, loc="upper right")
    _finish(
        ax,
        "表 3-3  ISAR ≥2 的合并灵敏度与特异度",
        "结局（指数急诊就诊后 6 个月）",
        "百分比",
        "来源：Galvin 等，Age Ageing 2017，DOI 10.1093/ageing/afw233。32 项验证研究，12,939 人，切点 ≥2。误差线为 95% 置信区间。特异度约三分之一，阳性不能单独决定收住院。",
    )
    save(fig, "fig_isar_galvin_6mo")


def fig_trst():
    import numpy as np
    labels = ["30 天再就诊", "90–120 天再就诊"]
    sens = [74, 66]
    spec = [43, 44]
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.bar(x - width / 2, sens, width, color=EMPH, label="灵敏度")
    ax.bar(x + width / 2, spec, width, color=ACCENT, label="特异度")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 100)
    ax.legend(frameon=False, labelcolor=INK)
    for i, (s, p) in enumerate(zip(sens, spec)):
        ax.text(i - width / 2, s + 1.5, str(s), ha="center", color=INK, fontsize=9)
        ax.text(i + width / 2, p + 1.5, str(p), ha="center", color=INK, fontsize=9)
    _finish(
        ax,
        "表 3-3  TRST 预测再次急诊就诊的合并估计",
        "随访窗口",
        "百分比",
        "来源：Rivero-Santana 等，Emergencias 2017;29:49–60。正文给出的点估计；该句未附置信区间，故本图不画误差线。全文范围：TRST 灵敏度 52%–75%，特异度 39%–51%，随结局而变。",
    )
    save(fig, "fig_trst_revisit")


def fig_esi_cstat():
    labels = ["18–64 岁", "≥80 岁"]
    cstat = [0.818, 0.754]
    lo = [0.818 - 0.814, 0.754 - 0.748]
    hi = [0.822 - 0.818, 0.759 - 0.754]
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.bar(labels, cstat, color=[ACCENT, EMPH], width=0.55,
           yerr=[lo, hi], capsize=4, ecolor=MUTED, error_kw={"linewidth": 0.9})
    ax.set_ylim(0.5, 1.0)
    ax.axhline(0.7, color=MUTED, linestyle="--", linewidth=0.8)
    ax.text(1.35, 0.708, "0.70", color=MUTED, fontsize=8)
    for i, value in enumerate(cstat):
        ax.text(i, value + 0.012, f"{value:.3f}", ha="center", color=INK, fontsize=10)
    _finish(
        ax,
        "ESI 级别对危重结局的 C 统计量，按年龄",
        "年龄",
        "C 统计量",
        "来源：Nguyen，Geriatr Gerontol Int 2026，PMID 43000685。MIMIC-IV-ED，2011–2019，418,025 次成人急诊停留。危重结局 = 急诊或住院死亡，或 24 小时内入 ICU。差值 −0.065（95% CI −0.072 至 −0.058）。纵轴从 0.50 起，避免零基线把差异压扁。",
    )
    save(fig, "fig_esi_cstat_by_age")


def fig_china_age():
    labels = ["0–15 岁\n（含不满 16 周岁）", "16–59 岁\n（含不满 60 周岁）", "60 岁及以上"]
    share = [17.1, 60.9, 22.0]
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    colors = ["#9aa5b1", ACCENT, EMPH]
    bars = ax.bar(labels, share, color=colors, width=0.62)
    for bar, value in zip(bars, share):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1.2, f"{value:.1f}%",
                ha="center", color=INK, fontsize=10)
    ax.set_ylim(0, 78)
    _finish(
        ax,
        "表 3-1  2024 年年末中国大陆人口年龄构成",
        "年龄组（统计公报口径）",
        "占全国人口的百分比",
        "来源：国家统计局《中华人民共和国 2024 年国民经济和社会发展统计公报》，2025-02-28 发布，初步数。60 岁及以上 31,031 万人（22.0%），其中 65 岁及以上 22,023 万人（15.6%），是 22.0% 的子集，不要再加一次。公报的 101.1 亿总诊疗人次含门诊和急诊，不能当作急诊分年龄表。",
    )
    save(fig, "fig_table_3_1_population")


def fig_gedi():
    labels = ["离院", "离开急诊"]
    hr = [1.19, 1.42]
    lo = [1.19 - 1.13, 1.42 - 1.33]
    hi = [1.24 - 1.19, 1.52 - 1.42]
    fig, ax = plt.subplots(figsize=(8.0, 5.2))
    bars = ax.bar(labels, hr, color=[ACCENT, EMPH], width=0.55,
                  yerr=[lo, hi], capsize=4, ecolor=MUTED, error_kw={"linewidth": 0.9})
    ax.axhline(1.0, color=MUTED, linestyle="--", linewidth=0.9)
    ax.text(1.45, 1.04, "风险比 = 1", color=MUTED, fontsize=8, ha="right")
    for bar, value in zip(bars, hr):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.08, f"{value:.2f}",
                ha="center", color=INK, fontsize=10)
    ax.set_ylim(0, 1.85)
    _finish(
        ax,
        "澳大利亚 GEDI：流程结局的风险比",
        "比较：GEDI 在岗时段 vs 不在岗时段",
        "风险比",
        "来源：Wallis 等，BMC Geriatr 2018;18:297。风险比大于 1 表示更快离院或更快离开急诊，不是停留更久。误差线为 95% 置信区间：离院 1.13–1.24，离开急诊 1.33–1.52。28 天病死率风险比 1.01（0.23–4.43），区间过宽，未画入本图。单中心前后对照，n = 44,983，年龄 ≥70 岁。",
    )
    save(fig, "fig_gedi_process_hr")


def write_table():
    TAB.mkdir(parents=True, exist_ok=True)
    rows = [
        ["工具与切点", "结局", "估计", "样本", "来源"],
        ["ISAR ≥2", "6 个月再就诊", "灵敏度 0.80（0.70–0.87）；特异度 0.31（0.24–0.38）", "32 项研究，12,939 人", "Galvin 2017 Age Ageing"],
        ["ISAR ≥2", "6 个月紧急住院", "灵敏度 0.82（0.74–0.88）；特异度 0.32（0.24–0.41）", "同上", "Galvin 2017"],
        ["ISAR ≥2", "6 个月死亡", "灵敏度 0.87（0.75–0.94）；特异度 0.35（0.26–0.44）", "同上", "Galvin 2017"],
        ["ISAR ≥2", "30 天死亡", "灵敏度 0.97（0.89–0.99）", "同上；特异度见原文表 2", "Galvin 2017 全文"],
        ["TRST", "30 天再次急诊", "灵敏度 74%；特异度 43%", "合并研究，该句未给置信区间", "Rivero-Santana 2017 Emergencias"],
        ["TRST", "90–120 天再次急诊", "灵敏度 66%；特异度 44%", "同上", "Rivero-Santana 2017"],
        ["TRST", "各结局汇总范围", "灵敏度 52%–75%；特异度 39%–51%", "系统综述", "Rivero-Santana 2017 摘要"],
        ["ISAR、TRST、VIP", "1–12 个月不良结局", "LR+ 0.98–1.40；LR− 0.53–1.11", "ISAR 19 项 14,440 人；TRST 14 项 7,016 人；VIP 4 项 1,765 人", "Carpenter 2015 Acad Emerg Med，PMID 25565487"],
        ["ESI 1 级", "立即救命干预", "灵敏度 42.3%（23.3–61.3）；特异度 99.2%（98.0–99.7）", "782 例 ≥65 岁；26 例发生干预", "Platts-Mills 2010，PMID 20370755"],
        ["ESI 1 级", "救命干预", "灵敏度 0.462（0.232–0.709）；特异度 0.998（0.989–1.000）", "519 例 ≥65 岁", "Grossmann 2012 Ann Emerg Med"],
        ["ESI 级别", "死亡或 24 小时内入 ICU 的 C 统计量", "18–64 岁 0.818（0.814–0.822）；≥80 岁 0.754（0.748–0.759）", "418,025 次停留", "Nguyen 2026，PMID 43000685"],
        ["CFS", "30 天全因死亡 AUC", "0.81（0.77–0.85）", "2,393 例 ≥65 岁；死亡 128（5.3%）", "Kaeppeli 2020 Ann Emerg Med"],
        ["CFS ≥5", "衰弱现患", "36.8%（880/2,393）", "同上；住院 AUC 0.72，入 ICU AUC 0.69", "Kaeppeli 2020"],
        ["APOP 推导", "90 天功能下降或死亡 AUC", "0.73（0.69–0.77）", "751 例 ≥70 岁；复合结局 230（30.6%）", "de Gelder 等 2016 APOP"],
        ["APOP 外部验证", "同上", "0.71（0.67–0.75）", "881 例", "de Gelder 等 2016"],
        ["APOP 死亡模型", "90 天死亡 AUC", "推导 0.79（0.73–0.85）；外部 0.67（0.60–0.73）", "推导队列死亡 71（9.5%）", "de Gelder 等 2016"],
        ["优化后 APOP", "90 天功能下降或死亡", "合并 AUC 0.71（0.69–0.73）", "2,629 例；805 人（30.6%）发生结局", "PMID 29935293"],
        ["e-triage 随机森林", "危重、紧急操作、住院", "AUC 0.73–0.92，随结局和院区变化", "172,726 次就诊；回顾性", "Levin 等 2018，DOI 10.1016/j.annemergmed.2017.08.005"],
    ]
    path = TAB / "table_3_3_performance.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)


def write_manifest():
    manifest = {
        "nhamcs_2022": {
            "source": "NCHS. National Hospital Ambulatory Medical Care Survey: 2022 Emergency Department Summary Tables. Tables 1, 4 and 24.",
            "url": "https://www.cdc.gov/nchs/data/nhamcs/web_tables/2022-nhamcs-ed-web-tables.pdf",
            "all_visits_thousands": 155398,
            "all_visits_se_thousands": 10251,
            "rate_per_100": 47.3,
            "rate_se": 3.1,
            "age_65_plus_thousands": 32935,
            "age_65_plus_se_thousands": 2702,
            "age_65_plus_percent": 21.2,
            "age_65_plus_percent_se": 1.2,
            "age_65_74_rate_per_100": 46.4,
            "age_75_plus_rate_per_100": 76.0,
            "admission_percent_of_visits": {
                "all": 11.5,
                "under_15": 3.7,
                "15_24": 4.1,
                "25_44": 6.0,
                "45_64": 14.0,
                "65_74": 23.2,
                "75_plus": 28.8,
            },
            "ambulance_percent": {
                "all": 17.0,
                "65_plus": 33.4,
                "75_plus": 39.6,
            },
            "note": "Error bars in the figures are published standard errors, not confidence intervals.",
        },
        "china_2024_communique": {
            "source": "国家统计局. 中华人民共和国 2024 年国民经济和社会发展统计公报. 2025-02-28.",
            "url": "https://www.stats.gov.cn/sj/zxfb/202502/t20250228_1958817.html",
            "population_wan": 140828,
            "age_60_plus_wan": 31031,
            "age_60_plus_percent": 22.0,
            "age_65_plus_wan": 22023,
            "age_65_plus_percent": 15.6,
            "total_visits_yi": 101.1,
            "note": "总诊疗人次包含门诊、急诊、出诊等，不是急诊分年龄就诊量。",
        },
    }
    (ROOT / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "cited_figures.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    fig_visit_rate()
    fig_visit_volume()
    fig_admission()
    fig_ambulance()
    fig_esi_levels()
    fig_lsi_sensitivity()
    fig_undertriage()
    fig_isar()
    fig_trst()
    fig_esi_cstat()
    fig_china_age()
    fig_gedi()
    write_table()
    write_manifest()
    print(f"wrote figures to {FIG}")


if __name__ == "__main__":
    main()
