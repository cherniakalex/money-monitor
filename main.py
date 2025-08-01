# main.py - v0.19
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError

# --- CONFIG ---
CHROME_USER_DATA_DIR = r"C:\Projects\money_monitor\chrome_profile"
DOWNLOAD_PATH = r"C:\Projects\money_monitor\downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

load_dotenv()

LEUMI_USERNAME = os.getenv("LEUMI_USERNAME")
LEUMI_PASSWORD = os.getenv("LEUMI_PASSWORD")

LEUMI_URL = "https://www.leumi.co.il/he"

SCRIPT_VERSION = "0.19"
DO_LEUMI = False
DO_MAX = True

LEUMI_FILE = os.path.join(DOWNLOAD_PATH, "leumi-transactions.html")
MAX_FILE = os.path.join(DOWNLOAD_PATH, "max-credit-transactions.xlsx")


def parse_transactions_html(filepath):
    try:
        print(f"[📊] Parsing Leumi file: {filepath}")
        tables = pd.read_html(filepath)
        df = tables[0] if tables else None
        if df is not None:
            print(df.head())
        return df
    except Exception as e:
        print(f"[❌] Failed parsing Leumi HTML: {e}")
        return None


def parse_max_excel(filepath):
    try:
        print(f"[📊] Parsing Max file: {filepath}")
        df = pd.read_excel(filepath)
        print(df.head())
        return df
    except Exception as e:
        print(f"[❌] Failed parsing Max Excel: {e}")
        return None


def main():
    print(f"\n===== 🧾 Running Finance Scraper v{SCRIPT_VERSION} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
    print(f"[⚙️] Configuration: DO_LEUMI = {DO_LEUMI}, DO_MAX = {DO_MAX}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=CHROME_USER_DATA_DIR,
                headless=False,
                args=["--start-maximized"]
            )
            page = browser.new_page()

            # --- Login to Leumi ---
            print("[🌐] Navigating to Leumi homepage...")
            page.goto(LEUMI_URL, timeout=20000)

            print("[🖱️] Clicking login link...")
            page.get_by_text("כניסה לחשבונך").click()

            print("[⏳] Waiting for login page to load...")
            page.wait_for_load_state("networkidle", timeout=20000)

            print("[🔐] Waiting for username and password fields...")
            page.wait_for_selector("input[type='text']", timeout=10000)
            page.wait_for_selector("input[type='password']", timeout=10000)

            print("[🔑] Filling in credentials...")
            page.fill("input[type='text']", LEUMI_USERNAME)
            page.fill("input[type='password']", LEUMI_PASSWORD)

            print("[🔓] Submitting login form...")
            page.get_by_role("button", name="כניסה לחשבון").click()
            page.wait_for_load_state("networkidle")

            print("[📄] Waiting for dashboard to load...")
            page.wait_for_url("**/SPA.aspx**", timeout=20000)
            page.wait_for_selector("app-nav-menu", timeout=15000)

            # --- Leumi HTML Download ---
            if DO_LEUMI:
                print("[📄] Navigating to 'תנועות בחשבון'...")
                page.locator("app-nav-menu").get_by_text("עובר ושב").click()
                page.locator("a").filter(has_text="תנועות בחשבון").first.click()

                print("[💾] Triggering Leumi download...")
                page.get_by_role("button", name="שמירה").click()
                with page.expect_download(timeout=30000) as dl_info:
                    page.get_by_text("המשך").click()
                download = dl_info.value
                download.save_as(LEUMI_FILE)
                print(f"[✅] Leumi file saved to {LEUMI_FILE}")

            # --- Max Credit Card Flow ---
            if DO_MAX:
                print("[MAX] Starting MAX flow...")

                try:
                    print("[MAX] Navigating to Max credit section...")
                    page.locator("app-nav-menu").get_by_text("כרטיסי אשראי").click()

                    print("[MAX] Clicking on דפי פירוט link...")
                    page.locator("a").filter(has_text="דפי פירוט").click()

                    print("[MAX] Clicking on specific card (MAX 2711)...")
                    page.get_by_text("MAX 2711", exact=True).click()

                    print("[MAX] Clicking פעולות בכרטיס button...")
                    actions_button = page.locator("button").filter(has_text="פעולות בכרטיס").first
                    actions_button.click()

                    print("[MAX] Waiting for popup event...")
                    with page.expect_popup() as popup_event:
                        page.locator("#main a").filter(has_text="דפי פירוט").click()

                    print("[MAX] Popup triggered successfully.")
                    popup_page = popup_event.value
                    popup_page.wait_for_load_state("domcontentloaded", timeout=30000)
                    popup_page.bring_to_front()

                    # --- Maximize window + Log size ---
                    print("[MAX] Maximizing popup window...")
                    print("[MAX] Logging popup window size before maximizing...")
                    dimensions = popup_page.evaluate("""
                    () => ({
                        outerWidth: window.outerWidth,
                        outerHeight: window.outerHeight,
                        innerWidth: window.innerWidth,
                        innerHeight: window.innerHeight,
                        screenWidth: screen.width,
                        screenHeight: screen.height
                    })
                    """)
                    print(f"[MAX] Popup dimensions: outer=({dimensions['outerWidth']}x{dimensions['outerHeight']}), "
                          f"inner=({dimensions['innerWidth']}x{dimensions['innerHeight']}), "
                          f"screen=({dimensions['screenWidth']}x{dimensions['screenHeight']})")
                    popup_page.evaluate("window.resizeTo(1200, 1000);")

                    # --- Debug Text Dump ---
                    debug_file = os.path.join(DOWNLOAD_PATH, "popup_visible_texts.txt")
                    print(f"[DEBUG] Writing visible texts to: {debug_file}")
                    try:
                        with open(debug_file, "w", encoding="utf-8") as f:
                            for text in popup_page.locator("body *").all_inner_texts():
                                clean = text.strip()
                                if clean:
                                    f.write(clean + "\n")
                    except Exception as e:
                        print(f"[❌ DEBUG] Failed to write debug file: {e}")

                    print("[MAX] Waiting 1 second before locating dropdown...")
                    popup_page.wait_for_timeout(1000)

                    print("[MAX] Clicking dropdown using fallback by visible text...")
                    popup_page.get_by_text("max executive", exact=False).first.click()

                    popup_page.wait_for_timeout(500)

                    print("[MAX] Selecting 'כל הכרטיסים'...")
                    popup_page.get_by_text("כל הכרטיסים", exact=True).click()

                    print("[MAX] Waiting for and clicking 'יצוא לאקסל'...")
                    popup_page.wait_for_selector("text=יצוא לאקסל", timeout=30000)
                    with popup_page.expect_download(timeout=30000) as dl_max:
                        popup_page.get_by_text("יצוא לאקסל", exact=True).click()
                    download2 = dl_max.value
                    download2.save_as(MAX_FILE)
                    print(f"[MAX ✅] Max Excel saved to {MAX_FILE}")

                except Exception as e:
                    print(f"[❌ MAX Flow Error] {e}")

            # --- Parsing after download ---
            if DO_LEUMI:
                parse_transactions_html(LEUMI_FILE)
            if DO_MAX:
                parse_max_excel(MAX_FILE)

            input("Press Enter to close the browser...")
            browser.close()

    except TimeoutError:
        print("[❌] Timeout occurred during browser actions.")
    except Exception as e:
        print(f"[❌] Unexpected error: {e}")


if __name__ == "__main__":
    main()
    print("[ℹ️] Finished Finance Scraper.")
