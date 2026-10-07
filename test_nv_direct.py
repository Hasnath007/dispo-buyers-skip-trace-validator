import time
from playwright.sync_api import sync_playwright

def test_single_nv_sos(entity_name):
    print(f"--- 1. Testing Nevada SOS for: {entity_name} ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        # Test SilverFlume / NV SOS business search
        url = "https://esos.nv.gov/EntitySearch/OnlineEntitySearch"
        print(f"Navigating to {url}...")
        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(3000)
            page.screenshot(path=r"C:\buyers_information\nv_sos_search_page.png")
            print("Successfully loaded Nevada SOS portal!")
        except Exception as e:
            print("Error loading NV SOS:", e)
            
        browser.close()

if __name__ == '__main__':
    test_single_nv_sos("ALCHEMY INVESTMENTS LLC")
