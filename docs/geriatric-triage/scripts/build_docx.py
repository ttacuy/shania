#!/usr/bin/env python3
"""Build a WPS-openable .docx from the lecture markdown."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "讲义.md"
OUT = ROOT / "高龄患者急诊预检讲义.docx"
FIG = ROOT / "figures"

BODY = "宋体"
HEAD = "黑体"
INK = RGBColor(0x1F, 0x29, 0x33)
MUTED = RGBColor(0x52, 0x60, 0x6D)


def set_run_font(run, name, size, bold=False, color=None):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = name
    run.font.color.rgb = color or INK
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    fonts.set(qn("w:ascii"), name)
    fonts.set(qn("w:hAnsi"), name)
    fonts.set(qn("w:eastAsia"), name)
    fonts.set(qn("w:cs"), name)


def shade_cell(cell, hex_color):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")


def set_cell_border(cell):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_borders = tc_pr.find(qn("w:tcBorders"))
    if tc_borders is None:
        tc_borders = OxmlElement("w:tcBorders")
        tc_pr.append(tc_borders)
    for edge in ("top", "left", "bottom", "right"):
        element = tc_borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            tc_borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), "D0D7DE")


def add_page_number(paragraph):
    run = paragraph.add_run()
    set_run_font(run, BODY, 9, color=MUTED)

    def fld(kind):
        char = OxmlElement("w:fldChar")
        char.set(qn("w:fldCharType"), kind)
        run._r.append(char)

    fld("begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    run._r.append(instr)
    fld("end")


def add_inline(paragraph, text, size=12, base_bold=False):
    pattern = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`)")
    pos = 0
    for match in pattern.finditer(text):
        if match.start() > pos:
            run = paragraph.add_run(text[pos:match.start()])
            set_run_font(run, BODY, size, bold=base_bold)
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_run_font(run, BODY, size, bold=True)
        else:
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, BODY, size - 1, color=MUTED)
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        set_run_font(run, BODY, size, bold=base_bold)


def add_picture(document, name):
    path = FIG / name
    if not path.exists():
        paragraph = document.add_paragraph()
        add_inline(paragraph, f"缺少图片：{name}", size=10)
        return
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(8)
    run = paragraph.add_run()
    run.add_picture(str(path), width=Cm(15.5))


def add_table(document, rows):
    if not rows:
        return
    width = max(len(row) for row in rows)
    table = document.add_table(rows=len(rows), cols=width)
    table.autofit = True
    for r_index, row in enumerate(rows):
        for c_index in range(width):
            cell = table.rows[r_index].cells[c_index]
            text = row[c_index] if c_index < len(row) else ""
            cell.text = ""
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            add_inline(paragraph, text.strip(), size=10, base_bold=(r_index == 0))
            set_cell_border(cell)
            if r_index == 0:
                shade_cell(cell, "E8EEF4")
    document.add_paragraph().paragraph_format.space_after = Pt(4)


def split_row(line):
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return [part.strip() for part in raw.split("|")]


def is_separator(line):
    return bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line))


def build():
    document = Document()
    section = document.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(1.9)
    section.right_margin = Cm(1.9)
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)
    section.header_distance = Cm(0.6)
    section.footer_distance = Cm(0.6)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("高龄患者急诊预检讲义  ·  WPS 文字")
    set_run_font(run, BODY, 9, color=MUTED)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number(footer)

    normal = document.styles["Normal"]
    normal.font.name = BODY
    normal.font.size = Pt(12)
    normal.font.color.rgb = INK
    rpr = normal.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    fonts.set(qn("w:ascii"), BODY)
    fonts.set(qn("w:hAnsi"), BODY)
    fonts.set(qn("w:eastAsia"), BODY)

    lines = SRC.read_text(encoding="utf-8").splitlines()
    i = 0
    first_heading = True
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("# "):
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.space_after = Pt(8)
            run = paragraph.add_run(stripped[2:].strip())
            set_run_font(run, HEAD, 22, bold=True)
            i += 1
            continue

        if stripped.startswith("## "):
            if not first_heading:
                document.add_page_break()
            first_heading = False
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(8)
            run = paragraph.add_run(stripped[3:].strip())
            set_run_font(run, HEAD, 16, bold=True)
            i += 1
            continue

        if stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not is_separator(lines[i]):
                    rows.append(split_row(lines[i]))
                i += 1
            add_table(document, rows)
            continue

        images = re.findall(r"figures/([\w.-]+\.png)", stripped)
        if images and stripped.startswith("图"):
            for name in images:
                add_picture(document, name)
            i += 1
            continue

        if re.match(r"^[-*] ", stripped):
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.left_indent = Cm(0.75)
            paragraph.paragraph_format.first_line_indent = Cm(-0.4)
            paragraph.paragraph_format.space_after = Pt(3)
            paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            paragraph.paragraph_format.line_spacing = 1.15
            add_inline(paragraph, "·  " + stripped[2:].strip())
            i += 1
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered:
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.left_indent = Cm(0.75)
            paragraph.paragraph_format.first_line_indent = Cm(-0.45)
            paragraph.paragraph_format.space_after = Pt(3)
            paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            paragraph.paragraph_format.line_spacing = 1.15
            add_inline(paragraph, f"{numbered.group(1)}.  {numbered.group(2)}")
            i += 1
            continue

        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(6)
        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        paragraph.paragraph_format.line_spacing = 1.2
        paragraph.paragraph_format.first_line_indent = Cm(0.74)
        add_inline(paragraph, stripped)
        i += 1

    document.core_properties.title = "高龄患者急诊预检讲义"
    document.core_properties.subject = "WPS 文字可直接打开的文献讲义"
    document.core_properties.category = "讲义"
    document.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
