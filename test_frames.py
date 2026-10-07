import time
from playwright.sync_api import sync_playwright

url = 'https://orion.nv.gov/portal/public/#/public/nvsos/en/CaseXscreen?screen=external-GenericFilingsSearch&tabRoute=business'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url, timeout=40000)
    page.wait_for_timeout(10000)
    
    print("Frames count:", len(page.frames))
    for i, frame in enumerate(page.frames):
        print(f"Frame {i}: url={frame.url} name={frame.name}")
        try:
            inputs = frame.locator('input').all()
            print(f"  Frame {i} inputs: {len(inputs)}")
            for j, inp in enumerate(inputs):
                print(f"    input {j}: {inp.get_attribute('name')} / {inp.get_attribute('placeholder')}")
        except Exception as e:
            print("  Frame error:", e)
            
    page.screenshot(path=r'C:\buyers_information\nvsos_frame_test.png')
    browser.close()
