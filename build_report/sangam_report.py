"""
Build the Adspire AI report in the Sangam University report format.

    python -m build_report.sangam_report  TEMPLATE.docx      (run from the project root)

TEMPLATE.docx is a *copy* of an existing Sangam University report (cover page, certificate,
acknowledgement, contents, list of figures, abstract, chapters).  The copy is opened read-only
from disk; its cover / certificate / acknowledgement / header / footer / styles are kept, the
names and texts are replaced, and every chapter paragraph is created by cloning the template's
own paragraph formats (chapter heading, section heading, body text, bullet, figure, caption,
table, reference).  The original template file is never written.

Page numbers in the contents and list of figures are measured from the real layout: Word
exports a PDF, the page of every heading / caption is found, and the document is rebuilt until
the numbers are stable.
"""
import copy
import os
import re
import subprocess
import sys
import tempfile

import fitz  # pymupdf
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches
from PIL import Image

from build_report import docx_helper as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DOCX = os.path.join(ROOT, "Adspire_AI_Major_Project_Report.docx")
OUT_PDF = os.path.join(ROOT, "Adspire_AI_Major_Project_Report.pdf")

TITLE = "Adspire AI: AI-Powered Marketing Campaign and Ad Visual Generator"
SHORT_TITLE = "Adspire AI: AI Marketing Campaign Generator"
STUDENT, ROLL = "Suhani Sharma", "2023SUBTCS065"
OLD_TITLE = "DocuMind: AI Document Intelligence using Hybrid Retrieval-Augmented Generation"
OLD_SHORT = "DocuMind: AI Document Intelligence using Hybrid RAG"

ABSTRACT = [
    "The project titled “" + TITLE + "” presents a web application that turns a short product brief into a complete digital marketing campaign. Preparing a campaign normally needs a strategist, a copywriter, a designer and a media planner, and free AI tools used on their own produce disconnected text and images that often do not show the product at all.",
    "Adspire AI uses Google Gemini to write a buyer persona, value propositions, an advertisement with A/B variants, posts for four social networks, a video script, an e-mail newsletter and a seven-day calendar, streamed to the browser with automatic fail-over across six models. Product visuals come from licensed real photographs or from FLUX image generation with the brand name on the product, and every image is checked by Gemini vision, so a picture that does not match the prompt is never shown.",
    "The system is built with Flask and React and adds a budget and ROAS planner, advertisement mock-ups, a campaign library and an administration panel. It is verified by 33 unit tests, a 77-check live API test and a 32-step browser test, all of which pass.",
]

TEXT_WIDTH_IN = 6.27
MAX_FIG_H_IN = 7.9

# ----------------------------------------------------------------------------- state
S = {}            # current document + prototypes
PLAN = []         # (kind, key, label) collected while building, kind in ch / h2 / h3 / fig / end
FIG_MAP, TAB_MAP = {}, {}   # old "4.1" -> new number (from the dry run)
PAGES = {}        # (kind, key) -> page number (from the measured PDF)


def _strip_runs(p_el):
    for child in list(p_el):
        if child.tag != qn("w:pPr"):
            p_el.remove(child)
    return p_el


def _run(rpr, text):
    r = parse_xml(f"<w:r {nsdecls('w')}/>")
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = parse_xml(f"<w:t {nsdecls('w')} xml:space=\"preserve\"/>")
    t.text = text
    r.append(t)
    return r


def _proto(name):
    p = copy.deepcopy(S["proto"][name]["p"])
    return _strip_runs(p)


def _rpr(name, i=0):
    rprs = S["proto"][name]["rpr"]
    return rprs[min(i, len(rprs) - 1)]


def _append(el):
    S["sect"].addprevious(el)
    return el


def _para(name, segments):
    """segments: list of (rpr_index, text)."""
    p = _proto(name)
    for idx, text in segments:
        p.append(_run(_rpr(name, idx), text))
    return _append(p)


def _fix_refs(text):
    def sub(m):
        word, nums = m.group(1), m.group(2)
        table = TAB_MAP if word.startswith("Table") else FIG_MAP
        return word + " " + re.sub(r"\d+\.\d+", lambda n: str(table.get(n.group(0), n.group(0))), nums)
    return re.sub(r"\b(Figures?|Tables?) (\d+\.\d+(?:\s*(?:,|and|–|-|to)\s*\d+\.\d+)*)", sub, text)


# ----------------------------------------------------------------------------- shim API
def add_page_break(doc):
    pass  # chapters start on a new page automatically, as in the template


def add_heading_1(doc, text):
    _para("pagebrk", [])
    text = text.strip()
    if text.upper().startswith("CHAPTER"):
        _para("chap", [(0, text)])
        PLAN.append(("ch", text, text))
    else:
        _para("end", [(0, text)])
        PLAN.append(("end", text, text))


def add_heading_2(doc, text):
    _para("h2", [(0, text)])
    PLAN.append(("h2", text, text))


def add_heading_3(doc, text):
    _para("h3", [(0, text)])
    PLAN.append(("h3", text, text))


def add_body_p(doc, text):
    _para("body", [(0, _fix_refs(text))])


def add_bullet_p(doc, bold_prefix, text):
    prefix = re.sub(r"^\d+\.\s+", "", bold_prefix.strip())
    _para("bullet", [(0, prefix), (1, " " + _fix_refs(text.strip()))])


def add_reference(doc, text):
    _para("ref", [(0, text)])


def add_figure_image(doc, img_path, caption_text, width_inches=6.0):
    m = re.match(r"Figure\s+(\d+\.\d+)\s*:\s*(.*)", caption_text)
    old, label = (m.group(1), m.group(2)) if m else (None, caption_text)
    n = sum(1 for k, *_ in PLAN if k == "fig") + 1
    if old:
        FIG_MAP.setdefault(old, n)
    w_px, h_px = Image.open(img_path).size
    width = min(width_inches, TEXT_WIDTH_IN)
    if width * h_px / w_px > MAX_FIG_H_IN:
        width = MAX_FIG_H_IN * w_px / h_px
    p = _proto("img")
    _append(p)
    from docx.text.paragraph import Paragraph
    Paragraph(p, S["doc"]._body).add_run().add_picture(img_path, width=Inches(width))
    _para("cap", [(0, f"Fig {n}: "), (1, label)])
    PLAN.append(("fig", f"Fig {n}: {label}", label))


def add_table_caption(doc, caption_text):
    m = re.match(r"Table\s+(\d+\.\d+)\s*:\s*(.*)", caption_text)
    n = S.setdefault("tables", 0) + 1
    S["tables"] = n
    if m:
        TAB_MAP.setdefault(m.group(1), n)
    label = m.group(2) if m else caption_text
    p = _para("cap", [(0, f"Table {n}: "), (1, label)])
    ppr = p.find(qn("w:pPr"))
    ppr.insert(0, parse_xml(f"<w:keepNext {nsdecls('w')}/>"))
    sp = parse_xml(f"<w:spacing {nsdecls('w')} w:before=\"120\" w:after=\"60\"/>")
    old = ppr.find(qn("w:spacing"))
    if old is not None:
        ppr.remove(old)
    ppr.insert(1, sp)


def _cell_xml(width, text, header, center, sz):
    shade = '<w:shd w:val="clear" w:color="auto" w:fill="E7EBF1"/>' if header else ""
    jc = '<w:jc w:val="center"/>' if (header or center) else ""
    b = "<w:b/><w:bCs/>" if header else ""
    tc = parse_xml(
        f'<w:tc {nsdecls("w")}><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shade}<w:vAlign w:val="center"/></w:tcPr>'
        f'<w:p><w:pPr><w:spacing w:before="40" w:after="40" w:line="259" w:lineRule="auto"/><w:ind w:left="0" w:firstLine="0"/>{jc}</w:pPr>'
        f'<w:r><w:rPr>{b}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr><w:t xml:space="preserve"></w:t></w:r></w:p></w:tc>')
    tc.find(".//" + qn("w:t")).text = text
    return tc


def add_styled_table(doc, headers, rows, col_widths=None):
    ncol = len(headers)
    col_widths = col_widths or [1] * ncol
    total = 9072
    widths = [int(total * w / sum(col_widths)) for w in col_widths]
    sz = 24 if ncol <= 3 else (22 if ncol == 4 else 20)
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    tbl = parse_xml(
        f'<w:tbl {nsdecls("w")}><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="{total}" w:type="dxa"/>'
        f'<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
        f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid></w:tbl>')
    for r_i, row in enumerate([headers] + list(rows)):
        tr = parse_xml(f'<w:tr {nsdecls("w")}/>')
        if r_i == 0:
            tr.append(parse_xml(f'<w:trPr {nsdecls("w")}><w:tblHeader/><w:cantSplit/></w:trPr>'))
        else:
            tr.append(parse_xml(f'<w:trPr {nsdecls("w")}><w:cantSplit/></w:trPr>'))
        for c_i, val in enumerate(row):
            short = len(str(val)) <= 14
            tr.append(_cell_xml(widths[c_i], _fix_refs(str(val)), r_i == 0, short and c_i > 0, sz))
        tbl.append(tr)
    _append(tbl)
    _para("gap", [])


def add_code_block(doc, code_str):
    lines = code_str.rstrip("\n").split("\n")
    tbl = parse_xml(
        f'<w:tbl {nsdecls("w")}><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="9072" w:type="dxa"/>'
        f'<w:tblLook w:val="04A0"/></w:tblPr><w:tblGrid><w:gridCol w:w="9072"/></w:tblGrid></w:tbl>')
    tr = parse_xml(f'<w:tr {nsdecls("w")}><w:trPr><w:cantSplit/></w:trPr></w:tr>')
    tc = parse_xml(f'<w:tc {nsdecls("w")}><w:tcPr><w:tcW w:w="9072" w:type="dxa"/>'
                   f'<w:shd w:val="clear" w:color="auto" w:fill="F4F6F8"/></w:tcPr></w:tc>')
    for line in lines:
        p = parse_xml(
            f'<w:p {nsdecls("w")}><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
            f'<w:ind w:left="60" w:firstLine="0"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
            f'<w:sz w:val="17"/><w:szCs w:val="17"/></w:rPr><w:t xml:space="preserve"></w:t></w:r></w:p>')
        p.find(".//" + qn("w:t")).text = line
        tc.append(p)
    tr.append(tc)
    tbl.append(tr)
    _append(tbl)
    _para("gap", [])


SHIM = dict(add_page_break=add_page_break, add_heading_1=add_heading_1, add_heading_2=add_heading_2,
            add_heading_3=add_heading_3, add_body_p=add_body_p, add_bullet_p=add_bullet_p,
            add_figure_image=add_figure_image, add_table_caption=add_table_caption,
            add_styled_table=add_styled_table, add_code_block=add_code_block, add_reference=add_reference)
for _k, _v in SHIM.items():
    setattr(H, _k, _v)

# chapters import the helpers by name, so they are imported only after the shim is installed
from build_report.chapter_1_intro import build_chapter_1      # noqa: E402
from build_report.chapter_2 import build_chapter_2            # noqa: E402
from build_report.chapter_3 import build_chapter_3            # noqa: E402
from build_report.chapter_4 import build_chapter_4            # noqa: E402
from build_report.chapter_5 import build_chapter_5            # noqa: E402
from build_report.chapter_6 import build_chapter_6            # noqa: E402
from build_report.chapter_7 import build_chapter_7            # noqa: E402
from build_report.chapter_8_close import build_chapter_8_close  # noqa: E402

CHAPTERS = [build_chapter_1, build_chapter_2, build_chapter_3, build_chapter_4, build_chapter_5,
            build_chapter_6, build_chapter_7, build_chapter_8_close]


# ----------------------------------------------------------------------------- template handling
def _set_runs(p, text, keep=0):
    """Put `text` into run `keep` of paragraph p and empty the other runs (formatting kept)."""
    runs = p.runs
    for i, r in enumerate(runs):
        r.text = text if i == keep else ""


def _roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out, n = out + s, n - v
    return out


def _page(kind, key, default="–"):
    v = PAGES.get((kind, key))
    return str(v) if v else default


def load_template(path):
    doc = Document(path)
    P = doc.paragraphs
    find = lambda pred: next(i for i, p in enumerate(P) if pred(p))
    i_ch1 = find(lambda p: p.text.strip().startswith("CHAPTER 1:") and p.style.name == "Heading 1")
    i_conc = find(lambda p: p.text.strip() == "CONCLUSION" and p.style.name == "Heading 1")
    i_ref1 = find(lambda p: p.text.startswith("[1] "))
    i_bullet = find(lambda p: p.text.startswith("FR1 "))
    i_h3 = find(lambda p: re.match(r"2\.2\.1 ", p.text) is not None)
    i_cap = find(lambda p: p.text.startswith("Fig 1:"))
    proto_idx = dict(chap=i_ch1, h2=i_ch1 + 1, body=i_ch1 + 2, bullet=i_bullet, h3=i_h3,
                     img=i_cap - 1, cap=i_cap, end=i_conc, ref=i_ref1, pagebrk=i_ch1 - 1)
    proto = {}
    for name, i in proto_idx.items():
        p_el = P[i]._p
        proto[name] = {"p": copy.deepcopy(p_el),
                       "rpr": [copy.deepcopy(r.find(qn("w:rPr"))) for r in p_el.findall(qn("w:r"))] or [None]}
    # an empty spacer paragraph after tables
    proto["gap"] = {"p": parse_xml(f'<w:p {nsdecls("w")}><w:pPr><w:spacing w:after="60" w:line="240" w:lineRule="auto"/>'
                                   f'<w:ind w:left="0" w:firstLine="0"/></w:pPr></w:p>'), "rpr": [None]}
    assert "pageBreakBefore" in P[i_ch1 - 1]._p.xml, "template layout changed"

    body = doc.element.body
    sect = body.find(qn("w:sectPr"))
    start = list(body).index(P[i_ch1 - 1]._p)
    for el in list(body)[start:]:
        if el is not sect:
            body.remove(el)
    S.clear()
    S.update(doc=doc, proto=proto, sect=sect, tables=0)
    return doc


def fill_front_matter(doc):
    P = doc.paragraphs
    def find(pred, start=0):
        return next(p for p in P[start:] if pred(p))

    _set_runs(P[0], TITLE)
    for p in P[:30]:
        if p.text.strip().endswith("(2023SUBTCS044)") and "certified" not in p.text:
            _set_runs(p, f"{STUDENT} ({ROLL}) ")
            break
    cert = find(lambda p: p.text.startswith("This is certified"))
    for r in cert.runs:
        if OLD_TITLE in r.text or r.text.startswith("DocuMind"):
            r.text = TITLE
    names = [r for r in cert.runs if r.font.bold and ("Raghav" in r.text or "Jagetia" in r.text or "2023SUBTCS044" in r.text)]
    for i, r in enumerate(names):
        r.text = [STUDENT, "", f" ({ROLL})"][i] if i < 3 else ""
    sig = find(lambda p: p.text.strip() == "Raghav Jagetia" or p.text.replace(" ", "") == "RaghavJagetia")
    _set_runs(sig, f"  {STUDENT}")
    roll = find(lambda p: p.text.strip() == "(2023SUBTCS044)")
    _set_runs(roll, f"   ({ROLL}) ")

    # header text in every header part
    for part in doc.part.package.parts:
        if part.partname.endswith(".xml") and "/header" in part.partname:
            el = part.element if hasattr(part, "element") else None
            if el is None:
                continue
            for t in el.iter(qn("w:t")):
                if t.text and OLD_SHORT in t.text:
                    t.text = t.text.replace(OLD_SHORT, SHORT_TITLE)

    # abstract
    i_abs = next(i for i, p in enumerate(P) if p.text.strip() == "ABSTRACT")
    abs_paras = [p for p in P[i_abs + 1:] if p.text.strip()][:3]
    for p, text in zip(abs_paras, ABSTRACT):
        _set_runs(p, text)


def fill_contents(doc):
    P = doc.paragraphs
    i_top = next(i for i, p in enumerate(P) if p.text.strip().startswith("Topics"))
    i_ch = next(i for i, p in enumerate(P) if i > i_top and p.text.strip().startswith("CHAPTER 1:"))
    i_end = next(i for i, p in enumerate(P) if i > i_ch and p.text.strip().startswith("REFERENCES"))
    # front-matter rows: Certificate i, Acknowledgement ii, Contents iii, List of Figures, Abstract
    pre = {"Certificate": "i", "Acknowledgement": "ii", "Table of Contents": "iii",
           "List of Figures": _roman(max(PAGES.get(("pre", "LIST OF FIGURES"), 9) - 1, 1)),
           "ABSTRACT": _roman(max(PAGES.get(("pre", "ABSTRACT"), 10) - 1, 1))}
    for p in P[i_top + 1:i_ch]:
        key = p.text.split("\t")[0].strip()
        if key in pre and p.runs:
            p.runs[-1].text = pre[key]

    proto_ch = copy.deepcopy(P[i_ch]._p)
    proto_sec = copy.deepcopy(P[i_ch + 1]._p)
    proto_end = copy.deepcopy(P[i_end]._p)
    rpr_ch = copy.deepcopy(proto_ch.find(".//" + qn("w:rPr")))
    sec_runs = proto_sec.findall(qn("w:r"))
    rpr_bold = copy.deepcopy(sec_runs[0].find(qn("w:rPr")))
    rpr_plain = copy.deepcopy(sec_runs[1].find(qn("w:rPr")))
    end_runs = proto_end.findall(qn("w:r"))
    rpr_end_b = copy.deepcopy(end_runs[0].find(qn("w:rPr")))
    rpr_end_p = copy.deepcopy(end_runs[1].find(qn("w:rPr")))
    anchor = P[i_end]._p.getnext()
    for p in P[i_ch:i_end + 1]:
        p._p.getparent().remove(p._p)

    def tab_run(rpr):
        r = parse_xml(f"<w:r {nsdecls('w')}/>")
        r.append(copy.deepcopy(rpr))
        r.append(parse_xml(f"<w:tab {nsdecls('w')}/>"))
        return r

    def br_run(rpr):
        r = parse_xml(f"<w:r {nsdecls('w')}/>")
        r.append(copy.deepcopy(rpr))
        r.append(parse_xml(f"<w:br {nsdecls('w')}/>"))
        return r

    groups = []
    for kind, key, label in PLAN:
        if kind == "ch":
            groups.append([key, []])
        elif kind in ("h2", "h3") and groups:
            groups[-1][1].append((kind, key))
    for title, items in groups:
        p = _strip_runs(copy.deepcopy(proto_ch))
        p.append(_run(rpr_ch, title))
        anchor.addprevious(p)
        if not items:
            continue
        p = _strip_runs(copy.deepcopy(proto_sec))
        for j, (kind, key) in enumerate(items):
            if j:
                p.append(br_run(rpr_plain))
            p.append(_run(rpr_bold, ("      " if kind == "h3" else "") + key))
            p.append(tab_run(rpr_plain))
            p.append(_run(rpr_bold, _page(kind, key)))
        anchor.addprevious(p)
    for kind, key, label in PLAN:
        if kind == "end":
            p = _strip_runs(copy.deepcopy(proto_end))
            p.append(_run(rpr_end_b, key))
            p.append(tab_run(rpr_end_p))
            p.append(_run(rpr_end_b, _page("end", key)))
            anchor.addprevious(p)


def fill_figure_list(doc):
    tbl = doc.tables[0]
    rows = tbl._tbl.findall(qn("w:tr"))
    proto = copy.deepcopy(rows[1])
    for r in rows[1:]:
        tbl._tbl.remove(r)
    for kind, key, label in PLAN:
        if kind != "fig":
            continue
        n = re.match(r"Fig (\d+):", key).group(1)
        tr = copy.deepcopy(proto)
        cells = tr.findall(qn("w:tc"))
        p0, p1 = cells[0].find(qn("w:p")), cells[1].find(qn("w:p"))
        r0 = p0.findall(qn("w:r"))
        rpr_b, rpr_n = copy.deepcopy(r0[0].find(qn("w:rPr"))), copy.deepcopy(r0[-1].find(qn("w:rPr")))
        rpr_pg = copy.deepcopy(p1.find(qn("w:r")).find(qn("w:rPr")))
        _strip_runs(p0); _strip_runs(p1)
        p0.append(_run(rpr_b, f"Figure {n}: "))
        p0.append(_run(rpr_n, label))
        p1.append(_run(rpr_pg, _page("fig", key)))
        tbl._tbl.append(tr)


def drop_unused_images(doc):
    """Remove image relationships of the template's old figures that are no longer referenced."""
    part = doc.part
    xml = part.element.xml
    used = set(re.findall(r'r:(?:embed|id|link)="([^"]+)"', xml))
    for rid, rel in list(part.rels.items()):
        if rel.reltype.endswith("/image") and rid not in used:
            del part.rels[rid]


def build(template, out_path):
    PLAN.clear()
    doc = load_template(template)
    for chapter in CHAPTERS:
        chapter(doc)
    fill_front_matter(doc)
    fill_contents(doc)
    fill_figure_list(doc)
    drop_unused_images(doc)
    doc.save(out_path)
    return doc


# ----------------------------------------------------------------------------- layout measurement
def word_to_pdf(docx_path, pdf_path):
    ps = f"""
$ErrorActionPreference = 'Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {{
  $d = $w.Documents.Open('{docx_path}', $false, $true)
  $d.Fields.Update() | Out-Null
  $d.ExportAsFixedFormat('{pdf_path}', 17)
  try {{ $d.Close(0) }} catch {{ }}
}} finally {{ try {{ $w.Quit() }} catch {{ }} }}
"""
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], check=False)
    if not os.path.exists(pdf_path):
        raise RuntimeError("Word did not export the PDF")


def _norm(t):
    t = t.lower().replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", "", t)


def measure(pdf_path):
    pages = [_norm(p.get_text()) for p in fitz.open(pdf_path)]
    found = {}
    for i, t in enumerate(pages):
        if "figurespageno." in t and ("pre", "LIST OF FIGURES") not in found:
            found[("pre", "LIST OF FIGURES")] = i + 1
        if "abstract" in t[:80] and "theprojecttitled" in t and ("pre", "ABSTRACT") not in found:
            found[("pre", "ABSTRACT")] = i + 1
    cursor = found.get(("pre", "ABSTRACT"), 8)
    for kind, key, label in PLAN:
        needle = _norm(key if kind != "fig" else key)[:70]
        for i in range(cursor, len(pages)):
            if needle in pages[i]:
                found[(kind, key)] = i + 1
                cursor = i
                break
        else:
            print(f"   [warn] not found: {kind} {key[:60]}")
    return found, len(pages)


def main():
    template = sys.argv[1]
    if os.path.abspath(template).lower() in {os.path.abspath(OUT_DOCX).lower()}:
        sys.exit("refusing to use the output file as template")
    tmp = tempfile.mkdtemp(prefix="adspire_sangam_")
    d_tmp, p_tmp = os.path.join(tmp, "report.docx"), os.path.join(tmp, "report.pdf")

    print("[1] dry run (figure / table numbering)...")
    FIG_MAP.clear(); TAB_MAP.clear()
    build(template, d_tmp)
    print(f"    {sum(k == 'ch' for k, *_ in PLAN)} chapters, {sum(k == 'h2' for k, *_ in PLAN)} sections, "
          f"{sum(k == 'fig' for k, *_ in PLAN)} figures, {S['tables']} tables")
    PAGES.clear()
    n_pages = 0
    for attempt in range(1, 5):
        print(f"[{attempt + 1}] build + Word layout...")
        build(template, d_tmp)
        word_to_pdf(d_tmp, p_tmp)
        found, n_pages = measure(p_tmp)
        if found == PAGES:
            break
        PAGES.clear(); PAGES.update(found)
    print(f"    {n_pages} pages")
    for src, dst in ((d_tmp, OUT_DOCX), (p_tmp, OUT_PDF)):
        with open(src, "rb") as fi, open(dst, "wb") as fo:
            fo.write(fi.read())
    print("saved", OUT_DOCX, "and", OUT_PDF)


if __name__ == "__main__":
    main()
