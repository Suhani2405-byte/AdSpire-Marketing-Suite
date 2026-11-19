"""Chapter 1 laid out like the Sangam University template: Introduction, Aim, Objectives, Vision, Scope."""
from build_report.docx_helper import add_heading_1, add_heading_2, add_body_p, add_bullet_p


def build_chapter_1(doc):
    add_heading_1(doc, "CHAPTER 1: INTRODUCTION")

    add_heading_2(doc, "1.1 Introduction")
    add_body_p(doc, "Every business that sells a product has to market it. A single campaign today needs a clear picture of the buyer, persuasive advertisement copy with alternatives to test, posts written separately for Instagram, LinkedIn, X and TikTok, an e-mail newsletter, a posting calendar, product images in the right sizes for each platform, and a budget that is split sensibly across advertising channels. In an agency this work is shared between a strategist, a copywriter, a designer and a media planner and takes several days; small businesses and students rarely have such a team.")
    add_body_p(doc, "Large language models (LLMs) such as Google Gemini can now write fluent, structured marketing text in seconds, and image models such as FLUX can draw product pictures from a description. Used on their own, however, they have clear weaknesses: free image models do not know brand names and frequently draw something unrelated (for example a portrait of a woman for the prompt \"JBL earbuds\"), LLM services are often overloaded, and their output is not connected to any budget or preview.")
    add_body_p(doc, "This project builds Adspire AI, a complete web application that turns a short product brief into a full marketing campaign in about one to two minutes. Campaign text is written by Google Gemini and streamed to the browser while it is being produced, with automatic fail-over between six Gemini models. Product visuals come either from licensed real photographs or from AI generation, and every image is checked by Gemini vision before it is shown, so a picture that does not match the prompt is never displayed. A budget and ROAS (return on ad spend) planner, realistic advertisement mock-ups, a campaign library and an administration panel complete the system.")

    add_heading_2(doc, "1.2 Aim")
    add_body_p(doc, "The aim of this project is to design, implement and test a secure, multi-user web application that generates a complete, consistent marketing campaign — strategy, copy, social content, e-mail, calendar, verified product visuals and a budget plan — from a short product brief, using generative AI while guaranteeing that every displayed image actually shows the requested product.")

    add_heading_2(doc, "1.3 Objectives")
    add_body_p(doc, "The specific objectives of the project are:")
    add_bullet_p(doc, "Campaign generation:", "to turn a product name, description, audience, platform, goal, industry and tone into a structured campaign (buyer persona, value propositions, a primary advertisement with two A/B variants, posts for four social networks, a video script, an e-mail newsletter, a seven-day calendar and an image prompt) using Google Gemini with strict JSON output.")
    add_bullet_p(doc, "Live streaming and reliability:", "to stream the campaign to the browser while it is written, and to switch automatically to another Gemini model when one is overloaded, out of quota or silent.")
    add_bullet_p(doc, "Correct product visuals:", "to provide Auto, Real Photo and AI modes, use licensed real photographs for branded products of any company, generate AI images with the brand name on the product, and verify every image with Gemini vision before it is shown.")
    add_bullet_p(doc, "Budget planning:", "to simulate spend, clicks, conversions, cost per acquisition and ROAS across six advertising channels for five industries and five campaign goals.")
    add_bullet_p(doc, "Previews and export:", "to show realistic Instagram, TikTok, LinkedIn and Google Search mock-ups, and to export campaigns as PDF, Markdown and JSON.")
    add_bullet_p(doc, "Secure multi-user platform:", "to provide registration and login with hashed passwords and signed tokens, private campaign libraries and brand profiles, and an administration panel to manage users, switch features on or off, set usage limits and monitor activity.")
    add_bullet_p(doc, "Verification:", "to test every function with automated unit tests, a live API test against the real AI services and a browser test that drives every screen.")

    add_heading_2(doc, "1.4 Vision")
    add_body_p(doc, "The project envisions a small business owner who can describe a product in a few sentences and, a minute later, review a complete campaign that a team of specialists would otherwise need days to prepare: who the buyer is, what to say to them on each platform, what the advertisement will look like in the feed, and how much the campaign is likely to return.")
    add_body_p(doc, "Trust is central to this vision. A marketing tool that shows the wrong product is worse than no tool, so Adspire AI checks its own images and tells the user honestly which engine produced each result.")

    add_heading_2(doc, "1.5 Scope")
    add_body_p(doc, "The scope of the project covers the complete pre-launch life cycle of a digital marketing campaign: entering a product brief or a saved brand profile; generating and streaming the campaign; creating, verifying and downloading product visuals; previewing the advertisement on four platforms; simulating the budget; saving, searching and exporting campaigns; and administering users, features and usage limits.")
    add_body_p(doc, "The system runs locally (http://localhost:5000) and can be deployed to the cloud on Render with a PostgreSQL database. Publishing advertisements directly to advertising accounts and measuring live campaign performance are outside the scope; budget figures are benchmark-based simulations.")
