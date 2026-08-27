"""Capture UI screenshots for the README."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / "docs"
BASE = "http://localhost:8501"


def wait_streamlit(page):
    page.goto(BASE, timeout=60000)
    page.wait_for_selector('[data-testid="stMain"]', timeout=60000)
    page.wait_for_timeout(4000)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        wait_streamlit(page)

        # Chat tab
        box = page.get_by_placeholder("e.g. How did the Space Shuttle differ", exact=False)
        box.fill("How many people have walked on the Moon and during which program?")
        page.get_by_role("button", name="Ask").click()
        page.wait_for_timeout(20000)
        page.screenshot(path=OUT / "screenshot_chat.png", full_page=True)

        # Monitoring tab
        page.get_by_role("tab", name="Monitoring").click()
        page.wait_for_timeout(8000)
        page.screenshot(path=OUT / "screenshot_dashboard.png", full_page=True)

        browser.close()
    print(f"screenshots written to {OUT}")


if __name__ == "__main__":
    main()
