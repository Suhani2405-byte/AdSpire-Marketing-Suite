"""
Build the project report (DOCX + PDF) with page numbers measured from the real layout.

    python -m build_report.assemble_report          (run from the project root)

Requirements: python-docx, pymupdf, and Microsoft Word (used through COM to lay out the
document and export the PDF, so the PDF looks exactly like the DOCX opened in Word).

Steps
  1. dry run of the chapters -> list of all headings / figures / tables (H.PLAN)
  2. build the full DOCX (front matter is generated from H.PLAN)
  3. Word exports a PDF -> find the page of every heading / caption -> H.PAGE_MAP
  4. rebuild with real page numbers; repeat until the page numbers are stable
"""
import os
import re
import subprocess
import tempfile

import fitz  # pymupdf

from build_report import docx_helper as H
from build_report.docx_helper import create_styled_document, add_header_footer
from build_report.chapter_prelim import build_preliminary_pages
from build_report.chapter_1 import build_chapter_1
from build_report.chapter_2 import build_chapter_2
from build_report.chapter_3 import build_chapter_3
from build_report.chapter_4 import build_chapter_4
from build_report.chapter_5 import build_chapter_5
from build_report.chapter_6 import build_chapter_6
from build_report.chapter_7 import build_chapter_7
from build_report.chapter_8_9_refs import build_chapter_8_9_refs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DOCX = os.path.join(ROOT, "Adspire_AI_Major_Project_Report.docx")
OUT_PDF = os.path.join(ROOT, "Adspire_AI_Major_Project_Report.pdf")
CHAPTERS = [build_chapter_1, build_chapter_2, build_chapter_3, build_chapter_4, build_chapter_5,
            build_chapter_6, build_chapter_7, build_chapter_8_9_refs]


def build(path):
    H.REGISTRY.clear()
    doc = create_styled_document()
    build_preliminary_pages(doc)
    for chapter in CHAPTERS:
        chapter(doc)
    add_header_footer(doc, "Sangam University, Bhilwara", "Adspire AI – AI Marketing Campaign Generator")
    doc.save(path)


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
  $d.Close($false)
}} finally {{ $w.Quit() }}
"""
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], check=True)


def _norm(t):
    t = t.lower().replace("–", "-").replace("—", "-").replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", "", t)


def measure_pages(pdf_path):
    pages = [_norm(p.get_text()) for p in fitz.open(pdf_path)]
    page_map, cursor = {}, 0
    # body entries appear in document order; start after the front matter
    for i, txt in enumerate(pages):
        if _norm("CHAPTER 1:") in txt and "tableofcontents" not in txt:
            cursor = i
            break
    for kind, text in H.REGISTRY:
        needle = _norm(text)
        start = 0 if kind == "pre" else cursor
        for i in range(start, len(pages)):
            if needle in pages[i]:
                page_map[(kind, text)] = i + 1
                if kind != "pre":
                    cursor = i
                break
        else:
            print(f"   [warn] page not found for {kind}: {text[:60]}")
    return page_map, len(pages)


def generate_report():
    tmp = tempfile.mkdtemp(prefix="adspire_report_")
    docx_tmp, pdf_tmp = os.path.join(tmp, "report.docx"), os.path.join(tmp, "report.pdf")

    print("[1] Dry run to collect headings, figures and tables...")
    H.REGISTRY.clear()
    dry = create_styled_document()
    for chapter in CHAPTERS:
        chapter(dry)
    H.PLAN = list(H.REGISTRY)
    print(f"    {sum(k == 'h1' for k, _ in H.PLAN)} chapters, {sum(k == 'h2' for k, _ in H.PLAN)} sections, "
          f"{sum(k == 'fig' for k, _ in H.PLAN)} figures, {sum(k == 'tbl' for k, _ in H.PLAN)} tables")

    H.PAGE_MAP = {}
    for attempt in range(1, 5):
        print(f"[{attempt + 1}] Building DOCX and laying it out in Word...")
        build(docx_tmp)
        word_to_pdf(docx_tmp, pdf_tmp)
        new_map, n_pages = measure_pages(pdf_tmp)
        if new_map == H.PAGE_MAP:
            print(f"    page numbers stable ({n_pages} pages)")
            break
        H.PAGE_MAP = new_map
    else:
        print("    [warn] page numbers did not fully stabilise")

    for src, dst in ((docx_tmp, OUT_DOCX), (pdf_tmp, OUT_PDF)):
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            f_out.write(f_in.read())
    print(f"[+] Saved {OUT_DOCX}\n[+] Saved {OUT_PDF}")
    return OUT_DOCX


if __name__ == "__main__":
    generate_report()
