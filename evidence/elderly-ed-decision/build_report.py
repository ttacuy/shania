#!/usr/bin/env python3
"""Build the elderly emergency treatment-decision evidence compilation.

Numbers are transcribed from PubMed abstracts or PMC full-text tables
retrieved on 2026-11-18. Derived rates are labeled in the report.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
DATA = ROOT / "data"
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

NAVY = "#1F4E79"
TEAL = "#2F6F6A"
CLAY = "#A15C38"
SLATE = "#5C6B73"
RED = "#8C3A3A"
GOLD = "#C4A35A"
INK = "#1C1C1C"


def setup_font() -> None:
    pdfmetrics.registerFont(TTFont("WQY", FONT_PATH, subfontIndex=0))
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["savefig.facecolor"] = "white"


def style_ax(ax, title, xlabel, ylabel):
    ax.set_title(title, loc="left", fontsize=12, color=INK, pad=10)
    ax.set_xlabel(xlabel, fontsize=9, color=SLATE)
    ax.set_ylabel(ylabel, fontsize=9, color=SLATE)
    ax.tick_params(colors=INK, labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D0D5D8")
    ax.spines["bottom"].set_color("#D0D5D8")
    ax.grid(axis="y", color="#EEF1F2", zorder=0)


def save(fig, name):
    path = FIG / name
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def write_csv(name, header, rows):
    path = DATA / name
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


def charts() -> dict[str, Path]:
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    out = {}

    centers = [
        (1, 107, 9), (2, 112, 24), (3, 372, 28), (4, 353, 40), (5, 315, 41),
        (6, 320, 33), (7, 90, 9), (8, 43, 12), (9, 9, 4), (10, 63, 13),
        (11, 82, 23), (12, 134, 52), (13, 198, 11), (14, 98, 10), (15, 350, 20),
    ]
    rates = [100 * c / n for _, n, c in centers]
    write_csv(
        "icecub_center_eligibility.csv",
        ["center", "included_n", "icu_candidate_n", "eligibility_percent_calculated"],
        [(c, n, k, round(100 * k / n, 1)) for c, n, k in centers],
    )
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    ax.bar([str(c) for c, _, _ in centers], rates, color=NAVY, zorder=2)
    ax.axhline(12.4, color=CLAY, ls="--", lw=1, label="全样本 12.4%")
    style_ax(ax, "ICE-CUB：15 家医院把 ≥80 岁患者判为可入 ICU 的比例", "医院编号", "可入 ICU 比例（%）")
    ax.legend(frameon=False, fontsize=8)
    out["icecub_centers"] = save(fig, "01_icecub_center_eligibility.png")

    labels = ["院内死亡", "6 个月死亡", "6 个月死亡或功能下降"]
    elig = [32.8, 50.6, 63.7]
    non = [26.3, 50.7, 63.2]
    write_csv(
        "icecub_outcomes.csv",
        ["outcome", "eligible_percent", "eligible_n", "not_eligible_percent", "not_eligible_n", "denominator_note"],
        [
            ["院内死亡", 32.8, "108/329", 26.3, "609/2317", "全样本 717/2646 = 27.2%"],
            ["6个月死亡", 50.6, "157", 50.7, "1107", "全样本 1264；缺失 151"],
            ["6个月死亡或功能下降", 63.7, "177", 63.2, "1256", "表5按有数据者；摘要 1433/完成随访 2495 = 57.5%"],
        ],
    )
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    import numpy as np
    x = np.arange(len(labels))
    ax.bar(x - 0.18, elig, 0.36, label="判为可入 ICU（n=329）", color=NAVY, zorder=2)
    ax.bar(x + 0.18, non, 0.36, label="判为不可入 ICU（n=2317）", color=TEAL, zorder=2)
    ax.set_xticks(x, labels)
    style_ax(ax, "ICE-CUB：收治资格判断与 6 个月结局几乎重合", "结局", "发生比例（%）")
    ax.legend(frameon=False, fontsize=8)
    out["icecub_outcomes"] = save(fig, "02_icecub_outcomes.png")

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    cats = ["入 ICU", "6 个月死亡\n（未校正）", "6 个月死亡\n（校正后 RR×对照）"]
    # display percentages for first two; third is not a percentage of a shared baseline displayed as RR converted only in table
    sys = [61, 45]
    usu = [34, 39]
    x = np.arange(2)
    ax.bar(x - 0.18, sys, 0.36, label="系统推荐入 ICU", color=CLAY, zorder=2)
    ax.bar(x + 0.18, usu, 0.36, label="常规做法", color=NAVY, zorder=2)
    ax.set_xticks(x, ["入 ICU 比例", "6 个月死亡比例"])
    style_ax(ax, "ICE-CUB2：提高入 ICU 比例没有降低 6 个月死亡", "集群随机对照，年龄 ≥75 岁", "比例（%）")
    ax.legend(frameon=False, fontsize=8)
    out["icecub2"] = save(fig, "03_icecub2.png")

    ages = ["18–44", "45–64", "65–74", "75–84", ">84"]
    refusal = [11, 15, 18, 23, 36]
    mort_acc = [10.2, 21.2, 27.9, 35.5, 41.5]
    mort_ref = [12.5, 22.3, 34.6, 40.4, 58.5]
    write_csv(
        "eldicus_age.csv",
        ["age", "refusal_percent", "mortality_if_accepted", "mortality_if_rejected", "overall_mortality"],
        list(zip(ages, refusal, mort_acc, mort_ref, [11, 21, 29, 37, 48])),
    )
    fig, ax = plt.subplots(figsize=(7.8, 4.3))
    x = np.arange(len(ages))
    ax.plot(x, mort_acc, marker="o", color=NAVY, label="收入 ICU 的 28 天死亡")
    ax.plot(x, mort_ref, marker="o", color=RED, label="拒绝入 ICU 的 28 天死亡")
    ax.bar(x, refusal, color="#D9E2EA", zorder=0, label="拒绝比例")
    ax.set_xticks(x, ages)
    style_ax(ax, "Eldicus：年龄越高越常被拒绝，拒绝者与收治者的死亡差在高龄更大", "年龄（岁）", "比例（%）")
    ax.legend(frameon=False, fontsize=8)
    out["eldicus"] = save(fig, "04_eldicus_age.png")

    models = ["未校正", "多变量回归", "工具变量\n（距离）"]
    icu_m = [35.9, 21.5, 14.8]
    ward_m = [11.7, 17.8, 20.5]
    write_csv(
        "valley_pneumonia_30day.csv",
        ["model", "icu_30day_mortality_percent", "ward_30day_mortality_percent", "absolute_difference", "ci", "p"],
        [
            ["未校正", 35.9, 11.7, 24.2, "23.8 to 24.6", "<.001"],
            ["多变量回归", 21.5, 17.8, 3.7, "3.3 to 4.0", "<.001"],
            ["工具变量", 14.8, 20.5, -5.7, "-10.6 to -0.9", ".02"],
        ],
    )
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    x = np.arange(3)
    ax.bar(x - 0.18, icu_m, 0.36, label="入 ICU", color=NAVY, zorder=2)
    ax.bar(x + 0.18, ward_m, 0.36, label="普通病房", color=TEAL, zorder=2)
    ax.set_xticks(x, models)
    style_ax(ax, "Valley 2015：肺炎老年患者，三种算法给出方向不同的 30 天死亡", "Medicare ≥65 岁肺炎，2010–2012", "30 天死亡（%）")
    ax.legend(frameon=False, fontsize=8)
    out["valley"] = save(fig, "05_valley_estimates.png")

    groups = ["收入 ICU", "未收，认为\n病情不够重", "未收，认为\n太重或太老"]
    surv1 = [40.0, 50.0, 11.5]
    write_csv(
        "andersen_triage.csv",
        ["group", "n_note", "hospital_survival_percent", "one_year_survival_percent"],
        [
            ["全部转诊", "355，拒绝 105（29.6%）", "", ""],
            ["收入 ICU", "", 56.0, 40.0],
            ["未收，认为病情不够重", "", 65.2, 50.0],
            ["未收，认为太重或太老", "", 32.7, 11.5],
        ],
    )
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(groups, surv1, color=[NAVY, TEAL, RED], zorder=2)
    style_ax(ax, "Andersen：挪威 6 院 ≥80 岁转诊后的 1 年生存", "分诊决定", "1 年生存（%）")
    out["andersen"] = save(fig, "06_andersen_survival.png")

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(["无创通气", "有创通气", "有创通气后\n肾脏替代"], [27, 43, 63], color=CLAY, zorder=2)
    style_ax(ax, "ETHICA：≥80 岁受访者拒绝未来生命支持治疗的比例", "假设情景", "拒绝比例（%）")
    out["ethica"] = save(fig, "07_ethica_refusal.png")

    cfs = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    n_cfs = [319, 756, 1723, 1446, 1097, 1127, 730, 246, 43]
    icu_d = [18.8, 24.9, 23.4, 25.5, 24.9, 29.4, 35.5, 45.9, 65.1]
    d30 = [28.5, 33.6, 33.4, 37.7, 37.9, 45.5, 55.6, 60.6, 81.4]
    withhold = [12.9, 10.3, 14.7, 18.7, 22.2, 24.4, 30.8, 21.5, 25.6]
    withdraw = [12.2, 14.2, 13.6, 13.4, 15.1, 16.2, 18.5, 15.9, 25.6]
    intub = [51.7, 55.7, 51.4, 50.6, 46.5, 48.9, 48.9, 64.6, 58.1]
    write_csv(
        "fronczek_cfs.csv",
        ["cfs", "n", "icu_death_percent", "day30_death_percent", "withhold_percent", "withdraw_percent", "intubation_percent"],
        list(zip(cfs, n_cfs, icu_d, d30, withhold, withdraw, intub)),
    )
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.plot(cfs, d30, marker="o", color=RED, label="30 天死亡")
    ax.plot(cfs, icu_d, marker="o", color=NAVY, label="ICU 死亡")
    style_ax(ax, "VIP1+VIP2：7,487 例 ≥80 岁，CFS 与短期死亡不是一条直线", "临床衰弱量表 CFS", "死亡（%）")
    ax.legend(frameon=False, fontsize=8)
    out["cfs_death"] = save(fig, "08_cfs_mortality.png")

    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.plot(cfs, withhold, marker="o", color=CLAY, label="不开始某项生命支持")
    ax.plot(cfs, withdraw, marker="o", color=RED, label="撤除生命支持")
    ax.plot(cfs, intub, marker="o", color=NAVY, label="气管插管")
    style_ax(ax, "同一队列：CFS 升高伴随更多治疗限制，插管比例并未下降", "临床衰弱量表 CFS", "患者比例（%）")
    ax.legend(frameon=False, fontsize=8)
    out["cfs_lst"] = save(fig, "09_cfs_limits_and_intubation.png")

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    names = ["年龄\n每增 1 岁", "SOFA\n每增 1 分", "CFS\n每增 1 分", "Katz\n单独模型\n每增 1 分", "IQCODE\n单独模型\n每增 1 分"]
    hrs = [1.02, 1.15, 1.12, 0.93, 1.18]
    lo = [1.01, 1.14, 1.09, 0.90, 1.06]
    hi = [1.03, 1.17, 1.15, 0.95, 1.31]
    y = np.arange(len(names))
    ax.errorbar(hrs, y, xerr=[np.array(hrs) - np.array(lo), np.array(hi) - np.array(hrs)], fmt="o", color=NAVY, capsize=3)
    ax.axvline(1, color=SLATE, lw=0.8)
    ax.set_yticks(y, names)
    style_ax(ax, "VIP2：30 天死亡 HR。CFS、Katz、IQCODE 取各自单独模型", "风险比 HR", "")
    out["vip2_hr"] = save(fig, "10_vip2_hazard.png")

    ph = ["A 极低\nSOFA", "B 呼吸\n衰竭", "C 最高龄", "D 中等\nSOFA", "E 肾衰", "F 老年特征\n低 SOFA", "G 老年特征\n高 SOFA"]
    wh = [10, 23, 39, 27, 22, 37, 40]
    d30p = [9, 21, 31, 29, 23, 24, 68]
    icup = [5, 12, 13, 20, 15, 9, 57]
    write_csv(
        "mousai_phenotypes.csv",
        ["phenotype", "n", "age_median", "cfs_median", "sofa_median", "withhold_percent", "withdraw_percent", "icu_death_percent", "day30_death_percent"],
        [
            ["A", 244, 83, 3, 1, 10, 2, 5, 9],
            ["B", 247, 83, 4, 4, 23, 10, 12, 21],
            ["C", 134, 92, 4, 4, 39, 5, 13, 31],
            ["D", 252, 83, 3, 7, 27, 12, 20, 29],
            ["E", 143, 83, 4, 6, 22, 7, 15, 23],
            ["F", 106, 84, 6, 3, 37, 8, 9, 24],
            ["G", 142, 85, 7, 11, 40, 11, 57, 68],
        ],
    )
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    x = np.arange(len(ph))
    ax.bar(x - 0.18, wh, 0.36, label="不开始生命支持", color=CLAY, zorder=2)
    ax.bar(x + 0.18, d30p, 0.36, label="30 天死亡", color=NAVY, zorder=2)
    ax.set_xticks(x, ph, fontsize=7.5)
    style_ax(ax, "VIP2 七种入院表型：限制治疗与 30 天死亡并不沿同一顺序排列", "表型", "比例（%）")
    ax.legend(frameon=False, fontsize=8)
    out["phenotype"] = save(fig, "11_phenotype_decisions.png")

    countries = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    c_wh = [32, 10, 19, 57, 21, 44, 17, 17, 9, 52]
    c_wd = [12, 6, 8, 13, 4, 8, 9, 9, 0, 9]
    write_csv(
        "mousai_country.csv",
        ["anonymized_country", "n", "withhold_percent", "withdraw_percent"],
        list(zip(countries, [217, 205, 138, 105, 92, 79, 76, 64, 55, 54], c_wh, c_wd)),
    )
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    x = np.arange(len(countries))
    ax.bar(x, c_wh, color=NAVY, zorder=2, label="不开始")
    ax.bar(x, c_wd, bottom=c_wh, color=CLAY, zorder=2, label="撤除（另计，非堆叠互斥）")
    # don't stack if not mutually exclusive. Redraw grouped.
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    ax.bar(x - 0.18, c_wh, 0.36, color=NAVY, label="不开始生命支持", zorder=2)
    ax.bar(x + 0.18, c_wd, 0.36, color=CLAY, label="撤除生命支持", zorder=2)
    ax.set_xticks(x, countries)
    style_ax(ax, "同一研究中，占样本超过 3% 的国家之间，限制治疗的比例相差数倍", "原文匿名的国家编号", "比例（%）")
    ax.legend(frameon=False, fontsize=8)
    out["country"] = save(fig, "12_country_treatment_limits.png")

    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    labs = ["CFS 2–3", "CFS 4–5", "CFS 6", "CFS ≥7"]
    hr = [1.16, 1.28, 1.56, 1.78]
    lo = [0.94, 1.06, 1.32, 1.49]
    hi = [1.43, 1.55, 1.84, 2.12]
    y = np.arange(len(labs))
    ax.errorbar(hr, y, xerr=[np.array(hr) - lo, np.array(hi) - hr], fmt="o", color=NAVY, capsize=3)
    ax.axvline(1, color=SLATE, lw=0.8)
    ax.set_yticks(y, labs)
    style_ax(ax, "Bruno 个体数据：≥65 岁 ICU 死亡，对照为 CFS 1", "校正 SOFA、性别和年龄后的 HR", "")
    out["bruno"] = save(fig, "13_bruno_cfs_hr.png")

    ages_o = ["65–74", "75–79", "80–84", "85–89", "≥90"]
    mort_o = [29, 34, 40, 43, 50]
    aor = [1.0, 1.3, 1.7, 1.9, 2.6]
    write_csv(
        "ouchi_ed_intubation.csv",
        ["age", "n", "inhospital_mortality_percent", "adjusted_or_vs_65_74"],
        list(zip(ages_o, [18901, 7708, 6877, 5167, 2810], mort_o, aor)),
    )
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.bar(ages_o, mort_o, color=NAVY, zorder=2)
    style_ax(ax, "Ouchi：美国 262 家医院，急诊插管后的院内死亡随年龄上升", "年龄（岁），非创伤、非院外停跳", "院内死亡（%）")
    out["ouchi"] = save(fig, "14_ouchi_ed_intubation.png")

    dest = ["回家\n（含家庭护理）", "护理机构", "长期急性\n照护医院", "安宁疗护"]
    days = [384, 229, 133, 10]
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.bar(dest, days, color=[TEAL, NAVY, CLAY, RED], zorder=2)
    style_ax(ax, "活着离开医院之后，中位生存天数因去向而完全不同", "出院去向，MIMIC-III，年龄 ≥75 岁", "出院后至死亡的中位天数")
    out["dest"] = save(fig, "15_survival_by_destination.png")

    sax_age = ["18–29", "30–39", "40–49", "50–59", "60–69", "70–79", "≥80"]
    sax_n = [1015662, 815214, 707641, 785815, 733716, 622107, 635021]
    sax_u = [33454, 25227, 22455, 26894, 26912, 22049, 19140]
    sax_rate = [round(100 * u / n, 2) for u, n in zip(sax_u, sax_n)]
    sax_rr = [1, 0.89, 0.84, 0.84, 0.83, 0.77, 0.66]
    write_csv(
        "sax_undertriage_by_age.csv",
        ["age", "encounters", "undertriage_n", "undertriage_percent_calculated", "adjusted_rr_vs_18_29"],
        list(zip(sax_age, sax_n, sax_u, sax_rate, sax_rr)),
    )
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.bar(sax_age, sax_rate, color=NAVY, zorder=2)
    style_ax(ax, "Sax：ESI 第 4 版，按原表计数计算的低估分诊比例", "年龄（岁），21 家美国急诊，2016–2020", "低估分诊（%）")
    out["sax"] = save(fig, "16_sax_undertriage.png")

    metrics = ["衰弱 CFS>4", "气管插管", "血管活性药", "肾脏替代", "限制生命支持", "30 天死亡"]
    nona = [58, 41, 52, 4, 40, 44]
    octa = [42, 52, 59, 12, 33, 40]
    write_csv(
        "nonagenarian_vs_octogenarian.csv",
        ["measure", "nonagenarian_percent", "octogenarian_percent", "n_nonagenarian", "n_octogenarian"],
        [
            ["衰弱 CFS>4", 58, 42, 790, 7110],
            ["气管插管", 41, 52, 790, 7110],
            ["血管活性药", 52, 59, 790, 7110],
            ["肾脏替代", 4, 12, 790, 7110],
            ["不开始和/或撤除", 40, 33, 790, 7110],
            ["30天死亡", 44, 40, 790, 7110],
            ["ICU死亡", 27, 27, 790, 7110],
        ],
    )
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    x = np.arange(len(metrics))
    ax.bar(x - 0.18, nona, 0.36, label="≥90 岁（n=790）", color=CLAY, zorder=2)
    ax.bar(x + 0.18, octa, 0.36, label="80–89 岁（n=7110）", color=NAVY, zorder=2)
    ax.set_xticks(x, metrics, fontsize=8)
    style_ax(ax, "VIP 队列：九十岁以上更少接受器官支持，30 天死亡只高 4 个百分点", "指标", "比例（%）")
    ax.legend(frameon=False, fontsize=8)
    out["nona"] = save(fig, "17_nonagenarian_intensity.png")

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.bar(["有明确收治指征", "指征不明确"], [30.9, 17.3], color=NAVY, zorder=2)
    style_ax(ax, "Garrouste-Orgeas：即使符合预先选定的 ICU 指征，多数 ≥80 岁患者未被转诊", "急诊医师使用的指征类别", "被转诊至 ICU 的比例（%）")
    out["referral"] = save(fig, "18_referral_despite_criteria.png")

    return out


# ---------- PDF ----------

def styles():
    s = {
        "h1": ParagraphStyle("h1", fontName="WQY", fontSize=18, leading=24, textColor=colors.HexColor(NAVY), spaceAfter=8),
        "h2": ParagraphStyle("h2", fontName="WQY", fontSize=13, leading=18, textColor=colors.HexColor(NAVY), spaceBefore=8, spaceAfter=6),
        "h3": ParagraphStyle("h3", fontName="WQY", fontSize=11, leading=15, textColor=colors.HexColor(TEAL), spaceBefore=6, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="WQY", fontSize=9, leading=13.5, textColor=colors.HexColor(INK), alignment=TA_LEFT, spaceAfter=6),
        "small": ParagraphStyle("small", fontName="WQY", fontSize=8, leading=11, textColor=colors.HexColor(SLATE), spaceAfter=4),
        "caption": ParagraphStyle("caption", fontName="WQY", fontSize=8, leading=11, textColor=colors.HexColor(SLATE), spaceBefore=2, spaceAfter=8),
        "cell": ParagraphStyle("cell", fontName="WQY", fontSize=7, leading=9, textColor=colors.HexColor(INK)),
        "cellh": ParagraphStyle("cellh", fontName="WQY", fontSize=7, leading=9, textColor=colors.white),
        "title": ParagraphStyle("title", fontName="WQY", fontSize=22, leading=30, textColor=colors.HexColor(NAVY), alignment=TA_LEFT, spaceAfter=8),
    }
    return s


S = None


def xml_text(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def P(text, kind="body"):
    return Paragraph(xml_text(text), S[kind])


def table(header, rows, widths=None):
    data = [[Paragraph(xml_text(c), S["cellh"]) for c in header]]
    for r in rows:
        data.append([Paragraph(xml_text(c), S["cell"]) for c in r])
    col_w = widths
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7F8")]),
        ("GRID", (0, 0), (-1, -1), 0.2, colors.HexColor("#D5DDE0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def bullet(items):
    flow = []
    for it in items:
        flow.append(ListItem(Paragraph(it, S["body"]), leftIndent=8))
    return ListFlowable(flow, bulletType="bullet", start="•", leftIndent=12, bulletFontName="WQY", bulletFontSize=9)


def build(figs: dict[str, Path]):
    global S
    S = styles()
    pdf_path = ROOT / "高龄急诊治疗决策原始数据汇编.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm, topMargin=16 * mm, bottomMargin=14 * mm,
        title="高龄急诊治疗决策原始数据汇编",
        author="文献数据汇编",
    )
    W = A4[0] - 32 * mm
    story = []

    story.append(P("高龄急诊患者治疗决策", "title"))
    story.append(P("原始研究数据与重绘图汇编", "h1"))
    story.append(P("检索日期：2026 年 11 月 18 日（北京时间）。数据来自 PubMed 摘要与 PMC 开放全文表格，不对医院病历作二次分析。", "small"))
    story.append(Spacer(1, 6))
    story.append(P("这份汇编回答一个具体问题：已经发表的原始数字，怎样说明急诊里的高龄患者接下来接受什么治疗。它紧接上传报告《高龄急诊患者预检分诊与重症治疗决策》的第四节到第八节，把治疗决定本身——转诊、收治、询问意愿、开始或限制生命支持、限时试验和筛查之后的行动——从“能否预测死亡”里分开。", "body"))
    story.append(P("阅读每张表之前先看它属于哪一类。预后关联只说明某种特征与后来的死亡一起出现。治疗效应才说明某种收治或干预策略改变了结局。决策行为描述医师实际做了什么，其中已经包含床位、习惯和患者意愿，不能倒过来当作“正确决定”的金标准。", "body"))

    story.append(P("一、汇编范围与检索", "h2"))
    story.append(P("上传报告把人群定在 ≥80 岁急诊患者，并把 ≥65 岁留作参照。本汇编沿用这个界限。研究若只纳入 ≥65、≥70 或 ≥75 岁，表中保留原年龄，不改写成高龄专属结果。ICE-CUB2 的入组是 ≥75 岁且功能较好、无恶病质、无癌症；Eldicus 是全成人分年龄；Valley 是 Medicare 肺炎。它们说明治疗决定的后果，但不能直接填进 ≥80 岁的准确性 Meta 分析。", "body"))
    story.append(P("检索使用 PubMed E-utilities，主题为：极高龄、急诊或 ICU、收治决定、治疗限制、治疗目标、限时治疗试验、衰弱。再按题名核对 ICE-CUB、ICE-CUB2、VIP1、VIP2、Eldicus、ETHICA、SOLAR、ESI 低估分诊和急诊严重疾病谈话。开放全文来自 PMC XML。无 PMC 全文时只采用 PubMed 摘要中的数字，并在来源列标明“摘要”。Springer 与 JAMA 的部分 PDF 在本次环境返回 403，未从付费全文抄录表格。未使用 Sci-Hub。", "body"))
    story.append(P("本次不是系统综述。没有双人筛选，没有偏倚评分，没有把不同研究的死亡比例做新的合并。图全部按下面各表的数字重新绘制，不是期刊原图的复制。由计数相除得到的比例，列名写明“计算”。", "body"))
    story.append(table(
        ["层次", "能说明什么", "不能说明什么"],
        [
            ["决策行为", "医师是否转诊、收治、询问、插管或限制治疗", "这个决定对患者有益"],
            ["预后关联", "CFS、SOFA、年龄与死亡的伴随关系", "降低 CFS 或拒绝 ICU 会改变死亡"],
            ["治疗效应", "随机分配或工具变量下，策略与结局的差别", "每一名患者的个体获益"],
        ],
        [28 * mm, 75 * mm, 75 * mm],
    ))
    story.append(P("图和表使用的三层标签。同一篇论文可以同时含有两层，必须分行阅读。", "caption"))

    story.append(P("二、急诊门口：谁被送去 ICU", "h2"))
    story.append(P("2.1 符合指征仍然很少被转诊", "h3"))
    story.append(P("Garrouste-Orgeas 等 2009 年在 15 家法国医院观察 ≥80 岁、至少符合一条 ICU 指征的急诊患者，共 2,646 人。指征由急诊医师用 Delphi 从 76 条初步标准中选定：44 条定为明确应收，30 条定为可商榷。PMID 19866508。数字来自摘要。", "body"))
    story.append(table(
        ["指征", "人数", "被转诊", "转诊者中实际入 ICU"],
        [
            ["明确应收", "1,426", "441（30.9%）", "231 / 441（52.4%）"],
            ["可商榷", "1,041", "181（17.3%）", "79 / 181（43.6%）"],
        ],
        [35 * mm, 30 * mm, 40 * mm, 55 * mm],
    ))
    story.append(P("来源：Garrouste-Orgeas 等，Crit Care Med. 2009；摘要。未被转诊的相关因素包括年龄（每年 OR 1.04，95%CI 1.04–1.07）、活动性肿瘤、日常功能评分较低。", "caption"))
    story.append(Image(str(figs["referral"]), width=150 * mm, height=88 * mm))
    story.append(P("图 1. 预先写成“应当考虑 ICU”的标准，并没有变成转诊。明确指征组仍有约七成没有被转诊。", "caption"))

    story.append(P("2.2 医院之间的收治资格相差数倍，结局却没有跟着分开", "h3"))
    story.append(P("Boumendil 等 ICE-CUB 研究把同一地区 15 家医院、2009 年前后一年内可能需要 ICU 的 ≥80 岁急诊患者全部纳入。2,646 人，中位年龄 86 岁（四分位 83–91），随访完成 2,495 人（94%）。急诊和 ICU 医师都认为适合入 ICU 的只有 329 人（12.4%）。院内死亡 717 人（27.2%），6 个月死亡 1,264 人（50.7%）。PMID 22509296，PMC3324496。", "body"))
    story.append(table(
        ["医院", "纳入", "判为可入 ICU", "比例（计算）", "医院", "纳入", "判为可入 ICU", "比例（计算）"],
        [
            ["1", "107", "9", "8.4%", "9", "9", "4", "44.4%"],
            ["2", "112", "24", "21.4%", "10", "63", "13", "20.6%"],
            ["3", "372", "28", "7.5%", "11", "82", "23", "28.0%"],
            ["4", "353", "40", "11.3%", "12", "134", "52", "38.8%"],
            ["5", "315", "41", "13.0%", "13", "198", "11", "5.6%"],
            ["6", "320", "33", "10.3%", "14", "98", "10", "10.2%"],
            ["7", "90", "9", "10.0%", "15", "350", "20", "5.7%"],
            ["8", "43", "12", "27.9%", "", "", "", ""],
        ],
        [18 * mm, 22 * mm, 32 * mm, 28 * mm, 18 * mm, 22 * mm, 32 * mm, 28 * mm],
    ))
    story.append(P("表 1. 原表 1 的纳入数与 ICU 候选数。比例由本汇编计算，四舍五入到 0.1。原文报告的医院间范围为 5.6%–38.8%，与第 13 院和第 12 院一致。第 9 院只有 9 人，比例不稳定。", "caption"))
    story.append(Image(str(figs["icecub_centers"]), width=160 * mm, height=82 * mm))
    story.append(P("图 2. 虚线是全样本 12.4%。校正患者特征后，医院随机截距的中位比数比是 2.25（95%CrI 1.60–3.58），组内相关 18%。也就是说，换一家医院，被判为适合 ICU 的机会可以成倍变化。", "caption"))

    story.append(table(
        ["项目", "全部 2,646", "可入 ICU 329", "不可入 ICU 2,317"],
        [
            ["年龄，均值（中位；四分位）", "87.4（86；83–91）", "85.3（84；82–87）", "87.7（87；83–92）"],
            ["女性", "62.6%（1,658）", "58.7%（193）", "63.2%（1,465）"],
            ["住家", "78.5%（2,024）", "87.8%（281）", "77.1%（1,743）"],
            ["痴呆", "19%（480）", "9.3%（29）", "20.5%（451）"],
            ["急诊测得功能，中位", "5", "6", "5"],
            ["实际入 ICU", "12.4%（327）", "97.3%（320）", "0.3%（7）"],
            ["院内死亡", "27.2%（717）", "32.8%（108）", "26.3%（609）"],
            ["6 个月死亡", "50.7%（1,264）", "50.6%（157）", "50.7%（1,107）"],
            ["6 个月死亡或功能下降", "表 5：63.3%（1,433）", "63.7%（177）", "63.2%（1,256）"],
        ],
        [48 * mm, 42 * mm, 40 * mm, 48 * mm],
    ))
    story.append(P("表 2. ICE-CUB 原表 2、3、5 的决策相关行。6 个月死亡或功能下降在摘要中为 57.5%（1,433/完成随访 2,495）。表 5 的 63.3% 使用的是去除 382 名缺失后的分母。两个数字都保留，不互相覆盖。", "caption"))
    story.append(Image(str(figs["icecub_outcomes"]), width=150 * mm, height=82 * mm))
    story.append(P("图 3. 被判为适合 ICU 的人更年轻、痴呆更少、功能更好，院内死亡反而更高（32.8% 对 26.3%）。到 6 个月，死亡以及死亡或功能下降在两组几乎相同。原文同时报告：标准化后的医院收治水平与院内死亡、6 个月死亡没有显著相关（R² 0.008 与 0.213，p = 0.767 与 0.113）。", "caption"))
    story.append(P("多水平模型里，功能评分每高 1 分，被判为可入 ICU 的 OR 为 1.32（95%CrI 1.19–1.46），6 个月死亡的 OR 为 0.85（0.80–0.91）。年龄每大 1 岁，可入 ICU 的 OR 为 0.91（0.87–0.94）。这些是决定因素和预后因素，不是收治本身的效应。", "body"))

    story.append(P("三、把“尽量收进 ICU”做成随机试验之后", "h2"))
    story.append(P("Guidet 等 ICE-CUB2，JAMA 2017，PMID 28973065。24 家法国医院集群随机。患者 ≥75 岁、无癌症、ADL ≥4、无恶病质，在急诊被判断为危及生命。干预是推动系统收治入 ICU，对照是常规做法。1 人撤回同意后分析 3,036 人，中位年龄 85 岁（81–89），男性 45%。数字来自摘要；本次未能读取全文表格。", "body"))
    story.append(table(
        ["结局", "系统收治", "常规", "比较"],
        [
            ["人数", "1,519 所在中心的参与者", "1,518", "集群随机"],
            ["入 ICU", "61%", "34%", "RR 1.80（1.66–1.95）；校正后 RR 1.68（1.54–1.82）"],
            ["6 个月死亡", "45%", "39%", "未校正 RR 1.16（1.07–1.26）"],
            ["6 个月死亡，校正后", "更高的点估计", "参照", "RR 1.05（0.96–1.14），无显著增加"],
            ["院内死亡，校正后", "更高", "参照", "RR 1.18（1.03–1.33）"],
            ["6 个月功能与体能相关生活质量", "组间无显著差异", "组间无显著差异", "摘要未给出均数"],
        ],
        [38 * mm, 42 * mm, 32 * mm, 66 * mm],
    ))
    story.append(P("表 3. ICE-CUB2 摘要中的原始比较。校正后 6 个月死亡不再显著，不能改写成“系统收治降低死亡”，也不能改写成“系统收治显著增加 6 个月死亡”。未校正的 6 个月死亡是升高的。", "caption"))
    story.append(Image(str(figs["icecub2"]), width=145 * mm, height=82 * mm))
    story.append(P("图 4. 入 ICU 从 34% 升到 61%，6 个月死亡从 39% 到 45%。这是迄今最直接的高龄急诊收治策略试验，人群比 ≥80 岁更宽，而且排除了功能很差和恶病质的患者。", "caption"))

    story.append(P("四、观察性比较里，收与不收的死亡差随年龄变大", "h2"))
    story.append(P("Sprung 等 Eldicus，11 个欧洲 ICU、7 国，2003–2005 年。6,796 名患者发生 8,472 次明确的 ICU 申请，5,602 人（82%）收入，1,194 人（18%）被拒；其中 3,795 次（49%）发生在 ≥65 岁。PMID 22001580。这是观察数据：被拒绝的人病情不同，死亡差不能当成随机试验的效应。", "body"))
    story.append(table(
        ["年龄", "拒绝比例", "该年龄死亡", "收入者死亡", "被拒者死亡"],
        [
            ["18–44", "11%", "11%", "10.2%", "12.5%"],
            ["45–64", "15%", "21%", "21.2%", "22.3%"],
            ["65–74", "18%", "29%", "27.9%", "34.6%"],
            ["75–84", "23%", "37%", "35.5%", "40.4%"],
            [">84", "36%", "48%", "41.5%", "58.5%"],
        ],
        [30 * mm, 30 * mm, 32 * mm, 32 * mm, 32 * mm],
    ))
    story.append(P("表 4. Eldicus 第二部分摘要的年龄分层。logistic 回归在校正病情严重程度后，收入相对于拒绝的死亡优势比：>65 岁 OR 0.65（0.55–0.78），<65 岁 OR 0.74（0.57–0.97）。作者的解释是高龄患者从收治中得到的死亡率差别更大。这个解释依赖“拒绝”这一观察分组，和 ICE-CUB2 的随机结果放在一起看：自由放宽收治标准并没有降低 6 个月死亡。", "caption"))
    story.append(Image(str(figs["eldicus"]), width=155 * mm, height=86 * mm))
    story.append(P("图 5. 柱是拒绝比例，线是收入者与被拒者的死亡。>84 岁被拒者死亡 58.5%，收入者 41.5%，差距大于年轻组。第一部分还建立了拒绝评分，AUC 0.77 与最终分诊评分 AUC 0.83。本汇编不收录该评分的变量权重，也不把原文提出的拒绝切点当作可用规则。用“拒绝之后仍然活着”的人来训练拒绝规则，会把当时的床位和偏见写进规则。", "caption"))

    story.append(P("4.1 工具变量给出另一个方向", "h3"))
    story.append(P("Valley 等，JAMA 2015，PMID 26393850，PMC4758179。2010–2012 年美国 2,988 家医院、1,112,394 名 >64 岁 Medicare 肺炎患者，328,404 人（30%）入 ICU。工具变量是居住地到“高 ICU 使用医院”的差别距离。离高使用医院较近的 553,597 人，ICU 使用 36%；较远的 558,797 人，使用 23%。作者估计约 13% 的患者，其入 ICU 与否只随距离变化，并称这部分决定是可斟酌的。", "body"))
    story.append(table(
        ["30 天死亡的算法", "ICU", "病房", "绝对差（95%CI）", "p"],
        [
            ["未校正", "35.9%", "11.7%", "+24.2（23.8 至 24.6）", "<0.001"],
            ["多变量回归", "21.5%", "17.8%", "+3.7（3.3 至 4.0）", "<0.001"],
            ["工具变量", "14.8%", "20.5%", "−5.7（−10.6 至 −0.9）", "0.02"],
        ],
        [38 * mm, 28 * mm, 28 * mm, 58 * mm, 22 * mm],
    ))
    story.append(P("表 5. Valley 原表 4 的死亡部分。同一批患者，回归说入 ICU 者死亡更高，工具变量说可斟酌的那部分入 ICU 后死亡更低。工具变量下的 Medicare 支付差 −1,320 美元（−3,421 至 781，p = 0.22），医院成本差 +2,842 美元（−168 至 5,851，p = 0.06），都没有显著差别。", "caption"))
    story.append(Image(str(figs["valley"]), width=145 * mm, height=82 * mm))
    story.append(P("图 6. 三条算法不能平均成一个“ICU 是否有益”的数字。未校正的巨大差别主要来自病情：ICU 组呼吸衰竭 67.4%、休克 27.5%、机械通气 48.5%，病房组分别是 16.2%、1.2% 和 2.9%。≥85 岁在 ICU 组占 26.6%（87,484/328,404），在病房组占 36.2%（284,030/783,990）。这是 ≥65 岁住院肺炎，不是急诊分诊试验。", "caption"))

    story.append(P("4.2 挪威六家医院的转诊三分法", "h3"))
    story.append(P("Andersen 等，Crit Care Med. 2017，PMID 27618269。2013 年 11 月至 2014 年 10 月，6 家医院，≥80 岁且被申请 ICU。355 人中 105 人（29.6%）被拒绝。ICU 生存 71.6%。数字来自摘要。", "body"))
    story.append(table(
        ["分组", "住院生存", "1 年生存"],
        [
            ["收入 ICU", "56.0%", "40.0%"],
            ["未收入，被认为病情不够重", "65.2%", "50.0%"],
            ["未收入，被认为太重或太老", "32.7%", "11.5%"],
        ],
        [80 * mm, 40 * mm, 40 * mm],
    ))
    story.append(P("表 6. 校正后的生存曲线显示，“太重或太老”而未收入者的生存低于另外两组。拒绝原因里，年龄大、功能差与“太重或太老”一同出现；年龄大、男性、大学医院、合并症和较低的 SAPS 3 与“病情不够重”一同出现。随访时这批被分诊的患者在自理、日常活动和焦虑抑郁上差于年龄性别匹配的对照。摘要没有给出各组人数，故表中不补人数。", "caption"))
    story.append(Image(str(figs["andersen"]), width=140 * mm, height=80 * mm))
    story.append(P("图 7. 1 年生存。把“未收入”合成一组会掩盖两个完全不同的决定。", "caption"))

    story.append(P("五、决定作出之前，患者说了什么", "h2"))
    story.append(P("Le Guen 等用 ICE-CUB 中能够表达意见的 2,115 名 ≥80 岁患者，看决定之前有没有人问过他们。只有 270 人（12.7%）被询问。医院之间从 1.1% 到 53.6%。PMID 26758531。摘要。", "body"))
    story.append(table(
        ["因素", "比值比", "95%CI"],
        [
            ["有痴呆史", "0.47", "0.25–0.83"],
            ["功能自主保留", "2.10", "1.39–3.21"],
            ["已经询问过亲属", "5.46", "3.8–7.88"],
            ["年长的主诊医师相对年轻医师", "0.48", "0.35–0.66"],
        ],
        [70 * mm, 30 * mm, 40 * mm],
    ))
    story.append(P("表 7. 被询问这一行为的相关因素，不是患者偏好的内容。", "caption"))
    story.append(P("Philippart 等 ETHICA 第一部分，115 名 ≥80 岁、应答率 87%，平均 84.8 ± 3.5 岁，68% 为女性，81% 的工具性日常生活活动独立。看过治疗情景短片后，拒绝无创通气 27%，拒绝有创通气 43%，拒绝有创通气之后的肾脏替代 63%。生活质量与这三项选择都有关。PMID 23765236。", "body"))
    story.append(Image(str(figs["ethica"]), width=140 * mm, height=80 * mm))
    story.append(P("图 8. 社区和机构中的高龄受访者并不是一律拒绝，也不是一律同意。治疗越持续、越深入，拒绝越多。", "caption"))
    story.append(P("ETHICA 第二部分让医师对同一批患者做模拟决定。217 名受邀医师中 100 名参加（46%）。认为应当给予无创通气、有创通气、通气后肾脏替代的医师分别占 85.7%、78% 和 62%。医师之间一致性低。在患者本人不同意医师最初决定的情形中，得知患者偏好后，决定被改动的比例为 39.9%、56% 和 57%。多一张床使无创通气收治增加 38.6%、有创通气增加 13.6%。与收治相关的因素包括年龄 <85 岁、生活自理和有床。PMID 23765237。", "body"))
    story.append(P("这两项放在一起，才构成治疗决定的原始结构：多数能够表达的患者没有被询问；一旦询问，医师会改掉相当一部分决定；床位本身也会改决定。", "body"))

    story.append(P("六、已经进入 ICU 之后，限制治疗的原始分布", "h2"))
    story.append(P("6.1 VIP1：衰弱与是否限制治疗", "h3"))
    story.append(P("Flaatten 等，Intensive Care Med. 2017，PMID 28936626。2016 年 10 月至 2017 年 5 月，21 国 311 个 ICU，≥80 岁连续患者。最终 5,021 人，中位年龄 84 岁（81–86），女性 2,404（47.9%），急性入院 83.9%。ICU 死亡 22.1%，30 天死亡 32.6%。23.8% 在 ICU 期间没有接受通气、血管活性药或肾脏替代。CFS ≥5 占 43.1%。衰弱相对不衰弱的 30 天生存 HR 1.54（1.38–1.73）。摘要把 HR 写在“生存”之后；HR 大于 1，在该系列后续论文中对应更高的死亡风险。本次未取得全文，没有按 CFS 每一分列出 VIP1 单独的死亡表。", "body"))
    story.append(P("Guidet 等用同一 VIP1 队列分析限制生命支持，PMID 29774388。5,021 人中 1,356 人（27.2%）发生限制：15% 为不开始，12.2% 为撤除（含此前已有不开始决定的人）。不开始组的 ICU 死亡和 30 天死亡为 29.1% 和 53.1%；撤除组为 82.2% 和 93.1%。与发生限制相关的患者以外因素：急性入院 OR 5.77（4.32–7.7），CFS OR 2.08（1.78–2.42），年龄每增 5 岁 OR 1.22（1.12–1.34），SOFA 每分 OR 1.07（1.05–1.09）。东欧和南欧少于北欧；人均 GDP 较高的国家更多，宗教性较强的国家更少。摘要没有说明 CFS 的 OR 是每分还是二分，本汇编不把它改写成每分效应。", "body"))

    story.append(P("6.2 VIP2：3,920 例的器官支持、限制和 30 天生存", "h3"))
    story.append(P("Guidet 等，Intensive Care Med. 2020，PMID 31784798，PMC7223711。2018 年 5 月至 2019 年 5 月，22 国 242 个 ICU，急性收入、≥80 岁。3,920 人，中位年龄 84 岁（81–87），男性 53.3%。80% 至少接受一项器官支持。ICU 生存 72.5%，30 天生存 61.2%（表中按 2,346/有记录者 = 61.1%，缺失 79）。", "body"))
    story.append(table(
        ["变量", "全部", "30 天存活 2,327", "30 天死亡 1,514"],
        [
            ["年龄中位（四分位）", "84（81–87）", "84（81–87）", "84（82–87）"],
            ["住自己家", "72.8%（2,852）", "76.3%", "68.1%"],
            ["住护理机构", "5.4%（210）", "4.8%", "6.3%"],
            ["SOFA 中位（四分位）", "6（4–9）", "5（3–8）", "8（5–11）"],
            ["CFS 中位（四分位）", "4（3–6）", "4（3–5）", "4（3–6）"],
            ["Katz ADL 中位", "6（4–6）", "6（5–6）", "6（3–6）"],
            ["插管", "49.9%（1,953）", "40.4%", "64.5%"],
            ["血管活性药", "59.5%（2,329）", "50.3%", "73.6%"],
            ["肾脏替代", "11.0%（429）", "7.0%", "17.1%"],
            ["无创通气", "23.1%（903）", "23.6%", "22.6%"],
            ["不开始治疗", "29.4%（1,140）", "16.9%", "49.2%"],
            ["撤除治疗", "14.0%（545）", "1.2%", "34.4%"],
            ["ICU 存活", "72.5%（2,828）", "98.6%", "31.2%"],
            ["死亡日，中位（四分位）", "—", "—", "第 7 天（3–14）"],
        ],
        [42 * mm, 42 * mm, 42 * mm, 42 * mm],
    ))
    story.append(P("表 8. VIP2 原表 1 与表 2 的决策和结局行。存活与死亡人数之和为 3,841，与 3,920 的差来自缺失。不开始与撤除可以发生在同一人，不能相加后当成“限制治疗的人数”。原表 4 把“撤除和/或不开始”合在一起，为 1,332 / 3,920。", "caption"))
    story.append(table(
        ["分层", "全部", "存活", "死亡"],
        [
            ["CFS 1–3 健壮", "1,544（39.6%）", "43.5%", "33.9%"],
            ["CFS 4 易损", "791（20.3%）", "20.8%", "19.1%"],
            ["CFS 5–8 衰弱", "1,568（40.2%）", "35.7%", "46.9%"],
            ["Katz 0–4", "962（27.7%）", "22.6%", "36.8%"],
            ["Katz 6", "2,071（59.6%）", "64.1%", "52.0%"],
            ["SOFA 0–5", "1,741（44.5%）", "56.2%", "27.1%"],
            ["SOFA 6–9", "1,286（32.9%）", "30.1%", "36.7%"],
            ["SOFA >10", "882（22.6%）", "13.7%", "36.2%"],
        ],
        [40 * mm, 45 * mm, 40 * mm, 40 * mm],
    ))
    story.append(P("表 9. VIP2 原表 3。IQCODE ≥3.5 的认知下降在有记录者中占 30.2%（899/2,980 这一分组的合计）。认知、ADL 与 CFS 高度相关；多变量模型里后两者不再增加拟合。", "caption"))

    story.append(table(
        ["模型", "变量", "HR（95%CI）"],
        [
            ["30 天死亡，只放 CFS", "CFS 每分", "1.12（1.09–1.15）"],
            ["30 天死亡，CFS+Katz+IQCODE", "CFS 每分", "1.10（1.05–1.15）"],
            ["同上", "SOFA 每分", "1.15（1.14–1.17）"],
            ["同上", "年龄每岁", "1.02（1.00–1.03）"],
            ["同上", "Katz 每分", "0.98（0.94–1.02）"],
            ["同上", "IQCODE 每分", "1.03（0.91–1.18）"],
            ["只放 Katz", "Katz 每分", "0.93（0.90–0.95）"],
            ["只放 IQCODE", "IQCODE 每分", "1.18（1.06–1.31）"],
            ["死亡模型再加入限制治疗", "CFS 每分", "1.08（1.05–1.12）"],
            ["同上", "有限制对无限制", "4.25（3.80–4.74）"],
            ["发生限制治疗的时间", "CFS 每分", "1.11（1.08–1.15）"],
            ["同上", "SOFA 每分", "1.07（1.05–1.09）"],
            ["同上", "年龄每岁", "1.04（1.03–1.06）"],
            ["同上", "住自己家对不住家", "1.27（1.12–1.45）"],
            ["同上", "急诊手术对循环衰竭", "0.67（0.54–0.83）"],
        ],
        [62 * mm, 55 * mm, 50 * mm],
    ))
    story.append(P("表 10. VIP2 原表 5 至表 7 的主要行。平均 AIC：只含 CFS 的模型 23,991，含 Katz 的 24,017，含 IQCODE 的 24,026，三者都放的 23,994。CFS 的信息没有被 ADL 或认知替代。限制治疗的 HR 4.25 是决定与死亡的伴随，死亡本身就是作出撤除决定的原因之一，不能读成“限制治疗造成 4 倍死亡”。", "caption"))
    story.append(Image(str(figs["vip2_hr"]), width=150 * mm, height=78 * mm))
    story.append(P("图 9. 单独进入模型时的 HR。Katz 分数越高死亡风险越低，所以 HR 小于 1。误差线是原文 95%CI。", "caption"))

    story.append(P("6.3 信息量：急性病情主导撤除决定，衰弱的贡献较小", "h3"))
    story.append(P("Beil 等，BMC Med Inform Decis Mak. 2023，PMID 36609257，PMC9818057。用 VIP1 与 VIP2 共 7,488 名 ≥80 岁患者，测量各项资料对“不开始”和“撤除”两个决定的熵。熵越接近最大值，说明这项资料越没有把决定分开。", "body"))
    story.append(table(
        ["", "VIP1 全部", "VIP1 不开始", "VIP1 撤除", "VIP2 全部", "VIP2 不开始", "VIP2 撤除"],
        [
            ["人数", "3,727", "1,070", "578", "3,761", "1,116", "532"],
            ["年龄中位", "84（81–87）", "84（82–87）", "84（82–87）", "84（81–87）", "84（82–88）", "84（81–86）"],
            ["女性", "48.2%", "49.2%", "43.6%", "46.7%", "47.7%", "44.4%"],
            ["CFS", "4（3–6）", "5（4–6）", "5（3–6）", "4（3–6）", "4（3–6）", "4（3–6）"],
            ["SOFA", "7（4–11）", "8（5–11）", "10（7–13）", "6（4–9）", "7（4–10）", "8（6–11）"],
        ],
        [24 * mm, 26 * mm, 28 * mm, 26 * mm, 26 * mm, 28 * mm, 26 * mm],
    ))
    story.append(P("表 11. 原表 1。VIP1 的 3,727 与 Flaatten 报告的 5,021 不是同一分析样本，引用时保留各自的分母。", "caption"))
    story.append(table(
        ["资料", "熵的最大值", "不开始 VIP1", "不开始 VIP2", "撤除 VIP1", "撤除 VIP2"],
        [
            ["年龄", "3.0", "2.98", "2.97", "2.99", "2.98"],
            ["性别", "1.0", "1.00", "1.00", "0.99", "1.00"],
            ["CFS", "3.0", "2.91", "2.95", "2.96", "2.99"],
            ["SOFA", "3.0", "2.97", "2.94", "2.78", "2.80"],
        ],
        [28 * mm, 28 * mm, 30 * mm, 30 * mm, 30 * mm, 30 * mm],
    ))
    story.append(P("表 12. 原表 2 的熵，省略了自助法标准差。撤除决定上，SOFA 的熵最低。CFS 在撤除决定上几乎贴着最大值，尤其是 VIP2 的 2.99。", "caption"))
    story.append(table(
        ["资料（KL 散度，括号内为判别到 0.5 以上的近似读数）", "不开始 VIP1", "不开始 VIP2", "撤除 VIP1", "撤除 VIP2"],
        [
            ["年龄", "0.02（0.55）", "0.02（0.56）", "0.01（0.53）", "0.01（0.51）"],
            ["CFS", "0.07（0.61）", "0.04（0.59）", "0.02（0.55）", "0.007（0.51）"],
            ["SOFA", "0.02（0.55）", "0.05（0.59）", "0.20（0.66）", "0.20（0.66）"],
            ["Katz（仅 VIP2）", "—", "0.07（0.57）", "—", "0.02（0.51）"],
        ],
        [55 * mm, 32 * mm, 32 * mm, 30 * mm, 30 * mm],
    ))
    story.append(P("表 13. 原表 3。散度越大，决定前后的分布差得越多。撤除决定上 SOFA 的散度是 CFS 的十倍量级。原文结论是：急性病情的短期预后主导了限制治疗的决定，功能结局仍然充满不确定。原表 2 括号中的比值比同时给出：撤除决定上 SOFA 每分，VIP1 为 1.12（1.10–1.15），VIP2 为 1.14（1.12–1.17）；CFS 每分，VIP1 为 1.08（1.03–1.14），VIP2 为 1.00（0.95–1.05）。", "caption"))

    story.append(P("6.4 七种入院表型，限制治疗与死亡的顺序不同", "h3"))
    story.append(P("Mousai 等，Ann Intensive Care 2023，PMID 37162595，PMC10170430。VIP2 的事后分析。聚类得到七种表型并分配到 1,268 人。这个子样本中不开始治疗 26.5%，撤除 8.1%。", "body"))
    story.append(table(
        ["表型", "n", "年龄", "CFS", "SOFA", "不开始", "撤除", "ICU 死亡", "30 天死亡"],
        [
            ["A 极低 SOFA", "244", "83", "3", "1", "10%", "2%", "5%", "9%"],
            ["B 呼吸衰竭", "247", "83", "4", "4", "23%", "10%", "12%", "21%"],
            ["C 最高龄", "134", "92", "4", "4", "39%", "5%", "13%", "31%"],
            ["D 中等 SOFA", "252", "83", "3", "7–9", "27%", "12%", "20%", "29%"],
            ["E 肾衰", "143", "83", "4", "6", "22%", "7%", "15%", "23%"],
            ["F 老年特征、低 SOFA", "106", "84", "6", "3", "37%", "8%", "9%", "24%"],
            ["G 老年特征、高 SOFA", "142", "85", "7", "11", "40%", "11%", "57%", "68%"],
        ],
        [38 * mm, 16 * mm, 16 * mm, 16 * mm, 18 * mm, 20 * mm, 18 * mm, 22 * mm, 24 * mm],
    ))
    story.append(P("表 14. 原表 1 的中位数和百分比，四分位距见 CSV。C 型是中位 92 岁、SOFA 只有 4、CFS 为 4 的最高龄患者，不开始治疗达到 39%，但 ICU 死亡只有 13%。F 型 CFS 为 6、30 天死亡 24%，不开始治疗 37%。G 型两者都高。年龄和衰弱推动的是“不开始”，急性器官衰竭推动的是死亡和撤除。", "caption"))
    story.append(Image(str(figs["phenotype"]), width=160 * mm, height=86 * mm))
    story.append(P("图 10. 不开始治疗的比例从 A 到 G 大致上升，30 天死亡在 C 型已经达到 31%，在 F 型回到 24%，到 G 型才到 68%。用一条衰弱切点同时代表“应当限制”和“必将死亡”，对不上这张图。", "caption"))
    story.append(P("以 G 型为参照，不开始治疗的 OR：A 0.17（0.10–0.29），B 0.45（0.29–0.71），C 0.95（0.58–1.5），D 0.54（0.35–0.83），E 0.42（0.25–0.70），F 0.88（0.52–1.5）。撤除治疗除 A 型 OR 0.16（0.05–0.43）外，其余表型与 G 型没有显著差异。判别限制决定的 logistic 模型，在同时放入表型、通气方式和国家后最好。国家是匿名的。", "body"))
    story.append(table(
        ["国家编号", "n", "不开始", "撤除", "国家编号", "n", "不开始", "撤除"],
        [
            ["1", "217", "32%", "12%", "6", "79", "44%", "8%"],
            ["2", "205", "10%", "6%", "7", "76", "17%", "9%"],
            ["3", "138", "19%", "8%", "8", "64", "17%", "9%"],
            ["4", "105", "57%", "13%", "9", "55", "9%", "0%"],
            ["5", "92", "21%", "4%", "10", "54", "52%", "9%"],
        ],
        [24 * mm, 18 * mm, 22 * mm, 20 * mm, 24 * mm, 18 * mm, 22 * mm, 20 * mm],
    ))
    story.append(P("表 15. 原表 2 中样本量超过全体 3% 的国家。不开始治疗从 9% 到 57%。原文没有公布国家名称。", "caption"))
    story.append(Image(str(figs["country"]), width=150 * mm, height=80 * mm))
    story.append(P("图 11. 同一套入组标准下，限制治疗的比例首先是一项国家实践，其次才是一项患者特征。", "caption"))

    story.append(P("6.5 CFS 每一分上的死亡、插管和限制", "h3"))
    story.append(P("Fronczek 等把 VIP1 与 VIP2 连在一起，Critical Care 2021，PMID 34210358，PMC8247215。连续 ≥80 岁患者 7,487 人，中位年龄 84 岁（81–87）。30 天死亡 2,985（39.9%），ICU 死亡 2,024（27.0%）。把 CFS 当作分类变量或非线性连续变量时，衰弱为 30 天死亡模型新增的预后信息占 9%（似然比检验 p < 0.001）。二分成衰弱与否只剩下 5%。关系是非线性的（p < 0.01）。", "body"))
    story.append(table(
        ["CFS", "n", "插管", "不限制", "不开始", "撤除", "ICU 死亡", "30 天死亡"],
        [
            ["1", "319", "51.7%", "74.9%", "12.9%", "12.2%", "18.8%", "28.5%"],
            ["2", "756", "55.7%", "75.5%", "10.3%", "14.2%", "24.9%", "33.6%"],
            ["3", "1,723", "51.4%", "71.7%", "14.7%", "13.6%", "23.4%", "33.4%"],
            ["4", "1,446", "50.6%", "67.9%", "18.7%", "13.4%", "25.5%", "37.7%"],
            ["5", "1,097", "46.5%", "62.7%", "22.2%", "15.1%", "24.9%", "37.9%"],
            ["6", "1,127", "48.9%", "59.4%", "24.4%", "16.2%", "29.4%", "45.5%"],
            ["7", "730", "48.9%", "50.7%", "30.8%", "18.5%", "35.5%", "55.6%"],
            ["8", "246", "64.6%", "62.6%", "21.5%", "15.9%", "45.9%", "60.6%"],
            ["9", "43", "58.1%", "48.8%", "25.6%", "25.6%", "65.1%", "81.4%"],
        ],
        [16 * mm, 20 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm, 24 * mm, 26 * mm],
    ))
    story.append(P("表 16. Fronczek 原表 1。CFS 8 和 9 的人数少，比例不稳定。插管在 CFS 1 到 7 之间保持在 46%–56%，CFS 8 为 64.6%。高衰弱并没有对应“已经不再插管”。不开始治疗从 CFS 2 的 10.3% 升到 CFS 7 的 30.8%，随后在 CFS 8 降到 21.5%。", "caption"))
    story.append(Image(str(figs["cfs_death"]), width=155 * mm, height=84 * mm))
    story.append(P("图 12. 30 天死亡从 CFS 4 的 37.7% 到 CFS 5 的 37.9% 几乎不动，到 CFS 6 才到 45.5%，CFS 7 到 55.6%。以 CFS ≥5 作为唯一行动切点，会把 4 分和 5 分几乎相同的死亡风险切成两类，又会把 7 分以上明显不同的风险合成一类。", "caption"))
    story.append(Image(str(figs["cfs_lst"]), width=155 * mm, height=84 * mm))
    story.append(P("图 13. 蓝线是插管。衰弱升高时，限制治疗增多，但已经发生的插管并不减少。决策时要分开“还没有开始的治疗”和“已经开始的治疗”。", "caption"))

    story.append(P("6.6 九十岁与八十岁：治疗强度下降，死亡没有同步下降那么多", "h3"))
    story.append(P("Bruno 等，BMC Geriatr. 2021，PMID 34666709，PMC8524896。VIP1+VIP2 急性入院 7,900 人，≥90 岁 790 人（10%），80–89 岁 7,110 人。", "body"))
    story.append(table(
        ["指标", "≥90 岁", "80–89 岁", "未进一步校正的比较"],
        [
            ["CFS >4", "58%", "42%", "p < 0.001"],
            ["SOFA 中位", "6（4–9）", "7（4–10）", "p < 0.001"],
            ["插管", "41%", "52%", "p < 0.001"],
            ["血管活性药", "52%", "59%", "p = 0.002"],
            ["肾脏替代", "4%", "12%", "p < 0.001"],
            ["无创通气", "21%", "23%", "p = 0.03"],
            ["不开始和/或撤除", "40%", "33%", "p < 0.001"],
            ["ICU 死亡", "27%", "27%", "p = 0.97"],
            ["30 天死亡", "44%（337）", "40%（2,743）", "p = 0.029"],
        ],
        [42 * mm, 32 * mm, 36 * mm, 50 * mm],
    ))
    story.append(P("表 17. 原表 1 的主要行。表 2 的多水平模型：30 天死亡，模型 1 的 aOR 1.39（1.13–1.72），模型 2 的 aOR 1.25（0.90–1.74，p = 0.19）。插管的 aOR 从模型 1 的 0.72（0.56–0.93）到模型 2 的 1.26（0.85–1.87）。肾脏替代模型 1 的 aOR 0.32（0.19–0.53）。原文没有在摘出的主表里逐项列出两个模型的协变量，本汇编不补写。摘要采用的校正后 30 天死亡 aOR 是 1.25（0.90–1.74）。", "caption"))
    story.append(Image(str(figs["nona"]), width=158 * mm, height=86 * mm))
    story.append(P("图 14. 九十岁以上的人更衰弱、更少接受插管和肾脏替代、更常被限制治疗。ICU 死亡同为 27%。年龄超过 90 本身没有在这张图里表现为另一条死亡曲线。", "caption"))
    story.append(P("更早的 Outcomerea 匹配研究（Garrouste-Orgeas，Ann Intensive Care 2016，PMID 27076186，PMC4830777）在 12 个 ICU、1997–2013 年，把 176 名 >90 岁患者与 176 名 80–90 岁患者按病情、中心和年份匹配。动脉测压 21% 对 30.1%（p = 0.04），肾脏替代 2.8% 对 8%（p = 0.05）。入院 48 小时内预先不开始治疗 9.1% 对 10.2%。ICU 死亡 25% 对 20.5%（p = 0.34），住院死亡 39.8% 对 36.4%（p = 0.54）。只有 16/176（14%）转到老年病房。这是被选入 ICU 的九十岁患者，不是急诊里所有九十岁患者。", "body"))

    story.append(P("七、用来谈话的预后数字，以及它们不是治疗效应", "h2"))
    story.append(P("7.1 急诊插管之后的院内去向", "h3"))
    story.append(P("Ouchi 等，J Am Geriatr Soc. 2018，PMID 29542117，PMC6320691。2008–2015 年美国 262 家医院，≥65 岁、在急诊完成插管，排除创伤和院外插管或心跳骤停。识别 41,463 次，分析 35,036 次。全体院内死亡 33%。摘要把 95%CI 印成 34%–35%，点估计落在区间外，属于原文表述不一致；年龄分层的比例和区间是对齐的，下表采用分层数字。24% 出院回家，41% 出院到家以外的地方。", "body"))
    story.append(table(
        ["年龄", "人数（占分析集）", "院内死亡（95%CI）", "校正 OR"],
        [
            ["65–74", "18,901（46%）", "29%（28–29%）", "参照"],
            ["75–79", "7,708（19%）", "34%（33–35%）", "1.3（1.2–1.4）"],
            ["80–84", "6,877（17%）", "40%（39–41%）", "1.7（1.6–1.8）"],
            ["85–89", "5,167（12%）", "43%（42–44%）", "1.9（1.8–2.1）"],
            ["≥90", "2,810（7%）", "50%（48–51%）", "2.6（2.4–2.9）"],
        ],
        [28 * mm, 42 * mm, 48 * mm, 40 * mm],
    ))
    story.append(P("表 18. 原表 1。校正了种族、合并症、入院诊断、医院去向和地区。≥80 岁三组合计 14,854 人，死亡从 40% 到 50%。这是已经插管之后的预后，用来支持谈话，不能用来证明“不插管会更好”或“应当插管”。", "caption"))
    story.append(Image(str(figs["ouchi"]), width=145 * mm, height=80 * mm))
    story.append(P("图 15. 急诊插管后的院内死亡。80–84 岁是 40%，不是年轻老年组的 29%。", "caption"))
    story.append(table(
        ["入院诊断", "人数", "院内死亡", "校正 OR"],
        [
            ["呼吸衰竭", "11,073（32%）", "26%（25–26%）", "0.5（0.5–0.6）"],
            ["败血症", "3,920（11%）", "43%（42–45%）", "1.5（1.4–1.6）"],
            ["脑血管病", "3,471（10%）", "54%（53–56%）", "2.4（2.2–2.6）"],
            ["意识改变或抽搐", "5,259（15%）", "29%（27–30%）", "0.7（0.7–0.8）"],
            ["心力衰竭", "505（1%）", "23%（20–27%）", "0.5（0.4–0.7）"],
        ],
        [40 * mm, 38 * mm, 42 * mm, 40 * mm],
    ))
    story.append(P("表 19. 同一插管队列里，诊断改变死亡。谈话时只报一个“高龄插管死亡约三分之一”，会把脑血管病的 54% 和呼吸衰竭的 26% 说成同一件事。", "caption"))

    story.append(P("7.2 活过住院之后的天数", "h3"))
    story.append(P("Ouchi 等，J Pain Symptom Manage. 2020，PMID 32540468，PMC8164382。单中心 MIMIC-III，2008–2012 年，≥75 岁、非择期、接受机械通气。415 名患者、454 次住院，中位年龄 82.6 岁，院内死亡 36.6%（166/454）。幸存者出院后中位生存 163.5 天（四分位 37.5–476.8）。48 小时内有记录的严重疾病谈话只占 49.1%。转入长期急性照护医院的 93 人中，59 人（63%）在 6 个月内死亡。", "body"))
    story.append(table(
        ["出院时状态", "住院次数", "出院后至死亡的中位天数（四分位）"],
        [
            ["死亡", "166", "不适用"],
            ["家庭护理 / 回家", "45", "384（71–667）"],
            ["安宁疗护", "11", "10（4.5–12）"],
            ["长期急性照护医院", "93", "133（50–283）"],
            ["护理机构", "139", "229（41.5–574）"],
        ],
        [55 * mm, 35 * mm, 80 * mm],
    ))
    story.append(P("表 20. 原表 1。80% 的入院来自急诊。这是一家教学医院的数据库，外推时保留单中心这一限制。", "caption"))
    story.append(Image(str(figs["dest"]), width=145 * mm, height=80 * mm))
    story.append(P("图 16. 中位天数。安宁疗护组只有 11 次住院。回家与进入长期急性照护医院，是两种不同的存活轨迹。", "caption"))

    story.append(P("7.3 ≥65 岁的 CFS 与 ICU 死亡，个体数据", "h3"))
    story.append(P("Bruno 等，Ann Intensive Care 2023，PMID 37133796，PMC10155148。检索至 2020 年 6 月 24 日，12 项研究、30 国，排除择期手术后 23,989 人。≥65 岁 14,356 人。任一治疗限制在有记录的 ≥65 岁患者中占 33.3%（2,736/8,205），<65 岁只占 9.2%（38/414）。ICU 死亡：<65 岁 11.9%，≥65 岁 24%。", "body"))
    story.append(table(
        ["≥65 岁，校正 SOFA、性别、年龄", "HR（95%CI）"],
        [
            ["CFS 4 对健壮，完整病例", "1.10（1.05–1.16）"],
            ["CFS 5–8 对健壮，完整病例", "1.34（1.25–1.44）"],
            ["CFS 4，多重插补", "1.10（1.04–1.17）"],
            ["CFS 5–8，多重插补", "1.35（1.26–1.45）"],
            ["SOFA 每分", "1.14（1.10–1.19）"],
            ["年龄每增 5 岁", "1.20（1.15–1.25）"],
            ["CFS 4–5 对 CFS 1", "1.28（1.06–1.55）"],
            ["CFS 6 对 CFS 1", "1.56（1.32–1.84）"],
            ["CFS ≥7 对 CFS 1", "1.78（1.49–2.12）"],
            ["CFS 2–3 对 CFS 1", "1.16（0.94–1.43）"],
        ],
        [90 * mm, 55 * mm],
    ))
    story.append(P("表 21. 原表 4 与表 5 中 ≥65 岁的行。脆弱（CFS 4）与衰弱（CFS 5–8）在校正后都高于 CFS 1–3，但原文摘要写明：只把“脆弱”与“衰弱”相比，二者没有显著差别。因此“CFS ≥5 才开始算数、CFS 4 可以忽略”不被这组个体数据支持；“CFS 4 与 CFS 7 是同一风险”也不被支持。", "caption"))
    story.append(Image(str(figs["bruno"]), width=145 * mm, height=78 * mm))
    story.append(P("图 17. 对照固定为 CFS 1。误差线跨过 1 的只有 CFS 2–3。", "caption"))

    story.append(P("7.4 床旁累计评分的运行特性，不收录未在正文列出的赋分", "h3"))
    story.append(P("de Lange 等，J Am Geriatr Soc. 2019，PMID 30977911，PMC6850576。VIP1 急性入院且 30 天资料完整的 3,730 人（占急性入院 4,252 人的 88%），24 国 306 个 ICU，中位年龄 84 岁。ICU 死亡 1,065（28.6%），30 天死亡 1,562（41.9%）。模型纳入年龄、性别、入院诊断、CFS、SOFA、有创通气和肾脏替代。评分 ≥10 的 AUC 0.80，Brier 评分 0.18。正文写明赋分表在补充材料，本次 XML 没有包含可逐分核对的赋分，故不重造一份分数表。", "body"))
    story.append(table(
        ["协变量", "30 天死亡 OR（95%CI）"],
        [
            ["年龄", "1.05（1.03–1.07）"],
            ["男性", "1.26（1.09–1.47）"],
            ["机械通气", "2.07（1.72–2.50）"],
            ["肾脏替代", "1.70（1.33–2.18）"],
            ["CFS", "1.19（1.14–1.25）"],
            ["SOFA 4 至 <7，对照 <4", "1.80（1.37–2.37）"],
            ["SOFA 7 至 <10", "2.70（2.02–3.60）"],
            ["SOFA ≥10", "4.40（3.26–5.92）"],
        ],
        [70 * mm, 55 * mm],
    ))
    story.append(P("表 22. 原表 2 的主要 OR。入院诊断的 OR 以中毒为参照，置信区间很宽（例如呼吸循环联合衰竭 4.55，0.92–22.43），不适合单独拿来谈话。", "caption"))
    story.append(table(
        ["切点", "阳性预测值", "阴性预测值", "其他"],
        [
            [">10 分，覆盖 75% 患者", "50.6%", "85.8%", "能标出 91.1% 的死亡者"],
            [">12", "55.9%", "81.1%", ""],
            [">16", "67.6%", "69.2%", ""],
            [">20", "77.0%", "60.5%", ""],
        ],
        [48 * mm, 32 * mm, 32 * mm, 55 * mm],
    ))
    story.append(P("表 23. 原图 1 说明中的运行特性。即使超过 20 分，仍有约 23% 的阳性预测没有在 30 天死亡。分数用于打开谈话，不用于自动生成治疗限制。", "caption"))

    story.append(P("八、改变决策过程的试验", "h2"))
    story.append(P("8.1 急诊里的老年综合评估缩短停留，但不是复苏试验", "h3"))
    story.append(P("Leahy 等 SOLAR，Lancet Healthy Longev. 2024，PMID 39541993。爱尔兰一家医院，≥75 岁、内科、ISAR ≥2。排除需要复苏、新冠、精神、外科和创伤。2020 年 11 月 9 日至 2021 年 5 月 13 日纳入 228 人。干预组 113 人，平均 82.4 ± 4.9 岁；对照 115 人，平均 83.1 ± 5.6 岁。", "body"))
    story.append(table(
        ["急诊停留时间", "老年团队综合评估", "常规"],
        [
            ["中位数（四分位）", "11.5 小时（5–27）", "20 小时（7–29）"],
            ["Hodges–Lehmann 中位差", "3.1 小时（95%CI 0.6–7.5）", "p = 0.013"],
        ],
        [48 * mm, 60 * mm, 55 * mm],
    ))
    story.append(P("表 24. 两个中位数相减是 8.5 小时，试验报告的效应估计是 3.1 小时。摘要还报告护理院入住更低、30 天和 180 天的生活质量下降更小、功能下降更少，但没有给出这些次要结局的原始百分比。本汇编不补写百分比。没有与干预相关的不良事件。", "caption"))

    story.append(P("8.2 急诊严重疾病谈话增加了病历记录，没有改变患者自报的参与", "h3"))
    story.append(P("Ouchi 等，JAMA Netw Open. 2025，PMID 40531532，PMC12177648。141 名急诊中病情进展期的成人，平均 66.7 ± 9.2 岁，范围 50–92 岁。这不是 ≥80 岁试验。护士主导的谈话对照常规。主要患者自报的预先照护参与没有显著提高。6 个月时，病历中由临床人员记录的临终价值观：干预 22/70（31.4%），对照 9/71（12.7%），p = 0.008。6 个月死亡两组都是 4 人，合计 8/141（5.7%）。", "body"))
    story.append(table(
        ["6 个月病历记录", "对照 71", "干预 70", "p"],
        [
            ["医疗代理人表格", "4（5.6%）", "10（14.3%）", "0.10"],
            ["生命支持医嘱表格", "5（7.0%）", "8（11.4%）", "0.40"],
            ["临床记录的价值观与偏好", "9（12.7%）", "22（31.4%）", "0.008"],
        ],
        [55 * mm, 35 * mm, 35 * mm, 25 * mm],
    ))
    story.append(P("表 25. 原表 3 的 6 个月行。1 个月和 3 个月的记录数更低，见 CSV。", "caption"))

    story.append(P("8.3 在 29 家急诊培训姑息照护，没有改变住院和生存", "h3"))
    story.append(P("Grudzen 等 PRIM-ER，JAMA 2025，PMID 39813042。29 家美国急诊的阶梯楔形集群试验。2018 年 5 月 1 日至 2022 年 12 月 31 日，≥66 岁、前 12 个月有 Medicare、Gagne 合并症分 >6（对应短期死亡风险 >30%），排除护理院。98,922 次首诊，中位年龄 77 岁（71–84）。干预是教育、谈话模拟、决策支持和反馈。", "body"))
    story.append(table(
        ["结局", "干预前", "干预后", "校正 OR（95%CI）"],
        [
            ["住院", "64.4%", "61.3%", "1.03（0.93–1.14）"],
            ["入 ICU", "7.8%", "6.7%", "0.98（0.83–1.15）"],
            ["再次急诊至少一次", "34.2%", "32.2%", "1.00（0.91–1.09）"],
            ["安宁疗护", "17.7%", "17.2%", "1.04（0.93–1.16）"],
            ["家庭护理", "42.0%", "38.1%", "1.01（0.92–1.10）"],
            ["再入院至少一次", "41.0%", "36.6%", "1.01（0.92–1.10）"],
            ["死亡", "28.1%", "28.7%", "1.07（0.98–1.18）"],
        ],
        [42 * mm, 32 * mm, 32 * mm, 55 * mm],
    ))
    story.append(P("表 26. 粗住院率下降 3.1 个百分点（95%CI −3.7 至 −2.5），校正后 OR 含 1。培训和电脑提示没有改变这组高死亡风险老年人的住院、ICU、安宁疗护或死亡。中位年龄 77 岁，不是 ≥80 岁专属队列。", "caption"))

    story.append(P("九、分诊级别没有测到治疗决定", "h2"))
    story.append(P("上传报告已经核对过分诊准确性。这里只保留那些直接关系到“分诊之后治疗强度会不会改变”的原始数字。", "body"))
    story.append(P("9.1 同一分诊级别里，≥80 岁的住院和死亡仍然更高", "h3"))
    story.append(P("Ginsburg 等，Am J Emerg Med. 2021，PMID 33191046。一家学术急诊连续一年，年龄 ≥40 岁，主诉为胸痛、腹痛、意识改变、乏力或头痛，共 9,798 次就诊。校正 ESI 和主诉后，相对于 40–64 岁：", "body"))
    story.append(table(
        ["结局", "65–79 岁", "≥80 岁"],
        [
            ["急诊化验", "OR 1.46（1.29–1.66）", "OR 1.33（1.15–1.55）"],
            ["急诊影像", "OR 1.40（1.26–1.56）", "OR 1.48（1.30–1.69）"],
            ["住院", "OR 1.56（1.42–1.72）", "OR 1.97（1.75–2.21）"],
            ["入 ICU", "OR 1.38（1.15–1.65）", "OR 1.23（0.99–1.52）"],
            ["30 天死亡", "HR 1.87（1.39–2.51）", "HR 2.47（1.81–3.37）"],
        ],
        [35 * mm, 60 * mm, 65 * mm],
    ))
    story.append(P("表 27. 摘要。≥80 岁的住院和 30 天死亡明显高于同级别、同主诉的中年患者，入 ICU 的 OR 置信区间含 1。上传报告写明该研究排除 ESI 1 和 5。这一排除写在上传报告中，不在本次取得的摘要句子里，故未作为已复核的原文事实重复使用。摘要没有给出各组人数。", "caption"))

    story.append(P("9.2 大规模急诊里，≥80 岁的低估分诊比例并不更高", "h3"))
    story.append(P("Sax 等，JAMA Netw Open. 2023，PMID 36930151，PMC10024207。21 家美国急诊，2016–2020 年，ESI 第 4 版，5,315,176 次成人就诊。低估 176,131，高估 1,537,129，合适 3,601,916。识别危重患者的敏感度 66%（全体，不是年龄分层）。", "body"))
    story.append(table(
        ["年龄", "就诊", "低估人数", "低估比例（计算）", "校正 RR，对照 18–29 岁"],
        [
            ["18–29", "1,015,662", "33,454", "3.29%", "1"],
            ["30–39", "815,214", "25,227", "3.09%", "0.89（0.87–0.90）"],
            ["40–49", "707,641", "22,455", "3.17%", "0.84（0.83–0.86）"],
            ["50–59", "785,815", "26,894", "3.42%", "0.84（0.82–0.85）"],
            ["60–69", "733,716", "26,912", "3.67%", "0.83（0.82–0.85）"],
            ["70–79", "622,107", "22,049", "3.54%", "0.77（0.76–0.79）"],
            ["≥80", "635,021", "19,140", "3.01%", "0.66（0.65–0.68）"],
        ],
        [28 * mm, 32 * mm, 32 * mm, 38 * mm, 48 * mm],
    ))
    story.append(P("表 28. 人数来自原表 2，比例由本汇编计算。≥80 岁 19,140/635,021 = 3.013%，与上传报告的 3.01% 一致。校正 RR 来自原表 3。这里的低估包含事后资源使用和关键干预，与专家复核不是同一个定义。高估的校正 RR 在 ≥80 岁是 0.70（0.69–0.70）。", "caption"))
    story.append(Image(str(figs["sax"]), width=150 * mm, height=82 * mm))
    story.append(P("图 18. 按这一定义，≥80 岁不是低估比例最高的年龄。不能据此说高龄分诊已经足够，因为定义测的是资源，不是漏掉的救命干预。", "caption"))

    story.append(P("9.3 专家复核的低估，一次教学没有降下来", "h3"))
    story.append(P("Grossmann 等，PLoS One 2014，PMID 25153120，PMC4143318。同一家城市急诊，≥65 岁。教学前 519 人，低估 117（22.5%）；一年后 394 人，低估 95（24.1%）。卡方 0.248，p = 0.619。摘要写成 24.2%，表内为 24.1%，两数都保留。2012 年队列（PMID 22401951）报告 ESI 1 对救命干预的敏感度 0.462（0.232–0.709）、特异度 0.998。", "body"))
    story.append(table(
        ["低估原因", "教学前，占 117 人", "教学后，占 95 人"],
        [
            ["需要救命干预", "4（3.4%）", "2（2.1%）"],
            ["高危情境", "29（24.8%）", "22（24.2%）"],
            ["意识模糊、嗜睡或定向障碍", "3（2.6%）", "3（3.2%）"],
            ["严重疼痛或痛苦", "17（14.5%）", "10（10.5%）"],
            ["资源判断", "25（21.4%）", "24（25.3%）"],
            ["危险区生命体征", "20（17.1%）", "8（8.4%）"],
            ["高危情境加危险区生命体征", "4（3.4%）", "17（17.9%）"],
            ["原因未记录", "8（6.8%）", "4（4.2%）"],
        ],
        [70 * mm, 45 * mm, 45 * mm],
    ))
    story.append(P("表 29. 原表 2 的主要原因。高危情境和生命体征解释占了大部分，不是一个单纯的年龄按钮可以修正的。呼吸频率没有测量相对于已测量，正确分诊的 OR 为 4.52（1.99–10.27）。", "caption"))
    story.append(P("Platts-Mills 等，Acad Emerg Med. 2010，PMID 20370755。单中心一个月，≥65 岁 782 人。ESI 1 为 18 人，ESI 2 为 176 人，ESI 3 为 461 人。26 人接受即时救命干预：ESI 1 有 11 人，ESI 2 有 9 人，ESI 3 有 6 人。以 ESI = 1 为阳性阈值，敏感度 42.3%（23.3–61.3%），特异度 99.2%（98.0–99.7%）。不能把这个敏感度改写成“ESI 漏掉近六成危重患者”，因为 9 名 ESI 2 的患者已经在高优先级。", "body"))

    story.append(P("9.4 急迫等级和衰弱几乎不相关", "h3"))
    story.append(P("Mowbray 等，CJEM 2020，PMID 31718719。2009 年 11 月至 2012 年 4 月，加拿大 8 家急诊，≥75 岁 2,153 人。CTAS 与急诊衰弱指数的 Spearman r = 0.001，p = 0.99。衰弱指数每增加 0.1：住院 OR 1.5（1.4–1.6），住院日 OR 1.4（1.2–1.6），以后再住院 OR 1.1（1.05–1.2），再次急诊 OR 1.1（1.04–1.2）。CTAS 2 相对 CTAS 5 的住院 OR 为 6（3.3–11.4）。数据采集早于 2016 年 CTAS 衰弱修正，不能当作该修正规则的实施效果。", "body"))

    story.append(P("十、限时试验和跨国做法：有框架，少有患者级效应", "h2"))
    story.append(P("Beil 等，Ann Intensive Care 2023，PMID 37884827，PMC10603016。用一名 87 岁、CFS 4、无认知障碍、无创通气失败后进入 ICU 的情景，收集 10 个国家或地区重症医师的做法。这是专家意见，不是患者结局。", "body"))
    story.append(table(
        ["地区", "不确定时的做法", "情景中考虑限制的触发", "老年或姑息专科"],
        [
            ["澳大利亚", "ICU 内或 ICU 外的治疗试验", "急性肾损伤", "很少"],
            ["巴西", "ICU 内限时试验", "需要透析的急性肾损伤", "很少"],
            ["加拿大", "ICU 内限时试验", "急性肾损伤、卒中", "姑息"],
            ["中国", "ICU 试验，与法定代理人讨论", "治疗没有相应反应", "姑息"],
            ["英格兰", "ICU 试验", "急性肾损伤", "姑息，老年医学很少"],
            ["中国香港", "ICU 内限时试验", "大剂量血管活性药、急性肾损伤、卒中", "很少"],
            ["以色列", "ICU 试验", "痛苦增加、可接受的功能结局可能性下降", "老年医学很少"],
            ["利比亚", "与家属、同事讨论", "因患者价值观而个体化", "有老年或姑息经验的医师"],
            ["挪威", "ICU 内或外的治疗试验", "急性肾损伤", "很少"],
            ["波兰", "ICU 内限时试验", "卒中", "很少"],
        ],
        [28 * mm, 52 * mm, 58 * mm, 40 * mm],
    ))
    story.append(P("表 30. 原表 2 的三列。中国与中国香港在原文中分开列出。共同的做法是给不确定留一段有复评点的治疗，而不是在入院当时一次性写死。触发点高度依赖器官衰竭的出现，不是一个统一的天数。原文举例的法律条文没有整段转录。", "caption"))
    story.append(P("Vink 等对限时试验的综述（Intensive Care Med. 2018，PMID 30136140）和 Hashimoto 等把限时试验嵌进急诊的随机方案（PLoS One 2024，PMID 39715103）没有提供新的患者结局。ESICM 2025 年共识（Beil 等，PMID 39961851）由 28 名指导组成员和另外 82 名专家完成两轮 Delphi，对达成共识的 48 条陈述和 2 份清单给出建议。强共识定义为 9 点量表高端或低端至少 90% 同意，中等共识为至少 80%。本次没有取得陈述全文，不编造任何一条推荐的措辞或同意比例。Guidet 等 2024 年轨迹综述（PMID 38236292）是上传报告的源头文献，属于专家综述，不提供新的患者级分母。", "body"))

    story.append(P("十一、这些数字怎样落在上传报告的条款上", "h2"))
    story.append(P("上传报告的条款仍是草案。下表只指出哪一组原始数字与哪一条有关，不把条款改写成已生效的标准。", "body"))
    story.append(table(
        ["上传报告中的决定", "直接相关的原始数字", "数字不允许的推论"],
        [
            ["先抢救，衰弱评估不挡在前面", "Platts-Mills：26 名救命干预里 6 名在 ESI 3；Grossmann：低估主因是高危情境和生命体征", "先做完 CFS 再开始复苏"],
            ["年龄或 CFS 单独不能降低急迫等级或拒绝 ICU", "Fronczek：CFS 7 的 30 天死亡 55.6%，仍有 44% 存活；ICE-CUB2：系统收治未降低 6 个月死亡", "CFS 高分即无效，或所有 ≥80 岁都应入 ICU"],
            ["急迫等级和衰弱是两套信息", "Mowbray：r = 0.001；Ginsburg：同 ESI 下 ≥80 岁住院 OR 1.97", "用一个分数代替两个决定"],
            ["筛查必须接上行动，行动本身要被验证", "SOLAR：综合评估缩短急诊停留；PRIM-ER：培训后住院 aOR 1.03", "有筛查工具就等于患者获益"],
            ["询问患者，并允许决定改变", "Le Guen：仅 12.7% 被询问；ETHICA：得知偏好后 40%–57% 的分歧决定被修改", "家属不在场就视为拒绝"],
            ["不确定时做有复评点的限时试验", "10 个地区的专家都描述试验，没有共同天数；VIP2 死亡中位发生在第 7 天", "把某一篇评论里的 2 天或 5 天写成通用时限"],
            ["≥90 岁单独统计，避免系统性降级", "VIP：≥90 岁插管 41%、肾脏替代 4%、ICU 死亡仍为 27%", "年龄超过 90 即不适合器官支持"],
            ["终点同时看生存和功能", "ICE-CUB：6 个月死亡约 50%，死亡或功能下降在完整随访中 57.5%；Ouchi：回家者中位再生存 384 天，长期急性照护 133 天", "只报告住院死亡"],
        ],
        [42 * mm, 70 * mm, 66 * mm],
    ))
    story.append(P("表 31. 条款与数据的对应。推荐强度、证据确定性和本地时限仍然要按上传报告第六节的方案，在双人提取和预先登记之后再写。", "caption"))

    story.append(P("十二、来源、重算和没有拿到的全文", "h2"))
    story.append(table(
        ["研究", "PMID", "本汇编使用的材料", "年龄"],
        [
            ["Garrouste-Orgeas 2009 转诊", "19866508", "摘要", "≥80"],
            ["Boumendil ICE-CUB 2012", "22509296", "PMC 全文表", "≥80"],
            ["Le Guen 2016 是否询问", "26758531", "摘要", "≥80，能表达者"],
            ["Guidet ICE-CUB2 2017", "28973065", "摘要", "≥75，功能较好"],
            ["Flaatten VIP1 2017", "28936626", "摘要", "≥80"],
            ["Guidet VIP1 限制治疗 2018", "29774388", "摘要", "≥80"],
            ["Sprung Eldicus 2012", "21926598，22001580", "摘要", "全成人，分层"],
            ["Valley 肺炎 2015", "26393850", "PMC 全文表", ">64"],
            ["Andersen 挪威转诊 2017", "27618269", "摘要", "≥80"],
            ["Philippart / Garrouste ETHICA 2013", "23765236，23765237", "摘要", "≥80"],
            ["de Lange 评分 2019", "30977911", "PMC 全文表，无赋分补充表", "≥80"],
            ["Guidet VIP2 2020", "31784798", "PMC 全文表", "≥80"],
            ["Fronczek CFS 2021", "34210358", "PMC 全文表", "≥80"],
            ["Bruno 九十岁 2021", "34666709", "PMC 全文表", "≥80"],
            ["Bruno CFS 个体数据 2023", "37133796", "PMC 全文表", "含 <65 与 ≥65"],
            ["Beil 信息论 2023", "36609257", "PMC 全文表", "≥80"],
            ["Mousai 表型 2023", "37162595", "PMC 全文表", "≥80"],
            ["Beil 跨国情景 2023", "37884827", "PMC 全文表", "情景为 87 岁"],
            ["Ouchi 急诊插管 2018", "29542117", "PMC 全文表", "≥65"],
            ["Ouchi 通气后轨迹 2020", "32540468", "PMC 全文表", "≥75"],
            ["Ouchi 谈话试验 2025", "40531532", "PMC 全文表", "平均 67 岁"],
            ["Grudzen PRIM-ER 2025", "39813042", "摘要", "≥66，中位 77"],
            ["Leahy SOLAR 2024", "39541993", "摘要", "≥75"],
            ["Sax ESI 2023", "36930151", "PMC 全文表", "成人，含 ≥80"],
            ["Ginsburg 2021", "33191046", "摘要", "≥40，含 ≥80"],
            ["Grossmann 2012 / 2014", "22401951，25153120", "摘要；2014 为 PMC 表", "≥65"],
            ["Platts-Mills 2010", "20370755", "摘要", "≥65"],
            ["Mowbray 2020", "31718719", "摘要", "≥75"],
            ["Garrouste-Orgeas 九十岁 2016", "27076186", "PMC 全文表", ">90 对 80–90"],
            ["Beil ESICM 共识 2025", "39961851", "摘要，无陈述全文", "≥80"],
            ["Guidet 轨迹综述 2024", "38236292", "摘要，非患者数据", "≥80"],
        ],
        [62 * mm, 38 * mm, 52 * mm, 28 * mm],
    ))
    story.append(P("表 32. 材料边界。PMC 全文表的逐格 CSV 在同一目录的 data/。图 1 至图 18 在 figures/。", "caption"))
    story.append(P("本汇编自己做的算术只有：ICE-CUB 各院候选数除以纳入数，Sax 各年龄低估人数除以就诊数，以及若干已经由原文同时给出人数和百分比、本汇编只是并列呈现的核对。没有拟合新的回归，没有合并敏感度，没有用上传报告里的文献计量命中数充当患者数据。", "body"))
    story.append(P("仍缺少、因而没有写入效应的内容：ESICM 48 条陈述的原文和同意比例，VIP1 按 CFS 每一分的死亡表，de Lange 补充材料中的赋分，SOLAR 护理院和功能结局的百分比，Ginsburg 的分组人数，Andersen 三个转诊组的人数，以及任何一家中国急诊的患者级数据。上传报告所规划的多中心队列仍然是这些国际数字不能代替的部分。", "body"))

    story.append(P("图注汇总", "h2"))
    notes = [
        "图 1 转诊比例。Garrouste-Orgeas 2009，摘要。",
        "图 2 医院间可入 ICU 比例。Boumendil 2012 表 1 计数相除。虚线 12.4%。",
        "图 3 收治资格与结局。Boumendil 2012 表 5。",
        "图 4 系统收治试验。Guidet 2017 摘要。",
        "图 5 拒绝与死亡的年龄梯度。Sprung 2012 摘要。",
        "图 6 三种算法的 30 天死亡。Valley 2015 表 4。",
        "图 7 转诊三分法的 1 年生存。Andersen 2017 摘要。",
        "图 8 患者拒绝生命支持的比例。Philippart 2013 摘要。",
        "图 9 VIP2 单独模型的 HR。Guidet 2020 表 6。",
        "图 10 七种表型的不开始治疗与 30 天死亡。Mousai 2023 表 1。",
        "图 11 国家间限制治疗。Mousai 2023 表 2，国家匿名。",
        "图 12 CFS 每一分的死亡。Fronczek 2021 表 1。",
        "图 13 CFS 每一分的插管与治疗限制。Fronczek 2021 表 1。",
        "图 14 九十岁与八十岁的治疗强度。Bruno 2021 表 1。",
        "图 15 急诊插管后的院内死亡。Ouchi 2018 表 1。",
        "图 16 出院后中位生存天数。Ouchi 2020 表 1。",
        "图 17 ≥65 岁 CFS 分组的 ICU 死亡 HR。Bruno 2023 表 5。",
        "图 18 各年龄低估分诊比例。Sax 2023 表 2 计数相除。",
    ]
    for n in notes:
        story.append(P(n, "small"))

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("WQY", 8)
        canvas.setFillColor(colors.HexColor(SLATE))
        canvas.drawString(16 * mm, 8 * mm, "高龄急诊治疗决策原始数据汇编  ·  检索 2026-11-18")
        canvas.drawRightString(A4[0] - 16 * mm, 8 * mm, str(doc_.page))
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return pdf_path


def main():
    setup_font()
    figs = charts()
    pdf = build(figs)
    print(pdf)
    print("figures", len(list(FIG.glob('*.png'))))
    print("csv", len(list(DATA.glob('*.csv'))))


if __name__ == "__main__":
    main()
