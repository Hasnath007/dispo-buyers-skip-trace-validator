import time
from playwright.sync_api import sync_playwright

url = 'https://orion.nv.gov/portal/public/#/public/nvsos/en/CaseXscreen?screen=external-GenericFilingsSearch&tabRoute=business'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = context.new_page()
    print("Navigating...")
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    print("Waiting 10s for Angular/React to render...")
    page.wait_for_timeout(10000)
    
    # Dump HTML or all input fields
    inputs = page.locator('input').all()
    print(f"Total input tags found: {len(inputs)}")
    for i, inp in enumerate(inputs):
        try:
            print(f"Input {i}: name={inp.get_attribute('name')} id={inp.get_attribute('id')} placeholder={inp.get_attribute('placeholder')} aria-label={inp.get_attribute('aria-label')} type={inp.get_attribute('type')}")
        except Exception as e:
            pass
            
    page.screenshot(path=r'C:\buyers_information\nvsos_page.png')
    print("Saved screenshot.")
    browser.close()
