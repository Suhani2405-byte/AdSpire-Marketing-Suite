"""
Capture real application screenshots for Chapter 7 of the report.

    python build_report/screenshots.py      (app must be running on http://127.0.0.1:5000)

Needs: pip install playwright (uses the installed Microsoft Edge) and the admin account.
Writes report_assets/fig_7_*.png
"""
import os
import re
import sys

from playwright.sync_api import sync_playwright, expect

B = os.getenv("ADSPIRE_URL", "http://127.0.0.1:5000")
ADMIN = (os.getenv("ADSPIRE_ADMIN", "admin@adspire.app"), os.getenv("ADSPIRE_ADMIN_PW", "Admin@12345"))
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "report_assets")

PRODUCT = "JBL Flip 6 Portable Speaker"
DESCRIPTION = ("Waterproof (IP67) portable Bluetooth speaker with bold JBL Original Pro Sound, a racetrack-shaped "
               "woofer, separate tweeter, 12 hours of playtime and PartyBoost to pair multiple speakers.")
AUDIENCE = "College students, travellers and outdoor music lovers aged 18-30"


def shot(page, name, full=False, clip_sel=None):
    path = os.path.join(OUT, name + ".png")
    if clip_sel:
        page.locator(clip_sel).first.screenshot(path=path)
    else:
        page.screenshot(path=path, full_page=full)
    print("saved", name)


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
        page = ctx.new_page()
        page.on("dialog", lambda d: d.accept())

        # login screen
        page.goto(B + "/")
        expect(page.get_by_role("button", name="Log In")).to_be_visible()
        shot(page, "fig_7_1_login")
        page.locator("input[type=email]").fill(ADMIN[0])
        page.locator("input[type=password]").fill(ADMIN[1])
        page.get_by_role("button", name="Log In").click()
        expect(page.locator(".user-menu")).to_be_visible()
        # full-page screenshots repeat a sticky header mid-page; make it static while capturing
        page.add_style_tag(content=".main-navbar{position:static !important}")

        # campaign studio: fill + stream
        page.locator("input.modern-input").first.fill(PRODUCT)
        page.locator("textarea.modern-textarea").first.fill(DESCRIPTION)
        page.locator("input.modern-input").nth(1).fill(AUDIENCE)
        sels = page.locator(".config-card select.modern-select")
        sels.nth(1).select_option("Instagram")
        sels.nth(2).select_option("Product Launch")
        sels.nth(3).select_option("Consumer Electronics & D2C")
        sels.nth(4).select_option("High Energy & Dynamic")
        page.get_by_role("button", name=re.compile("Generate Full Campaign Suite")).click()
        expect(page.locator(".stream-preview")).to_be_visible(timeout=240000)
        page.wait_for_timeout(2500)
        page.evaluate("window.scrollTo(0, 380)")
        shot(page, "fig_7_2_streaming")
        expect(page.locator(".hero-strategy-card h2")).to_be_visible(timeout=300000)
        page.evaluate("window.scrollTo(0, 380)")
        shot(page, "fig_7_3_strategy")

        page.locator(".sub-nav-btn", has_text="Ad Copy").click()
        page.wait_for_timeout(300)
        shot(page, "fig_7_4_ad_copy", clip_sel="#campaign-output-pane")

        page.locator(".sub-nav-btn", has_text="Live Ad Mockups").click()
        expect(page.locator(".ig-media-img")).to_be_visible(timeout=300000)
        page.wait_for_timeout(800)
        shot(page, "fig_7_5_mockup", clip_sel="#campaign-output-pane")

        # visual studio: real photo for a brand + AI image for a generic prompt
        page.locator(".nav-pill-btn", has_text="Visual Studio").click()
        page.locator("textarea.modern-textarea").fill("Bowers & Wilkins speakers")
        page.locator(".mode-grid .style-chip-btn", has_text="Auto").click()
        page.get_by_role("button", name=re.compile("Generate Creative Asset")).click()
        expect(page.locator(".rendered-asset-img")).to_be_visible(timeout=300000)
        page.wait_for_timeout(800)
        shot(page, "fig_7_6_visual_real_photo", full=True)
        # click-to-expand viewer
        page.locator(".rendered-asset-img").first.click()
        expect(page.locator(".lightbox-img")).to_be_visible()
        page.wait_for_timeout(600)
        shot(page, "fig_7_6b_lightbox")
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

        page.locator("textarea.modern-textarea").fill("a bamboo toothbrush on a bathroom shelf, soft morning light")
        page.locator(".mode-grid .style-chip-btn", has_text="AI Generate").click()
        page.get_by_role("button", name=re.compile("Generate Creative Asset")).click()
        page.wait_for_timeout(1500)
        expect(page.locator(".rendered-asset-img")).to_be_visible(timeout=300000)
        page.wait_for_timeout(800)
        shot(page, "fig_7_7_visual_ai", full=True)

        # budget
        page.locator(".nav-pill-btn", has_text="Budget Planner").click()
        page.locator("input[type=range]").first.fill("8000")
        page.wait_for_timeout(1200)
        shot(page, "fig_7_8_budget", full=True)

        # library (admin = all campaigns)
        page.locator(".nav-pill-btn", has_text="All Campaigns").click()
        expect(page.locator(".library-item-card").first).to_be_visible()
        page.wait_for_timeout(600)
        shot(page, "fig_7_9_library")

        # admin panel
        page.locator(".nav-pill-btn", has_text="Admin Panel").click()
        expect(page.locator(".chart-card canvas").first).to_be_visible()
        page.wait_for_timeout(1200)
        shot(page, "fig_7_10_admin_overview", full=True)
        page.locator(".admin-section-tabs button", has_text="Users").click()
        page.wait_for_timeout(600)
        shot(page, "fig_7_11_admin_users")
        page.locator(".admin-section-tabs button", has_text="Settings").click()
        expect(page.locator(".switch-row").first).to_be_visible()
        shot(page, "fig_7_12_admin_settings", full=True)

        # phone layout
        mob = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True)
        mp = mob.new_page()
        mp.goto(B + "/")
        mp.locator("input[type=email]").fill(ADMIN[0])
        mp.locator("input[type=password]").fill(ADMIN[1])
        mp.get_by_role("button", name="Log In").click()
        expect(mp.locator(".user-menu")).to_be_visible()
        mp.wait_for_timeout(600)
        mp.screenshot(path=os.path.join(OUT, "fig_7_13_mobile.png"))
        print("saved fig_7_13_mobile")
        browser.close()


if __name__ == "__main__":
    sys.exit(main())
