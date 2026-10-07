import time
import csv
import re
import os
from playwright.sync_api import sync_playwright

# Configuration
INPUT_CSV = r'C:\buyers_information\Dispo Board Competitor Buyers (3).csv'
EMAIL = 'skinnovationstech@gmail.com'
PASSWORD = 'c1nl5&Ml&@5LCr'
LOGIN_URL = 'https://app.dealmachine.com/login'
SCREENSHOT_DIR = r'C:\buyers_information\screenshots'

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def run():
    print("Loading CSV file...")
    properties = []
    try:
        with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip two header rows
            next(reader, None)
            next(reader, None)
            for row in reader:
                if not row or not row[0]:
                    continue
                address = row[0]
                
                # Check Buyer Entity 1 (row[12]), if empty, use Buyer Name 1 (row[13])
                buyer_name = ""
                if len(row) > 12 and row[12].strip():
                    buyer_name = row[12].strip()
                elif len(row) > 13 and row[13].strip():
                    buyer_name = row[13].strip()
                    
                properties.append((address, buyer_name))
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return

    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Navigating to DealMachine...")
        page.goto(LOGIN_URL, timeout=60000)
        
        print("Logging in automatically...")
        page.wait_for_timeout(5000) # Wait for page to fully load
        
        try:
            # Try multiple selectors for email
            if page.locator('input[type="email"]').is_visible():
                page.locator('input[type="email"]').fill(EMAIL)
            elif page.locator('input[name="email"]').is_visible():
                page.locator('input[name="email"]').fill(EMAIL)
            else:
                page.locator('input').first.fill(EMAIL)
                
            page.wait_for_timeout(1000)
            
            # Try multiple selectors for password
            if page.locator('input[type="password"]').is_visible():
                page.locator('input[type="password"]').fill(PASSWORD)
            elif page.locator('input[name="password"]').is_visible():
                page.locator('input[name="password"]').fill(PASSWORD)
                
            page.wait_for_timeout(1000)
            
            # Click the login button instead of pressing Enter
            if page.get_by_text("Continue With Email", exact=False).is_visible():
                page.get_by_text("Continue With Email", exact=False).first.click()
            elif page.get_by_role("button", name="Log In").is_visible():
                page.get_by_role("button", name="Log In").first.click()
            elif page.get_by_role("button", name="Sign In").is_visible():
                page.get_by_role("button", name="Sign In").first.click()
            else:
                page.locator('button[type="submit"]').first.click()
        except Exception as e:
            print("Could not auto-login:", e)
        
        print("Waiting for login to complete (15 seconds)...")
        page.wait_for_timeout(15000)
        
        print("Starting to process addresses...")
        
        csv_path = r'C:\buyers_information\Extracted_Contacts.csv'
        processed_addresses = set()
        if os.path.isfile(csv_path) and os.path.getsize(csv_path) > 0:
            try:
                with open(csv_path, mode='r', encoding='utf-8') as f:
                    r = csv.reader(f)
                    next(r, None)
                    for row in r:
                        if row and row[0]:
                            processed_addresses.add(row[0].strip())
            except Exception:
                pass
        else:
            with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Property Address', 'Buyer Name / LLC', 'Owner Name', 'Phones', 'Emails'])
        
        print(f"Found {len(processed_addresses)} properties already completed in CSV. Resuming seamlessly...")
        
        for row_index, (address, buyer_name) in enumerate(properties, start=3):
            if not address:
                continue
            if row_index < 71:
                continue
            if address.strip() in processed_addresses:
                print(f"[Row {row_index}] Skipping already processed: {address}")
                continue
                
            print(f"\n[{row_index}] Searching for address: {address}")
            
            try:
                # Re-evaluate search bar inside the loop to ensure it's found
                search_bar = page.locator('input[placeholder*="Search"]').first
                if not search_bar.is_visible():
                    search_bar = page.locator('input[type="text"]').first
                if search_bar.is_visible():
                    # Clear search bar manually to trigger React events properly
                    search_bar.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    
                    # Wait for old dropdown results to disappear
                    for _ in range(10):
                        if not page.locator('text=/Jump to Location/i').first.is_visible():
                            break
                        page.wait_for_timeout(200)
                        
                    # Type new address slowly
                    page.keyboard.type(address, delay=50)
                    
                    print("Waiting for suggestion...")
                    page.wait_for_timeout(3000) 
                    
                    # Click the address in the dropdown
                    house_number = address.split(',')[0].strip().split()[0]
                    
                    print(f"Waiting for dropdown suggestion...")
                    try:
                        # First, try to find the explicit action button (Jump to Location / Open Property)
                        # We wait a short time because it might not exist for all addresses (e.g., condos)
                        button = page.locator('text=/Jump to Location|Open Property/i').first
                        
                        try:
                            button.wait_for(state="visible", timeout=4000)
                            print("Dropdown button found! Clicking it directly...")
                            button.click(force=True, timeout=3000)
                        except:
                            # If no button appears, click the first suggestion text containing the house number
                            print("No direct button found. Clicking the first suggestion text...")
                            suggestion_text = page.locator(f'text=/{house_number}/i').first
                            suggestion_text.wait_for(state="visible", timeout=5000)
                            suggestion_text.click(force=True, timeout=3000)
                            
                        page.wait_for_timeout(2000)
                    except Exception as e:
                        print(f"Could not find or click any dropdown suggestion: {e}")
                        print("Pressing Enter to load side panel as fallback...")
                        page.keyboard.press("Enter")
                    
                    # Wait up to 5 seconds to see if it auto-navigates
                    navigated = False
                    print("Waiting for property to open...")
                    for _ in range(15):
                        if "property" in page.url:
                            navigated = True
                            break
                        page.wait_for_timeout(500)
                        
                    if not navigated:
                        # DealMachine often loads a list of results on the right side panel instead of auto-navigating.
                        # We need to click the first property in that list.
                        print("Property didn't open immediately. Clicking the result from the side panel list...")
                        try:
                            # We will click ALL elements containing the house number until the property opens!
                            elements = []
                            for scroll_attempt in range(10):
                                elements = page.locator(f'text=/{house_number}/i').all()
                                if len(elements) > 0:
                                    break
                                
                                print(f"Not found in view (attempt {scroll_attempt+1}/10). Scrolling side panel...")
                                try:
                                    # Hover over an 'Est. Value' to focus the side panel's scrollable area
                                    est_value = page.locator('text=/Est. Value/i').first
                                    if est_value.is_visible():
                                        est_value.hover()
                                        page.mouse.wheel(0, 1500) # Scroll down
                                except Exception as e:
                                    print(f"Scroll error: {e}")
                                page.wait_for_timeout(1500)
                                
                            print(f"Found {len(elements)} elements containing '{house_number}'. Trying them all...")
                            
                            for i, element in enumerate(elements):
                                print(f"Clicking side-panel element {i+1}/{len(elements)}...")
                                try:
                                    element.click(force=True, timeout=2000)
                                    page.wait_for_timeout(1500)
                                    if "property" in page.url:
                                        print("URL changed to property! Property opened successfully.")
                                        navigated = True
                                        break
                                        
                                    print("Text click didn't navigate, trying parent container...")
                                    element.locator("xpath=..").click(force=True, timeout=2000)
                                    page.wait_for_timeout(1500)
                                    if "property" in page.url:
                                        print("URL changed to property! Property opened successfully.")
                                        navigated = True
                                        break
                                        
                                    print("Parent click didn't navigate, trying grandparent container...")
                                    element.locator("xpath=../..").click(force=True, timeout=2000)
                                    page.wait_for_timeout(1500)
                                    if "property" in page.url:
                                        print("URL changed to property! Property opened successfully.")
                                        navigated = True
                                        break
                                except Exception as e:
                                    print(f"Failed to click element {i+1} hierarchy: {e}")
                                    
                        except Exception as e:
                            print(f"Error finding side panel elements: {e}")
                            
                        if not navigated:
                            # Wait again just in case it was slow
                            for _ in range(15):
                                if "property" in page.url:
                                    navigated = True
                                    break
                                page.wait_for_timeout(500)
                            
                    if not navigated:
                        print("Warning: URL did not change. Navigation to new property failed!")
                        print("Skipping to next address to prevent duplicate extraction.")
                        continue
                        
                    print("Waiting for property details to load...")
                    page.wait_for_timeout(10000)
                    
                    print("Attempting to open contact details...")
                    try:
                        # Find the "Associated contacts" section strictly using substring regex
                        contacts_header = page.locator('text=/Associated contacts/i').first
                        
                        # Safely scroll into view
                        for _ in range(5):
                            if contacts_header.is_visible():
                                break
                            try:
                                contacts_header.scroll_into_view_if_needed(timeout=2000)
                                page.wait_for_timeout(500)
                                break
                            except:
                                page.mouse.wheel(0, 400)
                                page.wait_for_timeout(500)
                            
                        if contacts_header.is_visible():
                            header_text = contacts_header.inner_text()
                            match = re.search(r'\((\d+)\)', header_text)
                            num_contacts = int(match.group(1)) if match else 1
                            print(f"Found {num_contacts} associated contact(s).")
                        else:
                            print("No 'Associated contacts' section found on the page.")
                            safe_name = address.split(',')[0].replace(' ', '_').replace('#', '')
                            page.screenshot(path=rf"C:\buyers_information\error_{safe_name}.png")
                            num_contacts = 0
                            # Save to CSV immediately so this address is also recorded!
                            with open(csv_path, mode='a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([address, buyer_name, "No Associated Contacts Found", "", ""])
                                f.flush()
                                os.fsync(f.fileno())
                            print(f"--> [SAVED TO CSV] {address} -> No Associated Contacts Found")
                            
                        previous_data = None
                        for i in range(num_contacts):
                            print(f"Processing contact {i+1} of {num_contacts}...")
                            try:
                                contacts_header.scroll_into_view_if_needed(timeout=2000)
                                page.wait_for_timeout(300)
                            except:
                                pass
                            box = contacts_header.bounding_box()
                            if box:
                                # Click the contact card safely on the left side (avoiding phone icon on the right)
                                page.mouse.click(box["x"] + 50, box["y"] + 60)
                                print("Clicked contact card, waiting for panel...")
                                page.wait_for_timeout(4000)
                                
                                # Extract text from the page to find phones and emails
                                body_text = page.locator("body").inner_text()
                                
                                phone_pattern = r'\(\d{3}\)\s*\d{3}-\d{4}'
                                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                                
                                phones = list(set(re.findall(phone_pattern, body_text)))
                                emails = list(set(re.findall(email_pattern, body_text)))
                                
                                # Extract real owner name (Must be full name with First & Last name, no single-word icon text)
                                name = ""
                                
                                # Strategy 1: Look inside View Contact panel or body text directly after 'View Contact'
                                try:
                                    b_lines = [l.strip() for l in body_text.split('\n') if l.strip()]
                                    for idx, l in enumerate(b_lines):
                                        if 'view contact' in l.lower():
                                            for next_l in b_lines[idx+1:idx+6]:
                                                parts = next_l.split()
                                                if 2 <= len(parts) <= 4:
                                                    nl_low = next_l.lower()
                                                    if any(bad in nl_low for bad in ['view contact', 'contact', 'info', 'activity', 'mail', 'dealmachine', 'phone', 'email', 'address', 'details', 'real estate', 'investor', 'high earner', 'renter', 'portfolio', 'basic']):
                                                        continue
                                                    if any(ch in next_l for ch in ['@', '$', '(', ')', '%', ':', '/', '#']):
                                                        continue
                                                    if not re.search(r'\d', next_l):
                                                        name = next_l
                                                        break
                                            if name:
                                                break
                                except Exception:
                                    pass

                                # Strategy 2: Look for line directly above 'Likely Owner', 'Resident', 'Co-owner' on active card
                                if not name:
                                    try:
                                        b_lines = [l.strip() for l in body_text.split('\n') if l.strip()]
                                        for idx, l in enumerate(b_lines):
                                            if any(role in l.lower() for role in ['likely owner', 'resident', 'co-owner']):
                                                if idx > 0:
                                                    prev_l = b_lines[idx-1]
                                                    parts = prev_l.split()
                                                    if 2 <= len(parts) <= 4:
                                                        if not any(bad in prev_l.lower() for bad in ['associated', 'contact', 'est. value', 'mail', 'property', 'lead']):
                                                            if not re.search(r'\d', prev_l) and not any(ch in prev_l for ch in ['@', '$', '(', ')', '%', ':', '/', '#']):
                                                                name = prev_l
                                                                break
                                    except Exception:
                                        pass
                                
                                # Strategy 3: Find from active card container
                                if not name and contacts_header.is_visible():
                                    try:
                                        container = contacts_header.locator("xpath=../..")
                                        lines = [l.strip() for l in container.inner_text().split('\n') if l.strip()]
                                        for l in lines:
                                            parts = l.split()
                                            if 2 <= len(parts) <= 4:
                                                l_low = l.lower()
                                                if any(bad in l_low for bad in ['associated', 'contact', 'est. value', 'start mail', 'skip trace', 'view contact', 'why are there', 'more info', 'corporate owner', 'absentee owner']):
                                                    continue
                                                if any(ch in l for ch in ['@', '$', '(', ')', '%', ':', '/', '#']):
                                                    continue
                                                if not re.search(r'\d', l):
                                                    name = l
                                                    break
                                    except Exception:
                                        pass
                                
                                # Strategy 4: Fallback to buyer name from input CSV if available
                                if not name and buyer_name:
                                    name = buyer_name
                                
                                if not name:
                                    name = f"Owner {i+1}"
                                
                                print(f"--- Contact {i+1} Extracted ---")
                                print(f"Name: {name}")
                                print(f"Phones: {phones}")
                                print(f"Emails: {emails}")
                                print("---------------------------")
                                
                                current_data = f"{name}-{sorted(phones)}-{sorted(emails)}"
                                if previous_data and current_data == previous_data:
                                    print("Warning: Data is identical to the previous contact! The right arrow click likely failed.")
                                
                                # Avoid writing repeated empty buyer rows or empty Owner rows if no phones/emails
                                if not phones and not emails and (name == buyer_name or name.startswith("Owner ")) and i > 0:
                                    print(f"Skipping empty placeholder card {i+1} with no phones/emails.")
                                else:
                                    # Save to CSV ALWAYS with immediate disk sync
                                    with open(csv_path, mode='a', newline='', encoding='utf-8') as f:
                                        writer = csv.writer(f)
                                        writer.writerow([address, buyer_name, name, ", ".join(phones), ", ".join(emails)])
                                        f.flush()
                                        os.fsync(f.fileno())
                                    print(f"--> [SAVED TO CSV] {address} | {name} | {len(phones)} phone(s) | {len(emails)} email(s)")
                                previous_data = current_data
                                
                                # Close the panel to go back to the main property view
                                view_contact = page.locator('text="View Contact"').first
                                if view_contact.is_visible():
                                    print("Closing View Contact panel...")
                                    for offset in [30, 45, 60, 20, 75]:
                                        try:
                                            vc_box = view_contact.bounding_box()
                                            if vc_box:
                                                page.mouse.click(vc_box["x"] - offset, vc_box["y"] + vc_box["height"]/2)
                                                page.wait_for_timeout(800)
                                                if not page.locator('text="View Contact"').is_visible():
                                                    print("Panel closed successfully.")
                                                    break
                                        except:
                                            pass
                                    if page.locator('text="View Contact"').is_visible():
                                        print("Warning: Failed to close View Contact panel!")
                                        page.keyboard.press("Escape")
                                    page.wait_for_timeout(1000)
                                
                                # Press Escape only if View Contact panel is still visible
                                if page.locator('text="View Contact"').is_visible():
                                    page.keyboard.press("Escape")
                                    page.wait_for_timeout(500)
                                
                                # If there are more contacts, try to click the next arrow
                                if i < num_contacts - 1:
                                    print("Moving to next contact...")
                                    try:
                                        container = contacts_header.locator("xpath=../..")
                                        old_text = container.inner_text()
                                        
                                        # Strategy 1: Click the actual DealMachine arrow icon directly
                                        arrow_icons = container.locator('i:has-text("keyboard_arrow_right"), i:has-text("chevron_right"), [class*="arrow_right"]').all()
                                        if arrow_icons:
                                            print(f"Found {len(arrow_icons)} arrow icon(s). Clicking the last one...")
                                            try:
                                                arrow_icons[-1].click(force=True, timeout=2000)
                                                page.wait_for_timeout(1000)
                                            except:
                                                pass
                                        
                                        # Strategy 2: Keyboard ArrowRight
                                        if container.inner_text() == old_text and box:
                                            print("Trying ArrowRight...")
                                            page.mouse.click(box["x"] + 150, box["y"] + 60)
                                            page.keyboard.press("ArrowRight")
                                            page.wait_for_timeout(1000)
                                            
                                        # Strategy 3: Swipe (Drag mouse right to left)
                                        if container.inner_text() == old_text and box:
                                            print("Trying Mouse Swipe...")
                                            page.mouse.move(box["x"] + 220, box["y"] + 60)
                                            page.mouse.down()
                                            page.wait_for_timeout(100)
                                            page.mouse.move(box["x"] + 40, box["y"] + 60, steps=20)
                                            page.wait_for_timeout(100)
                                            page.mouse.up()
                                            page.wait_for_timeout(1000)
                                            
                                        # Strategy 4: Coordinate Click on arrow button
                                        if container.inner_text() == old_text and box:
                                            print("Trying Coordinate Click on > arrow...")
                                            page.mouse.click(box["x"] + 240, box["y"] + 110)
                                            page.wait_for_timeout(1000)
                                    except Exception as e:
                                        print(f"Navigation failed: {e}")
                                    
                                    page.wait_for_timeout(1500)

                    except Exception as e:
                        print(f"Error extracting contact info: {e}")
                        
                    print("Finished extracting all contacts for this property.")
                    print("Closing property panel to return to a clean state...")
                    try:
                        # Try to find the property title to click the 'X' next to it
                        prop_short = address.split(',')[0].strip()
                        if '#' in prop_short:
                            prop_short = prop_short.split('#')[0].strip()
                            
                        prop_title = page.locator(f'text="{prop_short}"').first
                        if prop_title.is_visible():
                            pt_box = prop_title.bounding_box()
                            if pt_box:
                                # The X is usually 30-50 pixels to the left of the title
                                page.mouse.click(pt_box["x"] - 40, pt_box["y"] + pt_box["height"]/2)
                                page.wait_for_timeout(1000)
                    except:
                        pass
                        
                    # Foolproof fallback: if the property panel didn't close (URL still has property id), force reload!
                    if "property" in page.url:
                        print("Panel did not close gracefully. Forcing reload to dashboard...")
                        page.goto(LOGIN_URL)
                        page.wait_for_timeout(5000)
                        
                    page.wait_for_timeout(1500)

                else:
                    print("Search bar not visible on the page! Make sure you are on the dashboard.")
                    break
                    
            except Exception as e:
                print(f"Error processing {address}: {e}")
                if "Target page, context or browser has been closed" in str(e) or (page and page.is_closed()):
                    print("Browser was closed. Exiting.")
                    break
        print("Closing browser...")
        browser.close()

if __name__ == "__main__":
    run()
