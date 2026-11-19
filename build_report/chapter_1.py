from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_figure_image, add_styled_table
)

def build_chapter_1(doc):
    add_heading_1(doc, "CHAPTER 1: INTRODUCTION")

    add_heading_2(doc, "1.1 Introduction to the Project")
    add_body_p(doc, "In the modern digital economy, marketing and advertising have evolved from static broadcast communications into dynamic, hyper-personalized, and multi-channel conversations. Businesses ranging from nascent startups to multinational enterprises must maintain an omni-present digital footprint across diverse social ecosystems, search engines, and communication channels. To successfully engage contemporary digital consumers, marketing teams are obligated to generate persuasive copywriting tailored to distinct buyer personas, conceptualize high-converting visual assets, design structured email nurture sequences, formulate tactical social calendar distributions, and optimize marketing budget allocations across fragmented advertising networks.")

    add_body_p(doc, "However, executing this multi-dimensional workflow consistently requires substantial human capital, cross-functional collaboration, and financial investment. Traditional marketing campaign development involves copywriters, digital marketing strategists, graphic designers, media buyers, and financial analysts working in siloed environments. This conventional model results in extensive turnaround times, high agency retainers, and severe creative fatigue. Furthermore, small and medium enterprises (SMEs) and independent entrepreneurs frequently lack the financial resources and technical expertise required to operate enterprise-grade marketing technology stacks.")

    add_body_p(doc, "To resolve these challenges, this Major Project introduces \"Adspire AI – AI Marketing Campaign Generator\". Adspire AI is an autonomous, full-stack marketing intelligence platform designed to democratize high-converting campaign formulation. By unifying cutting-edge generative artificial intelligence (Google Gemini Large Language Models), advanced commercial text-to-image synthesis (FLUX.1-schnell and Pollinations AI), empirical financial return-on-ad-spend (ROAS) simulation algorithms, and live interactive social mockups into a cohesive single-page application (SPA), Adspire AI compresses weeks of campaign ideation and asset production into sub-four-second computational pipelines.")

    add_heading_2(doc, "1.2 Background and Industry Context")
    add_body_p(doc, "The global digital advertising expenditure surpassed $600 billion in recent years and continues to expand rapidly. Channels such as Instagram, TikTok, LinkedIn, Google Search, Facebook, and direct email newsletters constitute the primary battleground for customer acquisition. Each of these platforms operates under distinct algorithmic rules, formatting requirements, user psychology, and engagement dynamics:")
    
    add_bullet_p(doc, "Instagram & Facebook (Meta Ecosystem):", "Relies heavily on aesthetic visual storytelling, aspirational tone, lifestyle alignment, short-form copy with emotional hooks, and strategic hashtag taxonomy.")
    add_bullet_p(doc, "LinkedIn:", "Demands professional authority, B2B thought leadership, industry data perspectives, professional problem-solution frameworks, and value-oriented takeaways.")
    add_bullet_p(doc, "TikTok & Short-Form Video:", "Operates on rapid visual hooks within the initial 3 seconds, authentic spoken dialogue, high-energy pacing, viral sound archetypes, and immediate calls-to-action (CTAs).")
    add_bullet_p(doc, "Google Search (SERP):", "Functions on high intent, concise headline relevance, keyword density, sitelink breadcrumbs, and direct commercial utility.")
    add_bullet_p(doc, "Email Marketing:", "Requires high open-rate subject lines, engaging inbox preview snippets, personalized problem narratives, and focused conversion buttons.")

    add_body_p(doc, "Historically, digital marketers relied on point-solution tools—such as separate copywriting assistants, stock photography subscriptions, manual spreadsheet budget calculators, and static graphic mockups. The advent of foundation Large Language Models (LLMs) and latent diffusion models has created a paradigm shift, enabling software systems to autonomously understand complex market propositions, synthesize persuasive multi-platform deliverables, and forecast financial metrics simultaneously.")

    add_heading_2(doc, "1.3 Problem Statement")
    add_body_p(doc, "Despite rapid advances in generative software, existing marketing solutions remain fragmented, costly, and disjointed. Specifically, digital businesses confront four critical operational bottlenecks:")

    add_bullet_p(doc, "Fragmented Toolchains & High Costs:", "Marketing practitioners are forced to context-switch across multiple expensive SaaS platforms (e.g., dedicated AI copywriters, separate graphic design suites, spreadsheet calculators, and mockup renderers), costing thousands of dollars monthly in subscription fees.")
    add_bullet_p(doc, "Lack of Strategic Cohesion:", "Generating ad text with one tool, visuals with another, and distribution plans manually leads to disjointed brand messaging, inconsistent tone, and misaligned value propositions across channels.")
    add_bullet_p(doc, "Disconnected Financial & ROAS Planning:", "Creative content generation is rarely synchronized with empirical media budget allocation. Marketers frequently create ad copy without visibility into expected Cost Per Click (CPC), Click-Through Rates (CTR), and projected Return on Ad Spend (ROAS).")
    add_bullet_p(doc, "Absence of Contextual Visual Verification:", "Marketers struggle to evaluate how generated copy and creative assets will visually appear in real-world platform feeds (e.g., mobile Instagram card with like/bookmark buttons, 9:16 vertical TikTok player, or Google SERP snippet) prior to launching live ad spend.")

    add_heading_2(doc, "1.4 Motivation")
    add_body_p(doc, "The motivation behind Adspire AI stems from the realization that computational intelligence can bridge the gap between creative ideation and financial execution. By engineering an end-to-end autonomous suite, digital businesses, growth marketers, and engineering teams can achieve true creative velocity. Enabling an autonomous agent to digest a simple product brief and instantaneously output target personas, multi-angle A/B ad copy, channel-specific social posts, viral short-form video scripts, 7-day distribution calendars, 8K commercial product photography, and predictive multi-channel budget allocations revolutionizes modern digital entrepreneurship.")

    add_body_p(doc, "Furthermore, as final-year Computer Science Engineering students, this project provides an ideal convergence of state-of-the-art software engineering paradigms: asynchronous full-stack microservices, structured JSON enforcement in generative models, deterministic mathematical simulation, relational persistence with SQLAlchemy, and responsive modern user interface architecture with React 19 and Tailwind CSS.")

    add_heading_2(doc, "1.5 Objectives of the System")
    add_body_p(doc, "The primary technical and functional objectives of the Adspire AI Major Project include:")

    add_bullet_p(doc, "Objective 1 – Autonomous Multi-Channel Generation:", "Develop an AI-driven marketing engine leveraging Google Gemini (gemini-3.8-flash) that autonomously transforms simple product inputs into comprehensive, structured marketing briefs comprising buyer personas, objection-busting frameworks, value propositions, primary ad copy with A/B variants, social posts, email newsletters, and 7-day distribution calendars.")
    add_bullet_p(doc, "Objective 2 – Commercial Visual Asset Synthesis:", "Build a visual studio that always shows the product the user asked for: licensed real photographs for branded products of any company, and AI generation (Gemini, FLUX.1-schnell, Pollinations) for other requests, with six style presets, three aspect ratios, and Gemini vision verification so that an unrelated image is never displayed.")
    add_bullet_p(doc, "Objective 3 – Predictive ROAS & Budget Planning:", "Construct an algorithmic financial simulation engine that dynamically models ad spend allocation across six networks (Meta, Google, LinkedIn, TikTok, Email, Influencer), calculating real-time CPC, CTR, impressions, clicks, conversions, CPA, and projected ROAS with duration-based pacing adjustments.")
    add_bullet_p(doc, "Objective 4 – Live Interactive Social Mockups:", "Design pixel-accurate, interactive client-side simulators mimicking authentic user feeds on Instagram (with interactive like and bookmark states), TikTok (vertical 9:16 player UI), LinkedIn Sponsored Posts, and Google SERP snippets.")
    add_bullet_p(doc, "Objective 5 – Secure Multi-User Platform & Administration:", "Provide registration and login with hashed passwords and signed tokens, private per-user campaign libraries and brand profiles, export to PDF, Markdown and JSON, and an Admin Panel to manage users, switch features on or off, set usage limits and monitor real usage through an activity log.")

    add_heading_2(doc, "1.6 Scope of the Project")
    add_body_p(doc, "The functional scope of Adspire AI encompasses the entire lifecycle of pre-campaign formulation, creative generation, financial simulation, and brief management:")

    add_bullet_p(doc, "In-Scope Capabilities:", "Natural language product parsing; structured JSON LLM orchestration; multi-angle ad copywriting; Instagram, LinkedIn, Twitter/X, and TikTok script generation; email newsletter crafting; 7-day content roadmap planning; commercial image synthesis across 6 artistic styles; multi-channel budget modeling across 6 ad networks; interactive social feed previewing; multi-user accounts with roles; brand profiles; persistence with SQLite or PostgreSQL; PDF, Markdown and JSON export; real-photo search with licence attribution; and an administration panel.")
    add_bullet_p(doc, "Operational Boundary:", "The system is engineered as a complete full-stack web application designed for local deployment (localhost:5000) and production cloud environments (Render). Actual automated ad spend deployment (direct programmatic bidding via Meta Marketing API or Google Ads API) is intentionally excluded to ensure risk-free simulation and financial governance prior to human review.")

    add_page_break(doc)
