import os
from build_report.docx_helper import (
    add_page_break, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_p, add_figure_image, add_styled_table,
    add_code_block, add_table_caption
)

A = "report_assets/"


def fig(doc, name, caption, width=6.2):
    add_figure_image(doc, os.path.abspath(A + name), caption, width_inches=width)


def build_chapter_7(doc):
    add_heading_1(doc, "CHAPTER 7: RESULTS AND DISCUSSION")

    add_heading_2(doc, "7.1 Application Screenshots")
    add_body_p(doc, "All screenshots in this section were captured automatically from the running application (http://127.0.0.1:5000) by a Playwright script driving Microsoft Edge, using real Gemini output and real images. The demonstration campaign was generated for the \"JBL Flip 6 Portable Speaker\". The administrator views include the demonstration campaigns — 60 campaigns for 60 different real products (JBL, Sony, Nike, Dyson, Amul and others), with no product repeated — and their activity history.")

    fig(doc, "fig_7_1_login.png", "Figure 7.1: Login Screen", width=4.8)
    add_body_p(doc, "Figure 7.1 shows the login screen. New users can switch to the registration form; when the administrator closes sign-ups the link is hidden and a message explains that an administrator must create the account.")

    fig(doc, "fig_7_2_studio_result.png", "Figure 7.2: Campaign Studio – Generated Ad Copy and A/B Variants", width=5.4)
    add_body_p(doc, "Figure 7.2 shows the Campaign Studio after generation: the brief on the left and, on the right, the Ad Copy & A/B tab with the primary Instagram advertisement, two variants with their test hypotheses and copy buttons. While a campaign is being written, the text streams in live with the name of the Gemini model in use and a character counter, and a cancel button stops the request.")

    fig(doc, "fig_7_3_strategy.png", "Figure 7.3: Generated Strategy, Persona and Value Propositions", width=4.8)
    add_body_p(doc, "Figure 7.3 shows the finished campaign: title, tagline and summary, the buyer persona with desires, pain points and an objection buster, the value propositions and Gemini's own budget recommendation. The model that produced the campaign is shown under the summary.")

    fig(doc, "fig_7_5_mockup.png", "Figure 7.5: Instagram Ad Mock-up with a Verified Real Product Photo", width=4.2)
    add_body_p(doc, "Figure 7.5 shows the Instagram mock-up. Because the product is a branded JBL speaker, Auto mode selected a real, licensed photograph of a JBL Flip speaker, which Gemini vision confirmed before it was attached to the campaign.")

    fig(doc, "fig_7_6_visual_real_photo.png", "Figure 7.6: Visual Studio – Real Photo for \"Bowers & Wilkins speakers\"", width=4.3)
    add_body_p(doc, "Figure 7.6 shows the Visual Studio for the prompt \"Bowers & Wilkins speakers\". Auto mode recognised the brand and returned a verified, licensed photograph; the photographer, licence (with link) and source page are credited below the image, and non-commercial licences are highlighted in amber. Download and Regenerate sit side by side on the image.")

    fig(doc, "fig_7_6b_lightbox.png", "Figure 7.7: Full-Screen Image Viewer", width=4.6)
    add_body_p(doc, "Clicking a generated image opens it full-screen (Figure 7.7) with Download and Close buttons; the viewer closes with Esc or a click outside the image.")

    fig(doc, "fig_7_7_visual_ai.png", "Figure 7.8: Visual Studio – Verified AI Image for a Generic Prompt", width=4.3)
    add_body_p(doc, "Figure 7.8 shows AI Generate mode for a prompt without a brand. The image was produced by the best engine available at that moment and shown only after Gemini vision confirmed that it shows the requested product.")

    fig(doc, "fig_7_8_budget.png", "Figure 7.9: Budget & ROAS Planner", width=4.3)
    add_body_p(doc, "Figure 7.9 shows the budget planner with an $8,000, 30-day plan: key figures (ROAS, revenue and profit, daily spend, conversions), the channel table and the spend doughnut chart. Changing a slider recalculates within a few milliseconds.")

    fig(doc, "fig_7_9_library.png", "Figure 7.10: Library – Administrator View of All Campaigns", width=5.0)
    fig(doc, "fig_7_10_admin_overview.png", "Figure 7.11: Admin Panel – Overview Metrics and Charts", width=4.0)
    add_body_p(doc, "Figures 7.10 and 7.11 show the administrator's views. The library lists every user's campaigns as cards with real product photos of well-known brands (JBL, Sony, Apple, Nike and others), the owner and a filter by user. The overview reports users, campaigns, images generated in the last seven days with the success rate, average generation times, a seven-day bar chart, the platform split and the status of each AI service — all computed from the database.")

    fig(doc, "fig_7_11_admin_users.png", "Figure 7.12: Admin Panel – User Management", width=5.0)
    add_body_p(doc, "Figure 7.12 shows user management: creating accounts, changing roles, enabling or disabling logins, resetting passwords and deleting users together with their data. The Settings section has switches that turn campaign generation, image generation, the budget planner and sign-ups on or off for all users, the hourly limits and the announcement banner.")


    add_heading_2(doc, "7.2 Module-Wise Functional Results")
    add_bullet_p(doc, "Campaign generation:", "Every generated campaign in testing contained all eleven sections, exactly seven calendar days and posts for Instagram, LinkedIn, X and TikTok. Content referred to the specific product (for example, the toothbrush test campaign and image prompt both mentioned the toothbrush). When the preferred model was overloaded, the next model completed the campaign without user action.")
    add_bullet_p(doc, "Visuals:", "Branded prompts for JBL, Bowers & Wilkins, Sony, Apple, Samsung, Nike and Canon returned verified real photographs; generic prompts returned verified AI images. In every case where the free engine drew something else, the verification rejected it and a retry or an explanation followed.")
    add_bullet_p(doc, "Accounts and data isolation:", "Users could not read or delete another user's campaigns or brands (HTTP 404), disabled users were logged out immediately, and administrators could not remove their own access.")
    add_bullet_p(doc, "Administration:", "Switching a feature off removed it from marketers' navigation and blocked its API (HTTP 403) while administrators kept access; the announcement appeared for all users; limits were enforced (HTTP 429).")
    add_bullet_p(doc, "Budget planner:", "All 25 industry and goal combinations produced allocations summing to 100 %, a higher budget always produced more conversions, and invalid input was rejected with HTTP 400.")

    add_heading_2(doc, "7.3 Testing Results and Performance")
    add_body_p(doc, "Testing was carried out at three levels. Table 7.1 summarises the results of the final run on the completed system.")
    add_table_caption(doc, "Table 7.1: Summary of Test Results")
    add_styled_table(doc, ["Test Level", "Tool", "What Is Covered", "Result"], [
        ["Unit tests", "pytest", "Auth, failed-login limit, isolation, streaming, brands, budget, admin controls, demo data, image and logo verification, photo scoring, Cloudflare and Unsplash (AI calls stubbed)", "33 / 33 passed"],
        ["Live API test", "Python requests", "Every endpoint against the running server with real Gemini and image services (system, auth, campaigns, images, library, brands, budget, admin)", "77 / 77 passed"],
        ["Browser test", "Playwright + Edge", "32 user journeys: login, studio, streaming, tabs, copy, mock-ups, exports, visual studio, image buttons and full-screen viewer, budget, library, admin panel, feature switches, phone layout", "32 / 32 passed"],
        ["Static checks", "oxlint, Vite build", "Frontend lint and production build", "0 warnings, build OK"],
    ], [1.2, 1.2, 3.0, 1.1])

    add_body_p(doc, "Table 7.2 lists measured response times. Non-AI operations were timed over 20 requests each on the development laptop; AI timings are the range observed across the test runs and depend heavily on the load of the external services.")
    add_table_caption(doc, "Table 7.2: Measured Response Times")
    add_styled_table(doc, ["Operation", "Measured Time", "Notes"], [
        ["Health check", "3 ms (median)", "p95 4 ms"],
        ["Budget simulation", "6 ms (median)", "p95 7 ms"],
        ["Library list", "9 ms (median)", "p95 12 ms"],
        ["Admin metrics", "11 ms (median)", "p95 15 ms; computed from all stored data"],
        ["Login", "151 ms (median)", "Deliberately slow salted password hashing"],
        ["Campaign generation (streamed)", "20 – 161 s", "Typically 80 – 110 s; longer when preferred Gemini models were overloaded (503)"],
        ["Real product photo", "13 – 72 s", "Search, download and Gemini vision check of several candidates"],
        ["AI image, Cloudflare FLUX (verified)", "6 – 20 s", "Including the Gemini vision and logo check"],
        ["AI image, free fallback (verified)", "13 – 106 s", "Includes the 45 s Pollinations queue and any verification retries"],
        ["Frontend bundle", "161 kB JS + 9 kB CSS", "gzip-compressed production build"],
    ], [2.2, 1.6, 2.7])

    add_body_p(doc, "Table 7.3 lists representative test cases from the suites.")
    add_table_caption(doc, "Table 7.3: Representative Test Cases")
    add_styled_table(doc, ["ID", "Scenario", "Expected Result", "Status"], [
        ["TC-01", "Generate a campaign with real Gemini (streamed)", "All 11 sections, 7 calendar days, auto-saved", "PASSED"],
        ["TC-02", "Missing product name or description", "HTTP 400 with message", "PASSED"],
        ["TC-03", "Read or delete another user's campaign", "HTTP 404, data unchanged", "PASSED"],
        ["TC-04", "\"JBL earbuds\" in Auto mode", "Verified real JBL photo with licence", "PASSED"],
        ["TC-05", "Image engine returns a portrait for an earbuds prompt", "Image rejected and never shown; retry or clear error", "PASSED"],
        ["TC-06", "Administrator disables a user", "Login 403, existing token rejected", "PASSED"],
        ["TC-07", "Feature switched off", "Hidden for marketers, API 403, admin still allowed", "PASSED"],
        ["TC-08", "Image limit set to 2 per hour", "Third request HTTP 429", "PASSED"],
        ["TC-09", "11 wrong passwords from one address", "11th attempt HTTP 429; correct logins never limited", "PASSED"],
        ["TC-10", "All 25 industry × goal budget combinations", "Shares sum to 100 %, conversions > 0", "PASSED"],
    ], [0.6, 2.4, 2.6, 0.8])

    add_heading_2(doc, "7.4 Image Accuracy Before and After the Redesign")
    add_body_p(doc, "The most visible problem in the first version was that images did not match the prompt. Table 7.4 compares the behaviour of the original implementation with the final one for the same prompts.")
    add_table_caption(doc, "Table 7.4: Image Results Before and After the Redesign")
    add_styled_table(doc, ["Prompt", "Original Version", "Final Version"], [
        ["Editorial … matte-black titanium JBL earbuds … black marble, neon blue rim lighting", "Portrait of a woman (free model), or a fixed stock photo", "Verified AI image of black earbuds on dark stone"],
        ["JBL earbuds", "Stock photo chosen by keyword (may be another brand)", "Real licensed photo of JBL ear buds, credited"],
        ["Bowers & Wilkins speakers", "Generic stock speaker or watch photo", "Real photo of a B&W speaker (CC BY 2.0)"],
        ["Sony earbuds (AI mode)", "Unbranded or unrelated image", "FLUX image with the \"SONY\" logo, spelling verified"],
        ["Any product without a catalogue keyword", "Always a wristwatch photo", "Verified AI image of the requested product"],
        ["Regenerate button", "Same image every time (fixed seed)", "New variation on every click"],
    ], [2.3, 2.0, 2.2])

    add_heading_2(doc, "7.5 Advantages of the System")
    add_bullet_p(doc, "Speed:", "A complete multi-channel campaign in one to two minutes instead of days of agency work, with visible progress.")
    add_bullet_p(doc, "Trustworthy visuals:", "Every image is checked before it is shown; branded products use real licensed photos with attribution.")
    add_bullet_p(doc, "Honesty about AI:", "The interface always states which model or source produced a result and warns when a template or simplified image was used.")
    add_bullet_p(doc, "Secure and multi-user:", "Hashed passwords, signed tokens, private libraries, roles, limits and administrator controls.")
    add_bullet_p(doc, "Low cost:", "Runs on free tiers (Gemini, Cloudflare Workers AI, open photo libraries); more capacity is a configuration change, not a code change.")

    add_page_break(doc)
