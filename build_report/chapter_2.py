from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_figure_image, add_styled_table, add_table_caption
)

def build_chapter_2(doc):
    add_heading_1(doc, "CHAPTER 2: LITERATURE REVIEW")

    add_heading_2(doc, "2.1 Introduction to Digital Marketing")
    add_body_p(doc, "Digital marketing represents the strategic practice of connecting with prospective customers, building brand equity, and driving commercial conversions through digital communication channels, electronic devices, and internet-connected platforms. Unlike legacy broadcast media such as print, radio, and television, digital marketing operates on principles of bidirectional interaction, precise audience segmentation, behavioral tracking, and algorithmic auction mechanics. In recent years, consumer media consumption has migrated overwhelmingly toward mobile devices and fragmented social feeds, transforming the nature of customer attention.")

    add_body_p(doc, "Contemporary digital marketing demands that brands engage prospective buyers across diverse touchpoints throughout the marketing funnel: from initial top-of-funnel (TOFU) awareness and mid-funnel (MOFU) consideration to bottom-of-funnel (BOFU) conversion and post-purchase retention. To achieve sustained success, marketing organizations must produce high volumes of creative assets, formulate persuasive value propositions, and conduct continuous A/B testing across multiple digital ad networks.")

    add_heading_2(doc, "2.2 Artificial Intelligence in Marketing")
    add_body_p(doc, "The integration of Artificial Intelligence (AI) into marketing workflows has progressed through three fundamental historical paradigms:")

    add_bullet_p(doc, "Descriptive & Analytical AI (2010–2018):", "Characterized by statistical regressions, clustering algorithms, and historical data analysis. Machine learning models were employed to aggregate website analytics, segment consumer demographics, and compute historical churn rates without generating new content.")
    add_bullet_p(doc, "Predictive AI & Algorithmic Bidding (2018–2022):", "Marked by the deployment of real-time programmatic bidding engines on Google Ads and Meta Ads Manager. Neural networks predict user click probabilities (CTR) and conversion likelihoods, automating ad auction adjustments based on device signals, geolocation, and browsing histories.")
    add_bullet_p(doc, "Generative & Autonomous AI (2022–Present):", "Enabled by deep Transformer architectures, foundation Large Language Models (LLMs), and latent diffusion models. Systems have evolved from merely predicting outcomes to autonomously synthesizing original, high-converting marketing creative copy, video scripts, commercial product photography, and comprehensive campaign strategies.")

    add_body_p(doc, "In this current generative era, computational intelligence serves not merely as a passive analytical dashboard, but as an active creative co-pilot and autonomous marketing director capable of accelerating asset production by orders of magnitude.")

    add_heading_2(doc, "2.3 Generative AI and Foundation Architectures")
    add_body_p(doc, "The technical foundation of Adspire AI rests upon two breakthrough advances in artificial intelligence: the Transformer neural network architecture for natural language processing and Latent Diffusion Models (LDMs) for commercial image synthesis.")

    add_heading_3(doc, "2.3.1 Transformer Neural Networks and Self-Attention")
    add_body_p(doc, "Introduced by Vaswani et al. in the landmark paper 'Attention Is All You Need' (2017), the Transformer architecture replaced recurrent and convolutional layers with multi-head self-attention mechanisms. Self-attention enables the neural network to compute mathematical dependencies and contextual relationships between words across long textual sequences simultaneously, rather than processing tokens sequentially:")
    
    add_body_p(doc, "Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V")

    add_body_p(doc, "This mathematical formulation allows foundation models such as Google Gemini to comprehend nuanced marketing briefs, target demographic sensibilities, emotional tone modulations, and complex JSON schema formatting instructions with unprecedented syntactic and semantic accuracy.")

    add_heading_3(doc, "2.3.2 Latent Diffusion Models and Image Synthesis")
    add_body_p(doc, "Text-to-image synthesis has been revolutionized by Latent Diffusion Models (Rombach et al., 2022) and modern rectified flow architectures like FLUX.1. Diffusion models operate by systematically training a neural network to reverse a progressive forward Gaussian noise corruption process. Rather than diffusing directly in high-dimensional pixel space (which is computationally prohibitive), latent diffusion compresses images into a low-dimensional perceptual latent space using a pre-trained variational autoencoder (VAE). Textual conditioning prompts are projected via cross-attention layers, guiding the denoising trajectory to synthesize photorealistic commercial product imagery with studio lighting, realistic reflections, and sharp macro focus.")

    add_heading_2(doc, "2.4 AI-Based Content Generation")
    add_body_p(doc, "Research in natural language generation has demonstrated that prompting foundation models with structured schema constraints yields significantly superior commercial utility compared to unconstrained conversational dialogue. In commercial copywriting, effective copy must adhere to established psychological frameworks, including:")

    add_bullet_p(doc, "AIDA Framework:", "Attention (gripping hook), Interest (relatable problem narrative), Desire (transformational value proposition), and Action (unambiguous CTA).")
    add_bullet_p(doc, "PAS Framework:", "Problem (identifying the customer pain point), Agitation (amplifying the emotional/financial friction of inaction), and Solution (presenting the product as the definitive remedy).")
    add_bullet_p(doc, "Conversion Hypotheses in A/B Testing:", "Modern conversion rate optimization (CRO) requires testing contrasting marketing angles (e.g., direct utilitarian efficiency vs social proof / fear-of-missing-out) with clear conversion hypotheses.")

    add_body_p(doc, "Adspire AI operationalizes these research-backed psychological copywriting principles directly within its generative prompt templates, ensuring that generated marketing deliverables exhibit high persuasive rigor rather than generic prose.")

    add_heading_2(doc, "2.5 Existing Marketing Approaches and Software Suites")
    add_body_p(doc, "Several commercial tools and frameworks currently exist in the marketing technology (MarTech) landscape, each addressing narrow facets of digital marketing operations:")

    add_bullet_p(doc, "Copy.ai & Jasper.ai:", "Standalone AI writing assistants that generate basic ad snippets, blog posts, and emails. However, they lack integrated text-to-image commercial synthesis, do not offer empirical ROAS financial modeling, and provide no live interactive social feed mockups.")
    add_bullet_p(doc, "Midjourney & Stable Diffusion WebUIs:", "Exceptional image synthesis engines, but detached from marketing copy workflows. They lack copywriting generation, provide no budget planning, and often suffer from character hallucinations or text-rendering distortions when generating commercial products.")
    add_bullet_p(doc, "HubSpot & Marketo:", "Enterprise marketing automation platforms capable of email scheduling and CRM tracking. However, they require extensive manual asset creation, involve complex enterprise setups, and charge steep monthly subscriptions exceeding $800–$2,000.")
    add_bullet_p(doc, "AdCreative.ai:", "AI ad banner generator focusing on static visual layouts, but lacking comprehensive buyer persona profiling, short-form video scripts, omnichannel calendars, and unified financial pacing simulators.")

    add_heading_2(doc, "2.6 Limitations of Existing Approaches")
    add_body_p(doc, "A comprehensive comparative synthesis between existing market solutions and the unified Adspire AI suite is documented in Table 2.1:")

    add_table_caption(doc, "Table 2.1: Comparison of Existing Marketing Tools with Adspire AI")
    headers = ["Feature / Capability", "Jasper / Copy.ai", "Midjourney", "AdCreative.ai", "Adspire AI (Proposed)"]
    rows = [
        ["Multi-Channel Copy Generation", "Yes (Generic)", "No", "Limited", "Yes (Strict JSON Schema)"],
        ["Target Buyer Persona Profiling", "Partial", "No", "No", "Yes (Deep Psychographics)"],
        ["Commercial Image Synthesis", "No", "Yes (Artistic)", "Yes (Templates)", "Yes (AI + verified real photos)"],
        ["A/B Testing Variants & Angles", "Partial", "No", "Limited", "Yes (Hypothesis-Driven)"],
        ["Predictive ROAS Budget Planner", "No", "No", "No", "Yes (6 Channels + Pacing)"],
        ["Interactive Social Feed Mockups", "No", "No", "No", "Yes (IG, TikTok, LinkedIn, SERP)"],
        ["Relational Campaign Persistence", "Partial (Cloud)", "No", "Partial", "Yes (multi-user, PDF/MD/JSON)"],
        ["System Latency per Campaign", "5–10 seconds", "15–40 seconds", "10–20 seconds", "Under 3.5 seconds"],
        ["Cost & Accessibility", "High ($49–$199/mo)", "Paid ($10–$60/mo)", "High ($29–$299/mo)", "Open / Local Democratized"]
    ]
    add_styled_table(doc, headers, rows, [1.5, 1.2, 1.1, 1.2, 1.5])

    add_body_p(doc, "As summarized in Table 2.1, contemporary solutions force marketing practitioners into a fragmented, multi-subscription paradigm. Adspire AI bridges these systemic limitations by presenting an integrated, high-velocity, and democratized autonomous marketing suite.")

    add_page_break(doc)
