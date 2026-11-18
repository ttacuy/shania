#!/usr/bin/env python3
"""White-background briefing on elderly emergency triage and treatment."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures" / "ppt"
OUT = ROOT / "高龄急诊预检与综合救治.pptx"

INK = RGBColor(0x1A, 0x1A, 0x1A)
SECONDARY = RGBColor(0x3C, 0x40, 0x43)
BLUE = RGBColor(0x0B, 0x57, 0xD0)
LINE = RGBColor(0xDA, 0xDC, 0xE0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
NAVY = "#0B57D0"
TEAL = "#1F6B64"
CLAY = "#A15C38"
RED = "#8C3A3A"
SLATE = "#5F6368"

W = Inches(13.333)
H = Inches(7.5)


def setup_mpl():
    plt.rcParams["font.sans-serif"] = ["WenQuanYi Micro Hei"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["savefig.facecolor"] = "white"


def style_ax(ax, title, xlabel, ylabel):
    ax.set_title(title, loc="left", fontsize=13, color="#1A1A1A", pad=8)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=SLATE)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=SLATE)
    ax.tick_params(colors="#1A1A1A", labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#E0E3E6")
    ax.spines["bottom"].set_color("#E0E3E6")
    ax.grid(axis="y", color="#F1F3F4", zorder=0)


def save_fig(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / name
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def charts():
    setup_mpl()
    paths = {}

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    labels = ["0–15岁", "16–59岁", "60岁及以上"]
    values = [17.1, 60.9, 22.0]
    colors = ["#5F6368", "#1F6B64", NAVY]
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.62, zorder=2)
    for bar, v in zip(bars, values[::-1]):
        ax.text(v + 0.8, bar.get_y() + bar.get_height() / 2, f"{v:.1f}%", va="center", fontsize=11, color="#1A1A1A")
    ax.set_xlim(0, 78)
    style_ax(ax, "2024年末全国人口年龄构成", "占全国人口的比重（%）", "")
    paths["age"] = save_fig(fig, "age_structure.png")

    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    cats = ["2022年目标\n设立老年医学科", "2025年目标\n设立老年医学科", "2027年末目标\n规范设置老年医学科"]
    vals = [50, 60, 80]
    ax.bar(cats, vals, color=[TEAL, NAVY, CLAY], width=0.62, zorder=2)
    for i, v in enumerate(vals):
        ax.text(i, v + 1.5, f"{v}%", ha="center", fontsize=12, color="#1A1A1A")
    ax.set_ylim(0, 100)
    style_ax(ax, "综合医院老年医学科目标是逐步加严的", "", "目标比例（%）")
    paths["targets"] = save_fig(fig, "geriatrics_targets.png")

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ages = ["18–29", "30–39", "40–49", "50–59", "60–69", "70–79", "≥80"]
    rates = [3.29, 3.09, 3.17, 3.42, 3.67, 3.54, 3.01]
    colors = [NAVY if a != "≥80" else CLAY for a in ages]
    ax.bar(ages, rates, color=colors, zorder=2)
    ax.set_ylim(0, 5)
    style_ax(ax, "ESI第4版：各年龄低估分诊比例", "年龄（岁）", "低估分诊（%）")
    paths["sax"] = save_fig(fig, "sax_undertriage.png")

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    names = ["住院 OR", "入 ICU OR", "30天死亡 HR"]
    est = [1.97, 1.23, 2.47]
    lo = [1.75, 0.99, 1.81]
    hi = [2.21, 1.52, 3.37]
    y = np.arange(len(names))
    ax.errorbar(est, y, xerr=[np.array(est) - lo, np.array(hi) - est], fmt="o", color=NAVY, capsize=4, ms=7)
    ax.axvline(1, color=SLATE, lw=0.8)
    ax.set_yticks(y, names)
    ax.set_xlim(0.6, 3.6)
    style_ax(ax, "同一ESI、同一类主诉后，≥80岁相对40–64岁", "效应值（OR 或 HR，不能互相换算）", "")
    paths["ginsburg"] = save_fig(fig, "ginsburg_effects.png")

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    cfs = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    ax.plot(cfs, [28.5, 33.6, 33.4, 37.7, 37.9, 45.5, 55.6, 60.6, 81.4], marker="o", color=RED, label="30天死亡")
    ax.plot(cfs, [51.7, 55.7, 51.4, 50.6, 46.5, 48.9, 48.9, 64.6, 58.1], marker="o", color=NAVY, label="气管插管")
    style_ax(ax, "VIP1+VIP2：7,487名≥80岁患者", "临床衰弱量表 CFS", "比例（%）")
    ax.legend(frameon=False, fontsize=9)
    ax.set_ylim(0, 100)
    paths["cfs"] = save_fig(fig, "cfs_death_intubation.png")

    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    x = np.arange(2)
    ax.bar(x - 0.18, [61, 45], 0.36, label="系统推荐入ICU", color=CLAY, zorder=2)
    ax.bar(x + 0.18, [34, 39], 0.36, label="常规做法", color=NAVY, zorder=2)
    ax.set_xticks(x, ["入 ICU", "6个月死亡"])
    ax.set_ylim(0, 80)
    style_ax(ax, "ICE-CUB2：提高收治没有降低6个月死亡", "≥75岁、功能较好、无癌症、无恶病质", "比例（%）")
    ax.legend(frameon=False, fontsize=9)
    paths["icecub2"] = save_fig(fig, "icecub2.png")

    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    metrics = ["衰弱", "插管", "肾脏替代", "限制治疗", "30天死亡", "ICU死亡"]
    x = np.arange(len(metrics))
    ax.bar(x - 0.18, [58, 41, 4, 40, 44, 27], 0.36, label="≥90岁 n=790", color=CLAY, zorder=2)
    ax.bar(x + 0.18, [42, 52, 12, 33, 40, 27], 0.36, label="80–89岁 n=7110", color=NAVY, zorder=2)
    ax.set_xticks(x, metrics)
    style_ax(ax, "已经入ICU的九十岁与八十岁", "指标", "比例（%）")
    ax.legend(frameon=False, fontsize=9)
    ax.set_ylim(0, 80)
    paths["nona"] = save_fig(fig, "nonagenarian.png")
    return paths


def set_run(run, size, bold=False, color=INK, font="微软雅黑"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set("typeface", font)


def add_text(slide, text, x, y, w, h, size=16, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    try:
        tf._txBody.bodyPr.set("anchor", {MSO_ANCHOR.TOP: "t", MSO_ANCHOR.MIDDLE: "ctr", MSO_ANCHOR.BOTTOM: "b"}[anchor])
    except Exception:
        pass
    lines = str(text).split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(0)
        p.space_before = Pt(0)
        run = p.add_run()
        run.text = line
        set_run(run, size, bold, color)
    return box


def rect(slide, x, y, w, h, fill=WHITE, line=LINE):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = Pt(1)
    # no shadow
    spPr = shape._element.spPr
    effect = spPr.find(qn("a:effectLst"))
    if effect is not None:
        spPr.remove(effect)
    return shape


def footer(slide, page, total):
    add_text(slide, "高龄急诊预检与综合救治", 0.5, 7.16, 8.2, 0.24, 11, color=SECONDARY)
    add_text(slide, f"{page} / {total}", 10.6, 7.16, 2.2, 0.24, 11, color=SECONDARY, align=PP_ALIGN.RIGHT)


def new_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = WHITE
    return slide


def header(slide, title, subtitle=None):
    rect(slide, 0.5, 0.36, 0.08, 0.42 if not subtitle else 0.72, fill=BLUE, line=BLUE)
    add_text(slide, title, 0.72, 0.28, 12.1, 0.46, 26, bold=True)
    if subtitle:
        add_text(slide, subtitle, 0.72, 0.74, 12.1, 0.32, 14, color=SECONDARY)


def card(slide, x, y, w, h, label, value, note):
    rect(slide, x, y, w, h)
    add_text(slide, label, x + 0.16, y + 0.12, w - 0.32, 0.32, 12, color=SECONDARY)
    add_text(slide, value, x + 0.16, y + 0.42, w - 0.32, 0.48, 22, bold=True, color=BLUE)
    add_text(slide, note, x + 0.16, y + 0.96, w - 0.32, 0.55, 12, color=INK)


def bullets(slide, items, x, y, w, h, size=15):
    add_text(slide, "\n".join(items), x, y, w, h, size)


def build(paths):
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    prs.slides._sldIdLst.clear()
    # blank layout exists on default template
    total = 16

    # 1 cover
    s = new_slide(prs)
    rect(s, 0.5, 1.55, 0.1, 1.55, fill=BLUE, line=BLUE)
    add_text(s, "高龄急诊预检与综合救治", 0.8, 1.45, 11.5, 0.7, 36, bold=True)
    add_text(s, "老年患者现状、国家要求、与年轻患者的差别、\n规范分诊、高危识别和综合救治细节", 0.8, 2.3, 11.2, 0.9, 20, color=SECONDARY)
    add_text(s, "纯白底数据简报。人口与政策用国家统计局、国家卫生健康委公开文件。\n急诊决策数字用已核对的原始研究，检索日 2026年11月18日（北京时间）。", 0.8, 3.5, 11.2, 0.8, 15)
    add_text(s, "核心人群是急诊 ≥80 岁。国家文件里的 60 岁、65 岁界线单独保留，不并进同一个分母。", 0.8, 4.5, 11.2, 0.5, 15, color=SECONDARY)
    footer(s, 1, total)

    # 2 status
    s = new_slide(prs)
    header(s, "老年患者现状：人口已经越过 3 亿", "国家统计局《2024年国民经济和社会发展统计公报》；2024年度国家老龄事业发展公报")
    card(s, 0.5, 1.28, 3.0, 1.62, "60周岁及以上", "3.1031 亿", "占总人口 22.0%")
    card(s, 3.66, 1.28, 3.0, 1.62, "65周岁及以上", "2.2023 亿", "占总人口 15.6%")
    card(s, 6.82, 1.28, 3.0, 1.62, "老年抚养比", "22.8%", "分母是15–64岁人口")
    card(s, 9.98, 1.28, 2.85, 1.62, "人均预期寿命", "79.0 岁", "2024年度老龄事业公报")
    s.shapes.add_picture(str(paths["age"]), Inches(0.5), Inches(3.12), Inches(7.6), Inches(3.75))
    add_text(s, "三组互不重叠。\n0–15岁：2.3999亿，占17.1%。\n16–59岁：8.5798亿，占60.9%。\n60岁及以上：3.1031亿，占22.0%。\n65岁及以上包含在上一组内。\n0–15岁含不满16周岁。\n\n范围是大陆31个省、自治区、直辖市和现役军人，不含港澳台居民和外籍人员。", 8.25, 3.2, 4.55, 3.6, 14)
    footer(s, 2, total)

    # 3 health burden and supply
    s = new_slide(prs)
    header(s, "健康负担与服务供给不在同一个年份", "2018年口径来自卫健委老龄健康司发布会；2024年口径来自老龄事业发展公报")
    rows = [
        ("2018年底", "60岁及以上 2.5亿。人均预期寿命 77.0岁，健康预期寿命 68.7岁，带病生存约8年。"),
        ("慢性病与失能", "一种以上慢性病的比例 75%，患病人数接近1.9亿。失能和部分失能超过4000万。"),
        ("2024年服务量", "基层医疗卫生机构接受健康服务的65岁及以上老年人 1.41亿。每年一次健康管理。"),
        ("学科与友善机构", "二级及以上公立综合医院设老年医学科 6000余个。2020年底这一数字是2642个。"),
        ("友善与安宁", "老年友善综合医院 15624个，基层机构 39138个。安宁疗护推开到185个市（区）。"),
        ("人才", "2024年老年医学和安宁疗护培训 7500余名。国家老年医学中心1个，临床医学研究中心6个。"),
    ]
    y = 1.22
    for i, (k, v) in enumerate(rows):
        rect(s, 0.5, y, 12.33, 0.88)
        add_text(s, k, 0.68, y + 0.22, 2.3, 0.44, 15, bold=True, color=BLUE)
        add_text(s, v, 3.05, y + 0.16, 9.5, 0.58, 15)
        y += 0.96
    footer(s, 3, total)

    # 4 conference and guidance
    s = new_slide(prs)
    header(s, "全国卫生与健康大会怎样进入老年诊疗文件", "大会精神以《指导意见》及其政策解读的正式转述为准，不另写未核对的讲话原文")
    steps = [
        ("2016", "全国卫生与健康大会", "政策解读写明：把人民健康放在优先发展的战略地位，提供全生命周期服务，为老年人提供连续的健康管理和医疗服务。"),
        ("2016", "健康中国2030", "为老年人提供治疗期住院、康复期护理、稳定期生活照料、安宁疗护一体化的健康和养老服务。"),
        ("2019", "国卫老龄发〔2019〕61号", "八部门《关于建立完善老年健康服务体系的指导意见》。正文写明深入贯彻落实全国卫生与健康大会精神。"),
        ("2021", "国卫老龄发〔2021〕45号", "《关于全面加强老年健康服务工作的通知》。从以疾病为中心转向以健康为中心，按内在能力提供精准服务。"),
        ("2022", "十四五健康老龄化规划", "到2025年综合连续、覆盖城乡的老年健康服务体系基本建立，健康预期寿命不断延长。"),
        ("2024–2025", "能力与科室指南", "国卫办医政发〔2024〕19号，以及《老年医学科建设与管理指南（2025年版）》。"),
    ]
    y = 1.2
    for year, name, text in steps:
        add_text(s, year, 0.5, y, 1.35, 0.7, 14, bold=True, color=BLUE)
        add_text(s, name, 1.9, y, 3.3, 0.7, 14, bold=True)
        add_text(s, text, 5.3, y, 7.5, 0.78, 13)
        y += 0.92
    footer(s, 4, total)

    # 5 six links and targets
    s = new_slide(prs)
    header(s, "指导意见要求的六段连续服务", "国卫老龄发〔2019〕61号。诊治从单病种改为以患者为中心的多病共治。")
    links = ["健康教育", "预防保健", "疾病诊治", "康复护理", "长期照护", "安宁疗护"]
    for i, name in enumerate(links):
        x = 0.5 + i * 2.12
        rect(s, x, 1.22, 2.0, 0.85)
        add_text(s, f"{i+1}", x + 0.12, 1.32, 0.4, 0.55, 18, bold=True, color=BLUE, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, name, x + 0.48, 1.38, 1.4, 0.5, 15, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    s.shapes.add_picture(str(paths["targets"]), Inches(0.4), Inches(2.25), Inches(7.3), Inches(4.55))
    notes = [
        "2022年三项量化：老年医学科比例50%；80%以上综合医院、康复医院、护理院和基层机构成为老年友善机构；基层护理床位占比30%。",
        "2025年：设立老年医学科的比例达到60%以上；65岁及以上城乡社区规范健康管理服务率65%以上。",
        "2027年末：二级以上综合医院规范设置老年医学科的比例力争80%。“设立”和“规范设置”不是同一个口径。",
        "安宁疗护按充分知情、自愿选择。生命终末期同时提供症状控制和心理支持。",
    ]
    add_text(s, "\n\n".join(notes), 7.7, 2.35, 5.1, 4.4, 14)
    footer(s, 5, total)

    # 6 emergency national requirements
    s = new_slide(prs)
    header(s, "国家对老年应急救援的要求写在多份文件里", "救护车半径和出车时限是全体人群的院前标准，同样约束老年急救。文件没有把高龄写成降低抢救优先级的条款。")
    items = [
        ("院前体系", "国卫医发〔2020〕19号。到2025年覆盖城乡。城市服务半径不超过5公里，农村10–20公里。每3万人口1辆救护车。120在10秒内接听、3分钟出车的比例都要达到95%。危急重症现场监护或抢救措施实施率98%。调度原则是就近、就急、就专科。"),
        ("院前接入院内", "落实首诊负责制，规范交接，建立院前院内一体化绿色通道。与胸痛、卒中、创伤、危重孕产妇、危重新生儿中心衔接。急危重症优先救治、后补手续。"),
        ("不得因费用停救", "疾病应急救助制度：身份不明确或无力支付，也必须及时施救，不得拒绝、推诿或拖延。"),
        ("老年就医与风险", "老年友善机构设人工挂号和收费窗口、绿色通道。住院老年人筛查跌倒、肺栓塞、误吸、坠床，并有预案和告知。门急诊配备轮椅、平车。"),
        ("医养与家庭", "签约医疗机构为入住老年人开通急诊急救绿色通道。病情危重及时转送。面向居家失能照护者开展应急救护培训。探索紧急救助呼叫。老年人集中场所推动安装AED。"),
        ("老年医学科", "2025年版指南要求具备急诊科等科室和气管插管、除颤等抢救设备。三级医院加强老年危急重症。畅通上下转诊绿色通道。"),
    ]
    y = 1.18
    for title, text in items:
        add_text(s, title, 0.5, y, 1.7, 0.85, 13, bold=True, color=BLUE)
        add_text(s, text, 2.25, y, 10.55, 0.88, 13)
        y += 0.95
    footer(s, 6, total)

    # 7 difference vs young
    s = new_slide(prs)
    header(s, "急诊需求与年轻患者的差别", "差别在残余风险、表现和治疗目标，不是“高龄一定被低估”")
    s.shapes.add_picture(str(paths["sax"]), Inches(0.3), Inches(1.15), Inches(7.05), Inches(3.15))
    s.shapes.add_picture(str(paths["ginsburg"]), Inches(0.3), Inches(4.4), Inches(7.05), Inches(2.55))
    diffs = [
        "Sax等，21家美国急诊、531万次成人就诊。≥80岁低估 19140/635021 = 3.01%，校正RR 0.66（0.65–0.68），对照18–29岁。定义含事后资源使用。",
        "Ginsburg等，五类主诉并校正ESI。≥80岁住院OR 1.97（1.75–2.21），30天死亡HR 2.47（1.81–3.37）。入ICU的OR 1.23（0.99–1.52）含1。",
        "表现更常不典型：乏力、跌倒、进食减少、意识或活动能力改变。生命体征解释和呼吸频率容易被漏掉。",
        "多病、多药、储备低。同一次就诊要同时处理急症和基线功能，不能只用一个疾病诊断结束。",
        "年轻患者的成功多是活着离院。高龄还要问90天能否自理、住哪里、怎样的恢复可以接受。",
    ]
    add_text(s, "\n\n".join(diffs), 7.55, 1.2, 5.3, 5.7, 13)
    footer(s, 7, total)

    # 8 frailty vs acuity
    s = new_slide(prs)
    header(s, "急迫等级和衰弱几乎不相关", "Mowbray等，加拿大8家急诊，2009–2012年，≥75岁 2153人")
    blocks = [
        ("r = 0.001", "CTAS与急诊衰弱指数", "p = 0.99。数据采集早于2016年CTAS衰弱修正，不能当成该修正已经生效的证据。"),
        ("OR 6", "CTAS 2 相对 CTAS 5 的住院", "95%CI 3.3–11.4。传统急迫等级仍然预测住院。"),
        ("OR 1.5", "衰弱指数每增加 0.1 的住院", "95%CI 1.4–1.6。再住院 OR 1.1，再次急诊 OR 1.1。"),
        ("两套信息", "不能互相代替", "急迫决定这一小时救不救。衰弱决定储备、照护和后续功能。"),
    ]
    for i, (v, t, n) in enumerate(blocks):
        x = 0.5 + (i % 2) * 6.4
        y = 1.3 + (i // 2) * 2.7
        rect(s, x, y, 6.15, 2.45)
        add_text(s, v, x + 0.25, y + 0.25, 5.6, 0.6, 28, bold=True, color=BLUE)
        add_text(s, t, x + 0.25, y + 0.95, 5.6, 0.4, 16, bold=True)
        add_text(s, n, x + 0.25, y + 1.45, 5.6, 0.75, 14)
    footer(s, 8, total)

    # 9 how to triage
    s = new_slide(prs)
    header(s, "如何规范急诊预检", "在现有ESI、CTAS或本地分级上增加信息和动作，不另造一套替代抢救的分数")
    steps = [
        ("1", "先开抢救通道", "时间敏感疾病和需要立即救命的患者先进入既定通道。衰弱、认知和治疗目标并行采集，不作为抢救的前置条件。"),
        ("2", "记全第一分钟能得到的急性信息", "主诉、意识、氧疗、完整生命体征，包括呼吸频率。保留数值、测量时间和氧支持。"),
        ("3", "把基线与本次疾病分开", "病前约两周的CFS、ADL、认知、合并症、高危药物、居住和近期功能。这次病到不能走，不能直接写成长期衰弱。"),
        ("4", "高危情境由临床复核", "非特异主诉、新发功能下降、急性认知改变、近期反复就诊、抗凝或镇静药。取不到的信息记为未知，不记为正常。"),
        ("5", "候诊中复评", "症状变化、生命体征恶化、等待超过本级时限、护士或家属担忧。写下新等级、原因、时间和责任人。"),
        ("6", "阳性必须有人接", "写明接收团队、响应责任、监护场所和完成记录。没有老年团队时，由在岗急诊团队完成最低评估并安排转介。"),
    ]
    for i, (n, t, body) in enumerate(steps):
        x = 0.45 + (i % 3) * 4.25
        y = 1.22 + (i // 3) * 2.85
        rect(s, x, y, 4.08, 2.65)
        add_text(s, n, x + 0.18, y + 0.15, 0.5, 0.45, 22, bold=True, color=BLUE)
        add_text(s, t, x + 0.7, y + 0.2, 3.15, 0.45, 16, bold=True)
        add_text(s, body, x + 0.18, y + 0.8, 3.7, 1.65, 13)
    footer(s, 9, total)

    # 10 identify high risk
    s = new_slide(prs)
    header(s, "识别高危：用哪一个结局，决定了谁算漏诊", "救命干预、住院、30天死亡和功能下降不是同一个真值")
    s.shapes.add_picture(str(paths["cfs"]), Inches(0.25), Inches(1.15), Inches(7.2), Inches(5.15))
    facts = [
        "Platts-Mills：≥65岁782人中，26人接受即时救命干预。ESI=1的敏感度42.3%（23.3–61.3%）。这26人里，1级11人、2级9人、3级6人。2级已经是高优先级。",
        "Grossmann：专家复核的低估，教学前22.5%（117/519），一年后24.1%（95/394），p=0.619。主因是高危情境和危险区生命体征，不是年龄本身。",
        "CFS 4与CFS 5的30天死亡是37.7%和37.9%。CFS 7是55.6%，仍有44%在30天内存活。插管比例没有随衰弱下降。",
        "高危用于加快复核、监测和老年团队响应。年龄、CFS、认知或居住机构单独不能降低急迫等级，也不能推定治疗无效。",
    ]
    add_text(s, "\n\n".join(facts), 7.6, 1.2, 5.25, 4.0, 13)
    add_text(s, "来源：Platts-Mills 2010；Grossmann 2014；Fronczek 2021，VIP1+VIP2。CFS 8、9只有246和43人，比例不稳定。", 0.5, 6.55, 12.3, 0.45, 12, color=SECONDARY)
    footer(s, 10, total)

    # 11 principles
    s = new_slide(prs)
    header(s, "综合救治原则", "急迫、脆弱、变化和患者目标要接上，不能互相替代")
    principles = [
        ("先处理可逆的急症", "呼吸、循环、时间敏感疾病按现有路径。器官支持的决定和谈话同时进行，不把问卷插在抢救前面。"),
        ("四套信息各管一件事", "急迫性决定优先级。病前CFS和ADL决定储备与照护。复评抓住候诊中的变化。治疗目标决定做到哪一步。"),
        ("多病共治", "国家文件要求从单病种转向多病共治，做老年综合评估，处理衰弱、谵妄、误吸、跌倒、用药。急诊先抓会改变今日处置的几项。"),
        ("共同决策是连续的", "先确认决策能力、已有计划和适当代理人。需要ICU时，由急诊、重症，必要时老年和姑息共同评估获益与负担。"),
        ("不确定就做有复评点的治疗", "写下目标、可观察的改善、负责人、复评时间和达不到目标时的选项。评分不能自动生成治疗限制。"),
        ("去向匹配能力", "ICU、有监护能力的病房、老年急性照护、安宁支持按当时需求匹配。中间病房不能用来安置本应收进ICU的患者。姑息可与病因治疗并行。"),
    ]
    for i, (t, b) in enumerate(principles):
        x = 0.45 + (i % 3) * 4.25
        y = 1.22 + (i // 3) * 2.85
        rect(s, x, y, 4.08, 2.65)
        add_text(s, t, x + 0.18, y + 0.16, 3.7, 0.7, 16, bold=True)
        add_text(s, b, x + 0.18, y + 0.95, 3.7, 1.5, 13)
    footer(s, 11, total)

    # 12 details dataset
    s = new_slide(prs)
    header(s, "救治细节：到院时最少要留下的字段", "缺记录不等于没有。家属不在场不等于拒绝治疗。")
    headers = ["数据", "字段", "注意"]
    rows = [
        ["时间", "到院、分诊、首诊、转出", "用来发现延误和重复就诊"],
        ["急性状态", "主诉、生命体征、意识、氧疗、危急信号", "同时记下测量时间和给氧条件"],
        ["基线", "病前CFS、ADL、认知、居住、近期功能", "参考发病前约两周，并写信息来源"],
        ["用药与合并症", "抗凝、镇静，近30天住院", "没有记录就标未知"],
        ["治疗目标", "决策能力、代理人、已有计划、患者重视的结局", "随病情更新，不一次写死"],
        ["处置", "关键干预、再分诊、去向、治疗限制的时点", "限制决定要分清发生在治疗之前还是之后"],
    ]
    xs = [0.5, 2.3, 7.3]
    ws = [1.7, 4.9, 5.0]
    rect(s, 0.5, 1.22, 12.33, 0.48, fill=BLUE, line=BLUE)
    for x, w, hname in zip(xs, ws, headers):
        add_text(s, hname, x + 0.08, 1.3, w - 0.1, 0.34, 14, bold=True, color=WHITE)
    y = 1.7
    for a, b, c in rows:
        rect(s, 0.5, y, 12.33, 0.78)
        add_text(s, a, xs[0] + 0.08, y + 0.18, ws[0] - 0.1, 0.45, 14, bold=True, color=BLUE)
        add_text(s, b, xs[1] + 0.08, y + 0.18, ws[1] - 0.12, 0.45, 14)
        add_text(s, c, xs[2] + 0.08, y + 0.18, ws[2] - 0.15, 0.45, 14)
        y += 0.78
    footer(s, 12, total)

    # 13 what the trials say
    s = new_slide(prs)
    header(s, "收治策略的原始结果", "观察性的“收与不收”和随机试验不是同一个结论")
    s.shapes.add_picture(str(paths["icecub2"]), Inches(0.25), Inches(1.12), Inches(6.75), Inches(3.15))
    s.shapes.add_picture(str(paths["nona"]), Inches(0.25), Inches(4.35), Inches(6.75), Inches(2.6))
    text = (
        "ICE-CUB2，法国24家医院集群随机，3036人，中位年龄85岁。系统收治使入ICU从34%到61%（RR 1.80，1.66–1.95）。未校正6个月死亡45%对39%（RR 1.16，1.07–1.26）。校正后RR 1.05（0.96–1.14）。功能没有显著差别。\n\n"
        "ICE-CUB观察队列：15家医院把≥80岁判为可入ICU的比例从5.6%到38.8%，6个月死亡两组都是50.7%。能表达的患者里，决定前被询问的只有12.7%。\n\n"
        "≥90岁与80–89岁的ICU死亡都是27%。九十岁以上插管更少（41%对52%），肾脏替代更少（4%对12%）。校正后30天死亡aOR 1.25（0.90–1.74）。"
    )
    add_text(s, text, 7.15, 1.2, 5.7, 5.6, 13)
    footer(s, 13, total)

    # 14 time limited and preferences
    s = new_slide(prs)
    header(s, "限时治疗和患者偏好要写具体", "专家情景里没有统一的天数；患者拒绝的比例随治疗加深而上升")
    prefs = [
        ("27%", "拒绝无创通气"),
        ("43%", "拒绝有创通气"),
        ("63%", "拒绝通气后的肾脏替代"),
        ("12.7%", "能表达意见者被询问"),
    ]
    for i, (v, t) in enumerate(prefs):
        x = 0.5 + i * 3.2
        rect(s, x, 1.22, 3.02, 1.45)
        add_text(s, v, x + 0.15, 1.32, 2.7, 0.55, 26, bold=True, color=BLUE)
        add_text(s, t, x + 0.15, 1.95, 2.7, 0.5, 14)
    details = [
        "限时试验先写四件事：这次治疗要改善什么，用哪个可观察指标判断，谁在什么时间复评，达不到时下一步是继续、调整还是转向舒适。",
        "十个国家或地区的重症医师面对同一名87岁、CFS 4的患者，都描述了治疗试验，触发点却分别是急性肾损伤、卒中、血管活性药或“没有相应反应”。不能把某一篇文章里的两天或五天写成全院时限。",
        "VIP2中死亡日的中位数是第7天（四分位第3–14天）。这是已入ICU队列的死亡时间，不是试验应当设定的天数。",
        "上方前三项来自ETHICA，平均84.8岁，n=115。得知患者不同意后，医师模拟决定被改动的比例为39.9%、56%和57%。12.7%是另一项研究：2115名能表达意见的患者中，决定前被询问270人。",
        "撤除治疗与死亡强烈伴随（VIP2中有治疗限制者死亡HR 4.25）。这是决定和临终发生在一起，不能读成“限制治疗造成4倍死亡”。",
    ]
    add_text(s, "\n\n".join(details), 0.5, 2.85, 12.3, 4.1, 14)
    footer(s, 14, total)

    # 15 quality
    s = new_slide(prs)
    header(s, "用哪些指标看预检有没有做对", "两个容易混用的比例，分母不一样")
    metrics = [
        ("基线CFS覆盖", "完成且有时间、来源的就诊", "符合评估条件的高龄就诊。未完成原因单列。"),
        ("谵妄筛查覆盖", "完成规定工具的就诊", "复苏中暂缓的单列，不记入未筛。"),
        ("阳性后行动", "按时完成复核或干预", "分母是需要行动的阳性就诊，同时报告等待时间。"),
        ("危重被放在低优先级", "低优先级且出现预设关键结局", "分母是所有出现该结局的人，等于1减敏感度。"),
        ("低优先级里的事件", "低优先级且出现同一结局", "分母是所有低优先级就诊。与上一行不是同一个率。"),
        ("决策记录与功能随访", "写明目标、参与者、理由、复评", "90天ADL和居住地。死亡单列，不只分析幸存者。"),
    ]
    y = 1.2
    for i, (a, b, c) in enumerate(metrics):
        col = i % 2
        row = i // 2
        x = 0.5 + col * 6.4
        yy = y + row * 1.85
        rect(s, x, yy, 6.15, 1.7)
        add_text(s, a, x + 0.2, yy + 0.12, 5.75, 0.38, 16, bold=True)
        add_text(s, b, x + 0.2, yy + 0.55, 5.75, 0.35, 14, color=BLUE)
        add_text(s, c, x + 0.2, yy + 0.98, 5.75, 0.55, 13)
    footer(s, 15, total)

    # 16 boundaries and sources
    s = new_slide(prs)
    header(s, "使用这些数字时的边界", "国际原始研究说明决策结构。它们还不是中国急诊的外部验证。")
    lines = [
        "人口和政策是中国官方口径。急诊收治、分诊敏感度和CFS曲线来自法国、欧洲多国、美国和加拿大研究，年龄界线各不相同。",
        "ICE-CUB2排除了功能很差、恶病质和癌症。它不能外推成“所有≥80岁都不应入ICU”，也不能外推成“都应入ICU”。",
        "死亡预测高，不等于这次治疗无效。CFS高分不能单独成为拒绝抢救或拒绝ICU的理由。",
        "ESICM 2025年48条共识陈述的原文和逐条同意比例，本次没有取得全文，幻灯片不编造推荐措辞。",
        "SOLAR证明老年综合评估可以缩短符合条件患者的急诊停留，效应估计是3.1小时，不是两个中位数相减的8.5小时，而且排除了需要复苏的患者。",
        "下一步仍是上传报告里的方案：统一≥80岁最小数据集，先静默验证，再看漏识别、工作量、治疗一致性和90天功能。",
    ]
    y = 1.2
    for i, line in enumerate(lines, 1):
        add_text(s, f"{i}", 0.5, y, 0.4, 0.75, 16, bold=True, color=BLUE)
        add_text(s, line, 1.0, y, 11.8, 0.8, 14)
        y += 0.9
    footer(s, 16, total)

    # remove unused default if any leftover - we cleared sldIdLst before adding
    prs.save(OUT)
    return OUT


def main():
    paths = charts()
    out = build(paths)
    print(out)


if __name__ == "__main__":
    main()
