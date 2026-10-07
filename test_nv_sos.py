import time
import csv
import re
import os
from playwright.sync_api import sync_playwright

INPUT_CSV = r'C:\buyers_information\Dispo Board Competitor Buyers (3).csv'
OUTPUT_CSV = r'C:\buyers_information\Live_Prioritized_Buyers_Output.csv'
NV_SOS_URL = 'https://orion.nv.gov/portal/public/#/public/nvsos/en/CaseXscreen?screen=external-GenericFilingsSearch&tabRoute=business'

def fetch_nv_sos_officers(page, entity_name):
    """Searches Nevada SOS for an entity name and extracts Active Managing Members & Address."""
    print(f"  [NV SOS] Searching for entity: {entity_name}")
    officers = []
    try:
        page.goto(NV_SOS_URL, timeout=45000)
        page.wait_for_timeout(3000)
        
        # Locate entity name input
        entity_input = page.locator('input[placeholder*="Entity Name"], input[name*="entityName"], input[aria-label*="Entity Name"]').first
        if not entity_input.is_visible():
            # Try by label
            entity_input = page.locator('label:has-text("Entity Name") + input, input').nth(1)
            
        entity_input.fill("")
        entity_input.type(entity_name, delay=30)
        page.wait_for_timeout(1000)
        
        # Click search button
        search_btn = page.locator('button:has-text("Search"), input[value="Search"]').first
        search_btn.click()
        page.wait_for_timeout(4000)
        
        # Look for search results table
        results = page.locator('table tbody tr, .search-result-row, a[href*="CaseXscreen"]').all()
        if not results:
            print(f"  [NV SOS] No search results found for {entity_name}")
            return officers
            
        # Click the first result link
        first_result_link = page.locator('table tbody tr a, .search-result-row a, a:has-text("' + entity_name.split()[0] + '")').first
        if first_result_link.is_visible():
            first_result_link.click()
            page.wait_for_timeout(5000)
            
            # Extract Active Officers from the details page
            body_text = page.locator("body").inner_text()
            if "Active Officers" in body_text:
                print(f"  [NV SOS] Found Active Officers section for {entity_name}")
                # Parse officer lines from DOM
                officer_rows = page.locator('text=Active Officers').locator('xpath=ancestor::div[contains(@class, "card") or contains(@class, "panel") or contains(@class, "section") or contains(@class, "table")]//tr').all()
                if not officer_rows:
                    officer_rows = page.locator('tr:has-text("Managing Member"), tr:has-text("Manager"), tr:has-text("Individual")').all()
                    
                for r in officer_rows:
                    txt = r.inner_text().strip()
                    if txt and "Inactive" not in txt:
                        officers.append(txt)
        else:
            print(f"  [NV SOS] Could not click result link for {entity_name}")
            
    except Exception as e:
        print(f"  [NV SOS Error] {e}")
        
    return officers

def main():
    print("Testing NV SOS lookup pipeline...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        officers = fetch_nv_sos_officers(page, "FLIP SIDE PROPERTIES LLC")
        print("Officers found:", officers)
        browser.close()

if __name__ == '__main__':
    main()
