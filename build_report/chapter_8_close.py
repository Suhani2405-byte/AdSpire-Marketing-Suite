"""Chapter 8, Conclusion and References laid out like the Sangam University template."""
from build_report import docx_helper as H
from build_report.docx_helper import add_heading_1, add_heading_2, add_body_p, add_bullet_p


def build_chapter_8_close(doc):
    add_heading_1(doc, "CHAPTER 8: CHALLENGES AND LIMITATIONS")

    add_heading_2(doc, "8.1 Challenges Faced")
    add_bullet_p(doc, "Wrong images from free models:", "the free fallback model does not know brand names and drew a woman's portrait for \"JBL earbuds\"; prompt analysis, real photos and Gemini vision verification solved this.")
    add_bullet_p(doc, "Overloaded and limited AI services:", "Gemini models often answered 503 (high demand), Gemini image models had a free limit of zero, Hugging Face returned 402 (no credits) and Pollinations allows one image every 45 seconds. Model fail-over with cool-downs, a provider chain and request queuing keep the system working.")
    add_bullet_p(doc, "Brand logos on AI images:", "FLUX sometimes misspelled brand names (for example \"NIKE\" as \"AIKE\"). Gemini vision now reads the logo and rejects misspelled images; the last attempt is made without a logo.")
    add_bullet_p(doc, "Defects found by testing:", "a console encoding crash in image requests, a rejected Cloudflare parameter, collapsed charts and a login limit that counted successful logins were all fixed and covered by tests.")

    add_heading_2(doc, "8.2 System Limitations")
    add_bullet_p(doc, "Free AI quotas:", "FLUX on Cloudflare Workers AI allows 10,000 neurons per day (a few dozen images), resetting at 00:00 UTC (5:30 AM IST); after that the system falls back to the weaker Pollinations tier with a watermark.")
    add_bullet_p(doc, "Logos and text in images:", "AI images print the brand name as text, not the official logo artwork.")
    add_bullet_p(doc, "Photo licences:", "some openly licensed photos are non-commercial; they are labelled and must not be used in paid advertisements.")
    add_bullet_p(doc, "Simulated budgets:", "ROAS figures come from industry benchmark tables, not from live auction data, so seasonal changes are not reflected.")

    add_heading_2(doc, "8.3 Future Scope")
    add_bullet_p(doc, "Direct publishing:", "connect to the Meta, Google Ads and TikTok advertising APIs so that an approved campaign can be published in one click.")
    add_bullet_p(doc, "Learning from results:", "import real click and conversion data from live campaigns and use it to improve future copy and budget suggestions.")
    add_bullet_p(doc, "Video advertisements:", "turn the generated video script into a finished short video with text-to-speech and video generation models.")

    # ------------------------------------------------------------------ CONCLUSION
    add_heading_1(doc, "CONCLUSION")
    add_body_p(doc, "The project \"Adspire AI: AI-Powered Marketing Campaign and Ad Visual Generator\" successfully achieves its aim of turning a short product brief into a complete and consistent marketing campaign. From a few fields of input, the system produces a buyer persona, value propositions, a primary advertisement with A/B variants, posts for four social networks, a video script, an e-mail newsletter, a seven-day calendar, product visuals and a budget plan, and streams the text to the browser while Google Gemini is writing it.")
    add_body_p(doc, "Correctness of the visuals was treated as a first-class requirement. Gemini analyses every prompt, branded products are matched with licensed real photographs, AI images are generated with the brand name on the product, and every candidate image is checked by Gemini vision for the right product, unwanted people and the spelling of the logo. An image that does not match the request is never shown; the user receives a clear message instead.")
    add_body_p(doc, "The system was delivered as a secure multi-user web application with a Flask backend and a React frontend, with hashed passwords, signed tokens, private libraries, brand profiles and an administration panel that controls users, features and usage limits. It was verified with 33 automated unit tests, a 77-check live API test and a 32-step browser test, all of which pass.")
    add_body_p(doc, "In conclusion, the project shows that careful engineering around generative AI — structured output, model fail-over, provider chains and automatic verification — turns unreliable free AI services into a dependable marketing assistant that runs on free tiers and ordinary hardware, and provides a solid foundation for direct ad publishing and learning from real campaign results.")

    # ------------------------------------------------------------------ REFERENCES
    add_heading_1(doc, "REFERENCES")
    refs = [
        "A. Vaswani et al., “Attention Is All You Need,” in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, 2017, pp. 5998–6008.",
        "T. Brown et al., “Language Models are Few-Shot Learners,” in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, 2020, pp. 1877–1901.",
        "R. Rombach, A. Blattmann, D. Lorenz, P. Esser and B. Ommer, “High-Resolution Image Synthesis with Latent Diffusion Models,” in Proc. IEEE/CVF CVPR, 2022, pp. 10684–10695.",
        "Gemini Team, Google, “Gemini: A Family of Highly Capable Multimodal Models,” arXiv preprint arXiv:2312.11805, 2023.",
        "Black Forest Labs, “FLUX.1 [schnell],” 2024. [Online]. Available: https://huggingface.co/black-forest-labs/FLUX.1-schnell. [Accessed: 2026].",
        "T. Davenport, A. Guha, D. Grewal and T. Bressgott, “How Artificial Intelligence Will Change the Future of Marketing,” Journal of the Academy of Marketing Science, vol. 48, no. 1, pp. 24–42, 2020.",
        "M.-H. Huang and R. T. Rust, “A Strategic Framework for Artificial Intelligence in Marketing,” Journal of the Academy of Marketing Science, vol. 49, no. 1, pp. 30–50, 2021.",
        "D. Chaffey and F. Ellis-Chadwick, Digital Marketing: Strategy, Implementation and Practice, 7th ed. Harlow, UK: Pearson Education, 2019.",
        "Google, “Gemini API Documentation,” 2026. [Online]. Available: https://ai.google.dev/gemini-api/docs. [Accessed: 2026].",
        "Cloudflare, “Workers AI: Pricing and Limits,” 2026. [Online]. Available: https://developers.cloudflare.com/workers-ai/. [Accessed: 2026].",
        "Pallets Projects, “Flask Documentation,” 2024. [Online]. Available: https://flask.palletsprojects.com/. [Accessed: 2026].",
        "Meta Open Source, “React: The Library for Web and Native User Interfaces,” 2024. [Online]. Available: https://react.dev/. [Accessed: 2026].",
        "OWASP Foundation, “Password Storage Cheat Sheet,” 2026. [Online]. Available: https://cheatsheetseries.owasp.org/. [Accessed: 2026].",
    ]
    for i, ref in enumerate(refs, 1):
        H.add_reference(doc, f"[{i}] {ref}")
