import os
from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_figure_image, add_styled_table,
    add_code_block, register, page_of, toc_title
)
from build_report import docx_helper as H
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_preliminary_pages(doc):
    # -------------------------------------------------------------
    # 1. COVER PAGE
    # -------------------------------------------------------------
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(12)
    p_top.paragraph_format.space_after = Pt(4)
    run_univ = p_top.add_run("SANGAM UNIVERSITY, BHILWARA, RAJASTHAN")
    run_univ.font.name = 'Times New Roman'
    run_univ.font.size = Pt(16)
    run_univ.font.bold = True
    run_univ.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(0)
    p_dept.paragraph_format.space_after = Pt(24)
    run_dept = p_dept.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\nSCHOOL OF ENGINEERING AND TECHNOLOGY")
    run_dept.font.name = 'Times New Roman'
    run_dept.font.size = Pt(12)
    run_dept.font.bold = True
    run_dept.font.color.rgb = RGBColor(0x34, 0x49, 0x5E)

    # University Logo / Project Logo placeholder
    hero_path = os.path.abspath("frontend/src/assets/hero.png")
    if os.path.exists(hero_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(8)
        p_logo.paragraph_format.space_after = Pt(14)
        run_logo = p_logo.add_run()
        run_logo.add_picture(hero_path, width=Inches(1.8))

    p_proj_title = doc.add_paragraph()
    p_proj_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj_title.paragraph_format.space_before = Pt(12)
    p_proj_title.paragraph_format.space_after = Pt(8)
    run_title = p_proj_title.add_run("ADSPIRE AI – AI MARKETING CAMPAIGN GENERATOR")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(19)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1B, 0x4F, 0x72)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(28)
    run_sub = p_sub.add_run("A Major Project Report Submitted in Partial Fulfillment of the Requirements\nfor the Award of the Degree of\nBACHELOR OF TECHNOLOGY\nin\nCOMPUTER SCIENCE AND ENGINEERING")
    run_sub.font.name = 'Times New Roman'
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

    # Submitted by & Under the Guidance of Table
    p_details = doc.add_paragraph()
    p_details.paragraph_format.space_before = Pt(24)
    p_details.paragraph_format.space_after = Pt(12)
    
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.autofit = False
    t.columns[0].width = Inches(3.2)
    t.columns[1].width = Inches(3.2)

    cell_l = t.cell(0, 0)
    p_l = cell_l.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_l.paragraph_format.line_spacing = 1.3
    r = p_l.add_run("Submitted By:\n")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r = p_l.add_run("SUHANI SHARMA\n")
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x1B, 0x4F, 0x72)
    r = p_l.add_run("Enrollment No: 2023SUBTCS065\nFinal Year B.Tech CSE\nSangam University, Bhilwara")
    r.font.size = Pt(11)

    cell_r = t.cell(0, 1)
    p_r = cell_r.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r.paragraph_format.line_spacing = 1.3
    r = p_r.add_run("Under the Guidance of:\n")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r = p_r.add_run("DR. VIKAS SOMANI\n")
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x1B, 0x4F, 0x72)
    r = p_r.add_run("Associate Professor & Head\nDepartment of CSE\nSangam University, Bhilwara")
    r.font.size = Pt(11)

    p_sess = doc.add_paragraph()
    p_sess.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sess.paragraph_format.space_before = Pt(36)
    p_sess.paragraph_format.space_after = Pt(0)
    run_sess = p_sess.add_run("ACADEMIC SESSION: 2026–2027")
    run_sess.font.name = 'Times New Roman'
    run_sess.font.size = Pt(13)
    run_sess.font.bold = True
    run_sess.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    add_page_break(doc)

    # -------------------------------------------------------------
    # 2. CERTIFICATE
    # -------------------------------------------------------------
    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert_title.paragraph_format.space_before = Pt(18)
    p_cert_title.paragraph_format.space_after = Pt(18)
    r = p_cert_title.add_run("CERTIFICATE OF APPROVAL"); register("pre", "CERTIFICATE OF APPROVAL")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    add_body_p(doc, "This is to certify that the Major Project Report entitled \"Adspire AI – AI Marketing Campaign Generator\", submitted by Suhani Sharma (Enrollment No: 2023SUBTCS065) in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology (B.Tech) in Computer Science and Engineering from Sangam University, Bhilwara (Rajasthan), is an authentic record of bonafide project work carried out under my supervision and guidance during the academic session 2026–2027.")

    add_body_p(doc, "The matter embodied in this project report has not been submitted by the candidate elsewhere for the award of any other degree, diploma, or associateship in any University or Institute. To the best of my knowledge, the work presented herein adheres to high engineering standards, software craftsmanship, and academic integrity.")

    add_body_p(doc, "The student has successfully developed, integrated, verified, and demonstrated the end-to-end multi-agent autonomous marketing campaign generation architecture, creative text-to-image synthesis pipeline, predictive ROAS simulation engine, interactive platform social mockups, and persistent relational data tier.")

    # Signatures Table
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(48)
    p_sig.paragraph_format.space_after = Pt(0)

    t_sig = doc.add_table(rows=1, cols=2)
    t_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_sig.autofit = False
    t_sig.columns[0].width = Inches(3.2)
    t_sig.columns[1].width = Inches(3.2)

    c1 = t_sig.cell(0, 0)
    p_c1 = c1.paragraphs[0]
    p_c1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_c1.paragraph_format.line_spacing = 1.3
    r = p_c1.add_run("___________________________\n")
    r.font.bold = True
    r = p_c1.add_run("Dr. Vikas Somani\n")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r = p_c1.add_run("Project Guide & Head\nDepartment of Computer Science & Engg.\nSangam University, Bhilwara")
    r.font.size = Pt(10.5)

    c2 = t_sig.cell(0, 1)
    p_c2 = c2.paragraphs[0]
    p_c2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_c2.paragraph_format.line_spacing = 1.3
    r = p_c2.add_run("___________________________\n")
    r.font.bold = True
    r = p_c2.add_run("External Examiner\n")
    r.font.bold = True
    r.font.size = Pt(11.5)
    r = p_c2.add_run("Board of Examiners\nSchool of Engineering & Technology\nSangam University, Bhilwara")
    r.font.size = Pt(10.5)

    add_page_break(doc)

    # -------------------------------------------------------------
    # 3. DECLARATION
    # -------------------------------------------------------------
    p_decl = doc.add_paragraph()
    p_decl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_decl.paragraph_format.space_before = Pt(18)
    p_decl.paragraph_format.space_after = Pt(18)
    r = p_decl.add_run("CANDIDATE'S DECLARATION"); register("pre", "CANDIDATE'S DECLARATION")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    add_body_p(doc, "I, Suhani Sharma, student of Bachelor of Technology (B.Tech) in Computer Science and Engineering, Final Year, at Sangam University, Bhilwara, hereby declare that the major project work entitled \"Adspire AI – AI Marketing Campaign Generator\" submitted to the Department of Computer Science and Engineering is an authentic record of my own original research and development carried out during the academic session 2026–2027 under the continuous supervision and academic mentorship of Dr. Vikas Somani.")

    add_body_p(doc, "I solemnly affirm that:")
    add_bullet_p(doc, "Originality:", "The implementation details, architectural designs, algorithms, user interfaces, database schemas, and experimental evaluations presented in this report are original and written by me.")
    add_bullet_p(doc, "No Plagiarism:", "Any material, theory, code library, framework, or model architecture cited or utilized from published sources, open-source repositories, or research literature has been explicitly acknowledged and duly referenced in accordance with standard academic citation practices.")
    add_bullet_p(doc, "No Prior Submission:", "This report or any substantial portion of it has not been previously submitted by me or any other individual for the award of any degree, diploma, fellowship, or certificate at this or any other higher educational university.")

    p_dec_sig = doc.add_paragraph()
    p_dec_sig.paragraph_format.space_before = Pt(40)
    p_dec_sig.paragraph_format.space_after = Pt(0)
    p_dec_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_dec_sig.paragraph_format.line_spacing = 1.3
    
    r = p_dec_sig.add_run("___________________________\n")
    r.font.bold = True
    r = p_dec_sig.add_run("Suhani Sharma\n")
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x1B, 0x4F, 0x72)
    r = p_dec_sig.add_run("Enrollment No: 2023SUBTCS065\nB.Tech (CSE), Final Year\nSangam University, Bhilwara (Raj.)\nDate: November 2026")
    r.font.size = Pt(10.5)

    add_page_break(doc)

    # -------------------------------------------------------------
    # 4. ACKNOWLEDGEMENT
    # -------------------------------------------------------------
    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack.paragraph_format.space_before = Pt(18)
    p_ack.paragraph_format.space_after = Pt(18)
    r = p_ack.add_run("ACKNOWLEDGEMENT"); register("pre", "ACKNOWLEDGEMENT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    add_body_p(doc, "The completion of this Major Project Report and the successful realization of the Adspire AI Marketing Suite has been a profound educational and technical journey. I seize this invaluable opportunity to express my heartfelt gratitude and respect to all individuals whose steadfast encouragement, technical critique, and intellectual guidance made this project possible.")

    add_body_p(doc, "First and foremost, I express my deepest sense of gratitude and indebtedness to my revered project guide, Dr. Vikas Somani, Associate Professor & Head, Department of Computer Science and Engineering, Sangam University. His profound domain knowledge in computational intelligence, meticulous architectural scrutiny, constructive technical feedback, and inspiring encouragement provided invaluable direction at every phase of development—from architectural conceptualization and prompt engineering to full-stack integration and performance verification.")

    add_body_p(doc, "I extend my sincere appreciation to the faculty members, laboratory instructors, and administrative staff of the Department of Computer Science and Engineering and the School of Engineering and Technology, Sangam University, Bhilwara, for providing an academically vibrant environment, modern computational facilities, and continuous administrative assistance throughout my undergraduate curriculum.")

    add_body_p(doc, "I also express my boundless gratitude to my family and parents, whose unconditional love, sacrifices, patience, and unwavering belief in my aspirations served as an inexhaustible pillar of moral support and strength. Finally, I thank my batchmates and friends for their engaging discussions, peer reviews, constructive feedback, and camaraderie throughout the execution of this major project.")

    p_ack_sig = doc.add_paragraph()
    p_ack_sig.paragraph_format.space_before = Pt(28)
    p_ack_sig.paragraph_format.space_after = Pt(0)
    p_ack_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_ack_sig.add_run("Suhani Sharma\n(2023SUBTCS065)")
    r.font.bold = True
    r.font.size = Pt(11.5)

    add_page_break(doc)

    # -------------------------------------------------------------
    # 5. ABSTRACT
    # -------------------------------------------------------------
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs.paragraph_format.space_before = Pt(18)
    p_abs.paragraph_format.space_after = Pt(18)
    r = p_abs.add_run("ABSTRACT"); register("pre", "ABSTRACT")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    add_body_p(doc, "Modern digital marketing demands high velocity, multi-channel agility, creative personalization, and rigorous financial optimization. However, contemporary enterprises, direct-to-consumer (D2C) brands, and digital agencies grapple with fragmented toolchains, exorbitant agency retainers, severe creative fatigue, and disconnected budgeting workflows. Traditional copy creation cycles require days of collaborative back-and-forth between copywriters, media buyers, graphic designers, and financial planners, frequently resulting in delayed time-to-market and suboptimal return on ad spend (ROAS).")

    add_body_p(doc, "To address these bottlenecks, this final-year engineering major project presents Adspire AI – an AI Marketing Campaign Generator. Adspire AI combines large-language-model copywriting, AI and real-photo product visuals, a benchmark-based ROAS budget simulator and interactive social-media ad previews in a single, secure multi-user web application.")

    add_body_p(doc, "The presentation tier is a React 19 single-page application built with Vite and split into reusable components (Campaign Studio, Visual Studio, Budget Planner, Library, Admin Panel) that share state through a React context. The service tier is a Python Flask 3 REST API organised into seven blueprints (auth, campaigns, image, budget, brands, admin, settings) with password hashing, signed bearer tokens, role-based access (marketer / administrator), per-user rate limits and administrator-controlled feature switches. Data is stored through SQLAlchemy 2 in SQLite during development and PostgreSQL in production.")

    add_body_p(doc, "Campaign intelligence is produced by Google Gemini with strict JSON output and is streamed to the browser token-by-token using Server-Sent Events, with automatic fail-over across six Gemini models when a model is overloaded. A single request yields a buyer persona, value propositions, a primary advertisement with two A/B variants and conversion hypotheses, Instagram, LinkedIn, X and TikTok content, an e-mail newsletter, a seven-day content calendar and an image prompt. For visuals, the system first lets Gemini analyse the prompt: branded products (any company) are matched with licensed real photographs from Pexels, Unsplash, Openverse and Wikimedia, while other requests are generated with FLUX.1-schnell on Cloudflare Workers AI (falling back to Gemini, Hugging Face or Pollinations), with the brand name rendered as a logo on the product. Every candidate image is checked by Gemini vision — product type, unwanted people and logo spelling — and rejected if it is wrong, so mismatched images are never displayed.")

    add_body_p(doc, "The project is verified by 33 automated backend unit tests, a 77-check live API test against the real AI services and a 32-step browser test that drives Microsoft Edge through every screen, all of which pass. Measured end-to-end, a complete multi-channel campaign is produced in roughly 25–120 seconds depending on Gemini load, compared with the days typically needed for a manual agency workflow.")

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.space_after = Pt(0)
    r_kw = p_kw.add_run("Keywords: ")
    r_kw.font.bold = True
    r_kw.font.color.rgb = RGBColor(0x1B, 0x4F, 0x72)
    r_kw_txt = p_kw.add_run("Generative AI, Large Language Models, Google Gemini, Server-Sent Events, Text-to-Image Generation, Vision-Based Verification, Multi-Channel Campaign Generation, ROAS Simulation, React.js, Python Flask, SQLAlchemy, Role-Based Access Control.")
    r_kw_txt.font.italic = True

    add_page_break(doc)

    # -------------------------------------------------------------
    # 6. TABLE OF CONTENTS
    # -------------------------------------------------------------
    p_toc = doc.add_paragraph()
    p_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc.paragraph_format.space_before = Pt(18)
    p_toc.paragraph_format.space_after = Pt(18)
    r = p_toc.add_run("TABLE OF CONTENTS"); register("pre", "TABLE OF CONTENTS")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    plan = H.PLAN
    toc_items = [("Preliminary Pages", "")]
    pre_names = {"CERTIFICATE OF APPROVAL": "Certificate of Approval", "CANDIDATE'S DECLARATION": "Candidate's Declaration",
                 "ACKNOWLEDGEMENT": "Acknowledgement", "ABSTRACT": "Abstract", "TABLE OF CONTENTS": "Table of Contents",
                 "LIST OF FIGURES": "List of Figures", "LIST OF TABLES": "List of Tables"}
    for title, label in pre_names.items():
        toc_items.append(("  " + label, page_of("pre", title)))
    for kind, text in plan:
        if kind == "h1":
            toc_items.append((toc_title(text), page_of("h1", text)))
        elif kind == "h2":
            toc_items.append(("  " + text, page_of("h2", text)))

    t_toc = doc.add_table(rows=len(toc_items), cols=2)
    t_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_toc.autofit = False
    t_toc.columns[0].width = Inches(5.4)
    t_toc.columns[1].width = Inches(1.0)

    for i, (item, page) in enumerate(toc_items):
        r_c0 = t_toc.cell(i, 0).paragraphs[0]
        r_c0.paragraph_format.space_before = Pt(2)
        r_c0.paragraph_format.space_after = Pt(2)
        run_i = r_c0.add_run(item)
        run_i.font.name = 'Times New Roman'
        run_i.font.size = Pt(10.5)
        if not item.startswith("  "):
            run_i.font.bold = True
            run_i.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

        r_c1 = t_toc.cell(i, 1).paragraphs[0]
        r_c1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_c1.paragraph_format.space_before = Pt(2)
        r_c1.paragraph_format.space_after = Pt(2)
        run_p = r_c1.add_run(page)
        run_p.font.name = 'Times New Roman'
        run_p.font.size = Pt(10.5)
        if not item.startswith("  "):
            run_p.font.bold = True

    add_page_break(doc)

    # -------------------------------------------------------------
    # 7. LIST OF FIGURES
    # -------------------------------------------------------------
    p_lof = doc.add_paragraph()
    p_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof.paragraph_format.space_before = Pt(18)
    p_lof.paragraph_format.space_after = Pt(18)
    r = p_lof.add_run("LIST OF FIGURES"); register("pre", "LIST OF FIGURES")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    def _split(caption):
        num, _, desc = caption.partition(":")
        return num.strip(), desc.strip()

    figures = [(*_split(text), page_of("fig", text)) for kind, text in plan if kind == "fig"]

    t_lof = doc.add_table(rows=len(figures), cols=3)
    t_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_lof.autofit = False
    t_lof.columns[0].width = Inches(1.2)
    t_lof.columns[1].width = Inches(4.4)
    t_lof.columns[2].width = Inches(0.8)

    for i, (fig_no, fig_desc, page_no) in enumerate(figures):
        c0 = t_lof.cell(i, 0).paragraphs[0]
        c0.paragraph_format.space_before = Pt(3)
        c0.paragraph_format.space_after = Pt(3)
        r0 = c0.add_run(fig_no)
        r0.font.bold = True
        r0.font.size = Pt(10.5)

        c1 = t_lof.cell(i, 1).paragraphs[0]
        c1.paragraph_format.space_before = Pt(3)
        c1.paragraph_format.space_after = Pt(3)
        r1 = c1.add_run(fig_desc)
        r1.font.size = Pt(10.5)

        c2 = t_lof.cell(i, 2).paragraphs[0]
        c2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        c2.paragraph_format.space_before = Pt(3)
        c2.paragraph_format.space_after = Pt(3)
        r2 = c2.add_run(page_no)
        r2.font.size = Pt(10.5)

    add_page_break(doc)

    # -------------------------------------------------------------
    # 8. LIST OF TABLES
    # -------------------------------------------------------------
    p_lot = doc.add_paragraph()
    p_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot.paragraph_format.space_before = Pt(18)
    p_lot.paragraph_format.space_after = Pt(18)
    r = p_lot.add_run("LIST OF TABLES"); register("pre", "LIST OF TABLES")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x29, 0x4A)

    tables = [(*_split(text), page_of("tbl", text)) for kind, text in plan if kind == "tbl"]

    t_lot = doc.add_table(rows=len(tables), cols=3)
    t_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_lot.autofit = False
    t_lot.columns[0].width = Inches(1.2)
    t_lot.columns[1].width = Inches(4.4)
    t_lot.columns[2].width = Inches(0.8)

    for i, (tbl_no, tbl_desc, page_no) in enumerate(tables):
        c0 = t_lot.cell(i, 0).paragraphs[0]
        c0.paragraph_format.space_before = Pt(3)
        c0.paragraph_format.space_after = Pt(3)
        r0 = c0.add_run(tbl_no)
        r0.font.bold = True
        r0.font.size = Pt(10.5)

        c1 = t_lot.cell(i, 1).paragraphs[0]
        c1.paragraph_format.space_before = Pt(3)
        c1.paragraph_format.space_after = Pt(3)
        r1 = c1.add_run(tbl_desc)
        r1.font.size = Pt(10.5)

        c2 = t_lot.cell(i, 2).paragraphs[0]
        c2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        c2.paragraph_format.space_before = Pt(3)
        c2.paragraph_format.space_after = Pt(3)
        r2 = c2.add_run(page_no)
        r2.font.size = Pt(10.5)

    add_page_break(doc)
