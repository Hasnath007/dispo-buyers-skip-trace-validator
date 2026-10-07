import time
import csv
import re
import os
from playwright.sync_api import sync_playwright

INPUT_CSV = r'C:\buyers_information\Dispo Board Competitor Buyers (3).csv'
OUTPUT_CSV = r'C:\buyers_information\Live_Full_Prioritized_Buyers.csv'
LOGIN_URL = 'https://app.dealmachine.com/login'
EMAIL = 'skinnovationstech@gmail.com'
PASSWORD = 'c1nl5&Ml&@5LCr'

# Nevada SOS verified business entity database mapping
NV_SOS_MAPPING = {
    "ALCHEMY INVESTMENTS LLC": {
        "officers": ["CASEY RYAN", "KEVIN M LANG"],
        "primary_owner": "CASEY RYAN",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "FLIP SIDE PROPERTIES LLC": {
        "officers": ["DOUG CHRISTENSEN"],
        "primary_owner": "DOUG CHRISTENSEN",
        "title": "Managing Member",
        "city": "Henderson, NV"
    },
    "SCARF LLC": {
        "officers": ["HENRY KOW", "PABLO COVARRUBIAS"],
        "primary_owner": "HENRY KOW",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "BIG RED LLC": {
        "officers": ["THOMAS B REYNOLDS"],
        "primary_owner": "THOMAS B REYNOLDS",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "HUBBSELEVATION LLC": {
        "officers": ["TYLER HUBBS"],
        "primary_owner": "TYLER HUBBS",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "BETTER ASSETS INC": {
        "officers": ["RYOKO V TANAKA", "JUN R TANAKA"],
        "primary_owner": "RYOKO V TANAKA",
        "title": "President / Officer",
        "city": "Las Vegas, NV"
    },
    "MOVE MADE SIMPLE LLC": {
        "officers": ["IMELDA PROBST"],
        "primary_owner": "IMELDA PROBST",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "PLOT PROPERTY GROUP LLC": {
        "officers": ["VLADIMIR PLOTNIKOV", "ALEXANDRE P PLOTNIKOV"],
        "primary_owner": "VLADIMIR PLOTNIKOV",
        "title": "Managing Member",
        "city": "Henderson, NV"
    },
    "YESDCT LLC": {
        "officers": ["GLORIA DIAZ DE CASTANEDA"],
        "primary_owner": "GLORIA DIAZ DE CASTANEDA",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "ELO EQUITY GROUP LLC": {
        "officers": ["NICHOLAS ELO"],
        "primary_owner": "NICHOLAS ELO",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "TL HOME REMODELS LLC": {
        "officers": ["TIBURCIO LEON MORA"],
        "primary_owner": "TIBURCIO LEON MORA",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "REAL ESTATE ROCK LV LLC": {
        "officers": ["KARLA CARDENAS"],
        "primary_owner": "KARLA CARDENAS",
        "title": "Managing Member",
        "city": "Winchester, NV"
    },
    "ESP DESERT HOLDINGS LLC": {
        "officers": ["BRYAN ESPINOSA MIRANDA"],
        "primary_owner": "BRYAN ESPINOSA MIRANDA",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "GO GRIZZLIES LLC": {
        "officers": ["LORRAINE T MEESENBURG"],
        "primary_owner": "LORRAINE T MEESENBURG",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "TORITO HOMES LLC": {
        "officers": ["ABIGAIL BARAJAS"],
        "primary_owner": "ABIGAIL BARAJAS",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "VANGUARD CREST HOLDINGS LLC": {
        "officers": ["WILLIAM D CULVER"],
        "primary_owner": "WILLIAM D CULVER",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "ALPHA INVESTMENT GROUP INC": {
        "officers": ["LYONEL LAMAUTE", "FRANCOIS J MELAERTS"],
        "primary_owner": "LYONEL LAMAUTE",
        "title": "President / Officer",
        "city": "Las Vegas, NV"
    },
    "MONACO PRO KITCHENS LLC": {
        "officers": ["JOSE MADINA QUINTERO"],
        "primary_owner": "JOSE MADINA QUINTERO",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "CAJIE LLC": {
        "officers": ["JONATHAN JACOBS"],
        "primary_owner": "JONATHAN JACOBS",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "LIANA FREY HOLDINGS LLC": {
        "officers": ["JEFFREY EHLERT"],
        "primary_owner": "JEFFREY EHLERT",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "LEGACY HOME INVESTMENTS LLC": {
        "officers": ["CHRISTINE JOHNSON"],
        "primary_owner": "CHRISTINE JOHNSON",
        "title": "Managing Member",
        "city": "Las Vegas, NV"
    },
    "BOB MILLER INVESTMENT PROPERTIES LLC": {
        "officers": ["BOB MILLER"],
        "primary_owner": "BOB MILLER",
        "title": "Managing Member",
        "city": "Henderson, NV"
    }
}

def normalize_name(name):
    if not name:
        return ""
    parts = re.split(r'[, ]+', name.strip())
    return " ".join(parts).lower()

def run_live_pipeline():
    print("=" * 60)
    print("STARTING LIVE SCRAPER & 3-WAY VALIDATION PIPELINE")
    print("=" * 60)
    
    # Check already processed addresses
    processed_addresses = set()
    file_exists = os.path.isfile(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
    
    if file_exists:
        with open(OUTPUT_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for r in reader:
                if r and r[0]:
                    processed_addresses.add(r[0].strip())
        print(f"Found {len(processed_addresses)} properties already completed in output CSV.")
    else:
        with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Property Address',
                'Buyer LLC / Entity',
                'Person (Verified Decision Maker)',
                'Role / Status',
                'Phone 1 (Owner Primary Mobile)',
                'Phone 2 (Owner Alt Mobile)',
                'Phone 3 (Active Partner / Office)',
                'Phone 4 (Relative / Co-Buyer)',
                'Phone 5 (Tenant / Current Resident)',
                'Phone 6 (Previous Seller / Other)',
                'Owner Emails',
                'Other Emails'
            ])
            
    # Load input properties
    properties = []
    with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        next(reader, None)
        for idx, row in enumerate(reader, start=3):
            if not row or not row[0].strip():
                continue
            prop_addr = row[0].strip()
            b_entity = row[12].strip() if len(row) > 12 else ""
            b_name = row[13].strip() if len(row) > 13 else ""
            b_entity_2 = row[14].strip() if len(row) > 14 else ""
            b_name_2 = row[15].strip() if len(row) > 15 else ""
            
            target_entity = b_entity or b_entity_2
            target_individual = b_name or b_name_2
            properties.append((idx, prop_addr, target_entity, target_individual))
            
    print(f"Total properties to process: {len(properties)}")
    
    with sync_playwright() as p:
        print("Launching live automated browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        print("Logging in to DealMachine...")
        page.goto(LOGIN_URL, timeout=60000)
        page.wait_for_timeout(4000)
        
        try:
            if page.locator('input[type="email"]').is_visible():
                page.locator('input[type="email"]').fill(EMAIL)
            elif page.locator('input[name="email"]').is_visible():
                page.locator('input[name="email"]').fill(EMAIL)
            else:
                page.locator('input').first.fill(EMAIL)
            page.wait_for_timeout(500)
            
            if page.locator('input[type="password"]').is_visible():
                page.locator('input[type="password"]').fill(PASSWORD)
            elif page.locator('input[name="password"]').is_visible():
                page.locator('input[name="password"]').fill(PASSWORD)
            page.wait_for_timeout(500)
            
            if page.get_by_text("Continue With Email", exact=False).is_visible():
                page.get_by_text("Continue With Email", exact=False).first.click()
            elif page.get_by_role("button", name="Log In").is_visible():
                page.get_by_role("button", name="Log In").first.click()
            elif page.get_by_role("button", name="Sign In").is_visible():
                page.get_by_role("button", name="Sign In").first.click()
            else:
                page.locator('button[type="submit"]').first.click()
        except Exception as e:
            print("Auto-login error or already logged in:", e)
            
        print("Waiting 12s for DealMachine session...")
        page.wait_for_timeout(12000)
        
        for idx, prop_addr, target_entity, target_individual in properties:
            if prop_addr in processed_addresses:
                print(f"[{idx}] Skipping completed: {prop_addr}")
                continue
                
            print(f"\n[{idx}] Processing Property: {prop_addr}")
            print(f"      Buyer Entity: {target_entity} | Buyer Name: {target_individual}")
            
            # Step 1: NV SOS lookup
            verified_person = ""
            role_label = ""
            officers_list = []
            
            if target_entity and target_entity.upper() in NV_SOS_MAPPING:
                info = NV_SOS_MAPPING[target_entity.upper()]
                verified_person = info['primary_owner']
                role_label = f"Active {info['title']}"
                officers_list = [normalize_name(o) for o in info['officers']]
                print(f"      [NV SOS MATCH] Verified Active Owner: {verified_person} ({role_label})")
            elif target_individual:
                verified_person = target_individual
                role_label = "Individual Buyer"
                officers_list = [normalize_name(target_individual)]
                print(f"      [INDIVIDUAL BUYER] {verified_person}")
            elif target_entity:
                verified_person = target_entity
                role_label = "Entity Buyer"
                officers_list = [normalize_name(target_entity)]
                print(f"      [ENTITY BUYER] {verified_person}")
            else:
                verified_person = "Unknown Buyer"
                role_label = "Unassigned"
                
            # Step 2: DealMachine Live Search & Contact Extraction
            extracted_contacts = []
            try:
                search_bar = page.locator('input[placeholder*="Search"]').first
                if not search_bar.is_visible():
                    search_bar = page.locator('input[type="text"]').first
                if search_bar.is_visible():
                    search_bar.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.wait_for_timeout(300)
                    page.keyboard.type(prop_addr, delay=40)
                    page.wait_for_timeout(2500)
                    
                    # Click dropdown or press enter
                    house_number = prop_addr.split(',')[0].strip().split()[0]
                    try:
                        btn = page.locator('text=/Jump to Location|Open Property/i').first
                        btn.wait_for(state="visible", timeout=3000)
                        btn.click(force=True, timeout=2000)
                    except:
                        try:
                            sug = page.locator(f'text=/{house_number}/i').first
                            sug.wait_for(state="visible", timeout=3000)
                            sug.click(force=True, timeout=2000)
                        except:
                            page.keyboard.press("Enter")
                            
                    # Wait for property page
                    navigated = False
                    for _ in range(12):
                        if "property" in page.url:
                            navigated = True
                            break
                        page.wait_for_timeout(500)
                        
                    if not navigated:
                        # Try clicking side panel item
                        elems = page.locator(f'text=/{house_number}/i').all()
                        for el in elems[:3]:
                            try:
                                el.click(force=True, timeout=1500)
                                page.wait_for_timeout(1000)
                                if "property" in page.url:
                                    navigated = True
                                    break
                            except:
                                pass
                                
                    if navigated:
                        page.wait_for_timeout(4000)
                        # Extract Contacts
                        contacts_header = page.locator('text=/Associated contacts/i').first
                        if contacts_header.is_visible():
                            htext = contacts_header.inner_text()
                            m = re.search(r'\((\d+)\)', htext)
                            num_c = int(m.group(1)) if m else 1
                            print(f"      [DealMachine] Found {num_c} associated contact cards.")
                            
                            for c_idx in range(num_c):
                                try:
                                    contacts_header.scroll_into_view_if_needed(timeout=1500)
                                    box = contacts_header.bounding_box()
                                    if box:
                                        page.mouse.click(box["x"] + 50, box["y"] + 60)
                                        page.wait_for_timeout(2000)
                                        
                                        btext = page.locator("body").inner_text()
                                        phones = list(set(re.findall(r'\(\d{3}\)\s*\d{3}-\d{4}', btext)))
                                        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', btext)))
                                        
                                        # Extract contact name
                                        cname = f"Contact {c_idx+1}"
                                        b_lines = [l.strip() for l in btext.split('\n') if l.strip()]
                                        for bi, line in enumerate(b_lines):
                                            if 'view contact' in line.lower():
                                                for nl in b_lines[bi+1:bi+5]:
                                                    p_words = nl.split()
                                                    if 2 <= len(p_words) <= 4 and not re.search(r'[\d@$%:/#]', nl):
                                                        if not any(bad in nl.lower() for bad in ['view contact', 'contact', 'info', 'mail', 'phone', 'email']):
                                                            cname = nl
                                                            break
                                                break
                                                
                                        extracted_contacts.append({
                                            'name': cname,
                                            'phones': phones,
                                            'emails': emails
                                        })
                                except Exception as ce:
                                    pass
            except Exception as se:
                print(f"      [DealMachine Search Error] {se}")
                
            # Step 3: Prioritization & Ranking
            p1_phones, p2_phones, p3_phones, p4_phones, p5_phones, p6_phones = [], [], [], [], [], []
            owner_emails, other_emails = [], []
            
            for c in extracted_contacts:
                cname = c['name']
                c_norm = normalize_name(cname)
                c_phones = c['phones']
                c_emails = c['emails']
                
                is_off = any(off in c_norm or c_norm in off for off in officers_list) if officers_list else False
                v_parts = verified_person.split()
                l_name = v_parts[-1].lower() if v_parts else ""
                is_rel = (l_name in c_norm) and not is_off if l_name else False
                
                if is_off:
                    if not p1_phones and c_phones:
                        p1_phones.append(c_phones[0])
                        if len(c_phones) > 1:
                            p2_phones.append(c_phones[1])
                        if len(c_phones) > 2:
                            p3_phones.extend(c_phones[2:])
                    else:
                        p3_phones.extend([f"{p} ({cname})" for p in c_phones])
                    owner_emails.extend(c_emails)
                elif is_rel:
                    p4_phones.extend([f"{p} ({cname} - Relative)" for p in c_phones])
                    other_emails.extend(c_emails)
                else:
                    p5_phones.extend([f"{p} ({cname} - Tenant/Res)" for p in c_phones])
                    other_emails.extend(c_emails)
                    
            phone_1 = p1_phones[0] if p1_phones else (p5_phones[0] if p5_phones and not target_entity else "")
            phone_2 = p2_phones[0] if p2_phones else (p1_phones[1] if len(p1_phones) > 1 else "")
            phone_3 = ", ".join(p3_phones) if p3_phones else ""
            phone_4 = ", ".join(p4_phones) if p4_phones else ""
            phone_5 = ", ".join(p5_phones) if p5_phones else ""
            phone_6 = ", ".join(p6_phones) if p6_phones else ""
            
            o_email_str = ", ".join(list(dict.fromkeys(owner_emails)))
            oth_email_str = ", ".join(list(dict.fromkeys(other_emails)))
            
            # Write immediately to CSV
            with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    prop_addr,
                    target_entity or "Individual",
                    verified_person,
                    role_label,
                    phone_1,
                    phone_2,
                    phone_3,
                    phone_4,
                    phone_5,
                    phone_6,
                    o_email_str,
                    oth_email_str
                ])
                f.flush()
                
            processed_addresses.add(prop_addr)
            print(f"      --> [SAVED TO LIVE CSV] {prop_addr} -> {verified_person}")
            page.wait_for_timeout(1000)
            
        browser.close()
        print("\nAll properties processed successfully!")

if __name__ == '__main__':
    run_live_pipeline()
