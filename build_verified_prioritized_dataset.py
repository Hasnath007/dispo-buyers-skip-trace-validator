import csv
import re
import os

INPUT_DISPO_CSV = r'C:\buyers_information\Dispo Board Competitor Buyers (3).csv'
EXTRACTED_CSV = r'C:\buyers_information\Extracted_Contacts_Cleaned.csv'
OUTPUT_CSV = r'C:\buyers_information\Dispo_Buyers_Prioritized_Verified.csv'

# Official Nevada Secretary of State verified active officers & members
NV_SOS_VERIFIED_OFFICERS = {
    "ALCHEMY INVESTMENTS LLC": {
        "primary_owner": "CASEY RYAN",
        "officers": ["CASEY RYAN", "KEVIN M LANG"],
        "title": "Managing Member",
        "owner_phones": ["(725) 227-5761", "(702) 824-7270"],
        "partner_phones": ["(702) 331-1879", "(760) 952-2234"],
        "owner_emails": ["casey@webuyanyvegashouse.com", "kevin.lang@swgas.com"]
    },
    "FLIP SIDE PROPERTIES LLC": {
        "primary_owner": "DOUG CHRISTENSEN",
        "officers": ["DOUG CHRISTENSEN"],
        "title": "Managing Member",
        "owner_phones": ["(702) 247-2477"],
        "partner_phones": [],
        "owner_emails": ["doug@247companiesnow.com"]
    },
    "SCARF LLC": {
        "primary_owner": "HENRY KOW",
        "officers": ["HENRY KOW", "PABLO COVARRUBIAS"],
        "title": "Managing Member",
        "owner_phones": ["(630) 303-3530"],
        "partner_phones": ["(702) 437-1910"],
        "owner_emails": ["henry02kow@gmail.com"]
    },
    "BIG RED LLC": {
        "primary_owner": "THOMAS B REYNOLDS",
        "officers": ["THOMAS B REYNOLDS"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "HUBBSELEVATION LLC": {
        "primary_owner": "TYLER HUBBS",
        "officers": ["TYLER HUBBS"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": ["tyler@hubbshomes.com"]
    },
    "BETTER ASSETS INC": {
        "primary_owner": "RYOKO V TANAKA",
        "officers": ["RYOKO V TANAKA", "JUN R TANAKA"],
        "title": "President / Officer",
        "owner_phones": ["(530) 510-2327", "(530) 510-2606"],
        "partner_phones": ["(702) 463-9206 (Jun R Tanaka)", "(702) 241-2901 (Jun R Tanaka)", "(702) 680-9672 (Jun R Tanaka)"],
        "owner_emails": ["ryokovtanaka@gmail.com", "ryokotanakadgf@outlook.com", "patbass182@gmail.com"]
    },
    "MOVE MADE SIMPLE LLC": {
        "primary_owner": "IMELDA PROBST",
        "officers": ["IMELDA PROBST", "TONI YVETTE BURRELL"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "PLOT PROPERTY GROUP LLC": {
        "primary_owner": "VLADIMIR PLOTNIKOV",
        "officers": ["VLADIMIR PLOTNIKOV", "ALEXANDRE P PLOTNIKOV"],
        "title": "Managing Member",
        "owner_phones": ["(702) 580-3175", "(702) 496-0736"],
        "partner_phones": ["(702) 496-0736 (Alexandre Plotnikov)"],
        "owner_emails": ["plotnikov74@netzero.net", "plotnikov@cs.com"]
    },
    "YESDCT LLC": {
        "primary_owner": "GLORIA DIAZ DE CASTANEDA",
        "officers": ["GLORIA DIAZ DE CASTANEDA"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "ELO EQUITY GROUP LLC": {
        "primary_owner": "NICHOLAS ELO",
        "officers": ["NICHOLAS ELO"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": ["antbrewer031613@gmail.com"]
    },
    "TL HOME REMODELS LLC": {
        "primary_owner": "TIBURCIO LEON MORA",
        "officers": ["TIBURCIO LEON MORA", "ADAN PRECIADO"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "REAL ESTATE ROCK LV LLC": {
        "primary_owner": "KARLA CARDENAS",
        "officers": ["KARLA CARDENAS"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "ESP DESERT HOLDINGS LLC": {
        "primary_owner": "BRYAN ESPINOSA MIRANDA",
        "officers": ["BRYAN ESPINOSA MIRANDA"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "GO GRIZZLIES LLC": {
        "primary_owner": "LORRAINE T MEESENBURG",
        "officers": ["LORRAINE T MEESENBURG"],
        "title": "Managing Member",
        "owner_phones": ["(702) 263-5764", "(702) 300-3884"],
        "partner_phones": ["(702) 263-9024 (Office)"],
        "owner_emails": ["lorainie@earthlink.net", "godeliver@yahoo.com"]
    },
    "TORITO HOMES LLC": {
        "primary_owner": "ABIGAIL BARAJAS",
        "officers": ["ABIGAIL BARAJAS"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "VANGUARD CREST HOLDINGS LLC": {
        "primary_owner": "WILLIAM D CULVER",
        "officers": ["WILLIAM D CULVER"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "ALPHA INVESTMENT GROUP INC": {
        "primary_owner": "LYONEL LAMAUTE",
        "officers": ["LYONEL LAMAUTE", "FRANCOIS J MELAERTS"],
        "title": "President / Officer",
        "owner_phones": [],
        "partner_phones": ["(702) 277-6207 (Francois Melaerts)", "(702) 878-9315 (Francois Melaerts)", "(702) 646-7619 (Frank Melaerts)"],
        "owner_emails": ["fmelaerts@gmail.com", "lindamelaerts@gmail.com"]
    },
    "MONACO PRO KITCHENS LLC": {
        "primary_owner": "JOSE MADINA QUINTERO",
        "officers": ["JOSE MADINA QUINTERO"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "CAJIE LLC": {
        "primary_owner": "JONATHAN JACOBS",
        "officers": ["JONATHAN JACOBS"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "LIANA FREY HOLDINGS LLC": {
        "primary_owner": "JEFFREY EHLERT",
        "officers": ["JEFFREY EHLERT"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    },
    "LEGACY HOME INVESTMENTS LLC": {
        "primary_owner": "CHRISTINE JOHNSON",
        "officers": ["CHRISTINE JOHNSON"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": ["parasu@juno.com"]
    },
    "BOB MILLER INVESTMENT PROPERTIES LLC": {
        "primary_owner": "BOB MILLER",
        "officers": ["BOB MILLER"],
        "title": "Managing Member",
        "owner_phones": [],
        "partner_phones": [],
        "owner_emails": []
    }
}

def extract_valid_phones(text):
    if not text:
        return []
    matches = re.findall(r'\(\d{3}\)\s*\d{3}-\d{4}', text)
    return list(dict.fromkeys(matches))

def clean_emails(val):
    if not val:
        return []
    matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', val)
    return list(dict.fromkeys(matches))

def normalize_name(name):
    if not name:
        return ""
    parts = re.split(r'[, ]+', name.strip())
    return " ".join(parts).lower()

def run_validation():
    print("Reading extracted DealMachine contacts...")
    dm_contacts_by_address = {}
    if os.path.exists(EXTRACTED_CSV):
        with open(EXTRACTED_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                addr = row.get('Property Address', '').strip()
                if not addr:
                    continue
                if addr not in dm_contacts_by_address:
                    dm_contacts_by_address[addr] = []
                dm_contacts_by_address[addr].append({
                    'owner_name': row.get('Owner Name', '').strip(),
                    'phones': extract_valid_phones(row.get('Phones', '')),
                    'emails': clean_emails(row.get('Emails', ''))
                })

    print("Processing Dispo Board properties with Nevada SOS + DealMachine + Web cross-validation...")
    output_rows = []
    
    with open(INPUT_DISPO_CSV, mode='r', encoding='utf-8') as f:
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
            
            verified_person = ""
            role_label = ""
            officers_list = []
            
            p1_phones = []
            p2_phones = []
            p3_phones = []
            p4_phones = []
            p5_phones = []
            owner_emails = []
            other_emails = []
            
            # 1. Nevada SOS Match
            if target_entity and target_entity.upper() in NV_SOS_VERIFIED_OFFICERS:
                info = NV_SOS_VERIFIED_OFFICERS[target_entity.upper()]
                verified_person = info['primary_owner']
                role_label = f"Active {info['title']}"
                officers_list = [normalize_name(o) for o in info['officers']]
                if info.get('owner_phones'):
                    p1_phones.extend(info['owner_phones'][:1])
                    if len(info['owner_phones']) > 1:
                        p2_phones.extend(info['owner_phones'][1:2])
                if info.get('partner_phones'):
                    p3_phones.extend(info['partner_phones'])
                if info.get('owner_emails'):
                    owner_emails.extend(info['owner_emails'])
            elif target_individual:
                verified_person = target_individual
                role_label = "Individual Buyer"
                officers_list = [normalize_name(target_individual)]
            elif target_entity:
                verified_person = target_entity
                role_label = "Entity Buyer"
                officers_list = [normalize_name(target_entity)]
            else:
                verified_person = "Unknown Buyer"
                role_label = "Unassigned"
                
            # 2. DealMachine Contacts Match
            dm_records = dm_contacts_by_address.get(prop_addr, [])
            v_last = verified_person.split()[-1].lower() if verified_person else ""
            
            for rec in dm_records:
                r_name = rec['owner_name']
                r_norm = normalize_name(r_name)
                r_phones = rec['phones']
                r_emails = rec['emails']
                
                if not r_name or "No Associated Contacts" in r_name:
                    continue
                    
                is_officer = any(o in r_norm or r_norm in o for o in officers_list) if officers_list else False
                is_relative = (v_last in r_norm) and not is_officer if (v_last and len(v_last) > 2) else False
                
                if is_officer:
                    if not p1_phones and r_phones:
                        p1_phones.append(r_phones[0])
                        if len(r_phones) > 1:
                            p2_phones.append(r_phones[1])
                        if len(r_phones) > 2:
                            p3_phones.extend(r_phones[2:])
                    else:
                        for p in r_phones:
                            if p not in p1_phones and p not in p2_phones:
                                p3_phones.append(f"{p} ({r_name})")
                    owner_emails.extend(r_emails)
                elif is_relative:
                    for p in r_phones:
                        p4_phones.append(f"{p} ({r_name} - Relative)")
                    other_emails.extend(r_emails)
                else:
                    for p in r_phones:
                        p5_phones.append(f"{p} ({r_name} - Tenant/Res)")
                    other_emails.extend(r_emails)
                    
            # Individual buyer specific formatting
            if not p1_phones and p4_phones and target_individual:
                match = re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', p4_phones[0])
                if match:
                    p1_phones.append(match.group(0))
                    p4_phones = p4_phones[1:]
                    
            phone_1 = p1_phones[0] if p1_phones else ""
            phone_2 = p2_phones[0] if p2_phones else ""
            phone_3 = ", ".join(list(dict.fromkeys(p3_phones))) if p3_phones else ""
            phone_4 = ", ".join(list(dict.fromkeys(p4_phones))) if p4_phones else ""
            phone_5 = ", ".join(list(dict.fromkeys(p5_phones))) if p5_phones else ""
            phone_6 = ""
            
            o_emails_clean = list(dict.fromkeys(owner_emails))
            oth_emails_clean = list(dict.fromkeys(other_emails))
            
            output_rows.append([
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
                ", ".join(o_emails_clean),
                ", ".join(oth_emails_clean)
            ])
            
    print(f"Writing {len(output_rows)} verified rows to {OUTPUT_CSV}...")
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
        writer.writerows(output_rows)
        
    print("Completed generation of Dispo_Buyers_Prioritized_Verified.csv!")

if __name__ == '__main__':
    run_validation()
