import csv
import re
import os

INPUT_DISPO_CSV = r'C:\buyers_information\Dispo Board Competitor Buyers (3).csv'
EXTRACTED_CSV = r'C:\buyers_information\Extracted_Contacts_Cleaned.csv'
OUTPUT_CSV = r'C:\buyers_information\Final_Prioritized_Buyers_List.csv'

# Known Nevada SOS Verified Active Officers / Managing Members mapping
# (Built from NV SOS Portal & Business Entity filings)
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

def clean_phone(phone_str):
    if not phone_str:
        return []
    return [p.strip() for p in phone_str.split(',') if p.strip()]

def clean_email(email_str):
    if not email_str:
        return []
    return [e.strip() for e in email_str.split(',') if e.strip()]

def normalize_name(name):
    if not name:
        return ""
    # Strip suffixes, commas
    parts = re.split(r'[, ]+', name.strip())
    # Return lowercase alphanumeric
    return " ".join(parts).lower()

def run_processing():
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
                    'buyer_entity': row.get('Buyer Name / LLC', '').strip(),
                    'owner_name': row.get('Owner Name', '').strip(),
                    'phones': clean_phone(row.get('Phones', '')),
                    'emails': clean_email(row.get('Emails', ''))
                })

    print("Processing Dispo Board Competitor Buyers...")
    output_rows = []
    
    with open(INPUT_DISPO_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Skip headers
        next(reader, None)
        next(reader, None)
        
        for idx, row in enumerate(reader, start=3):
            if not row or not row[0].strip():
                continue
            
            prop_addr = row[0].strip()
            buyer_entity = row[12].strip() if len(row) > 12 else ""
            buyer_name = row[13].strip() if len(row) > 13 else ""
            buyer_entity_2 = row[14].strip() if len(row) > 14 else ""
            buyer_name_2 = row[15].strip() if len(row) > 15 else ""
            
            # Determine Target Entity / Individual
            target_entity = buyer_entity or buyer_entity_2
            target_individual = buyer_name or buyer_name_2
            
            verified_person = ""
            role_label = ""
            officers_list = []
            
            if target_entity and target_entity.upper() in NV_SOS_MAPPING:
                info = NV_SOS_MAPPING[target_entity.upper()]
                verified_person = info['primary_owner']
                role_label = f"Active {info['title']}"
                officers_list = [normalize_name(o) for o in info['officers']]
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
            
            # Now let's classify phones and emails for this property
            dm_records = dm_contacts_by_address.get(prop_addr, [])
            
            p1_phones = [] # Primary Owner Mobiles
            p2_phones = [] # Secondary Owner Mobiles / Alt
            p3_phones = [] # Partners / Office Lines
            p4_phones = [] # Relatives / Co-members
            p5_phones = [] # Tenants / Residents
            p6_phones = [] # Sellers / Others
            
            owner_emails = []
            other_emails = []
            
            # Check if any DM record matches the verified person or officers
            for rec in dm_records:
                rec_name = rec['owner_name']
                rec_norm = normalize_name(rec_name)
                phones = rec['phones']
                emails = rec['emails']
                
                is_officer = any(off in rec_norm or rec_norm in off for off in officers_list) if officers_list else False
                
                # Check if same surname as verified person
                v_parts = verified_person.split()
                last_name = v_parts[-1].lower() if v_parts else ""
                is_relative = (last_name in rec_norm) and not is_officer if last_name else False
                
                if is_officer:
                    # This is the verified owner or active partner!
                    if not p1_phones and phones:
                        p1_phones.append(f"{phones[0]}")
                        if len(phones) > 1:
                            p2_phones.append(f"{phones[1]}")
                        if len(phones) > 2:
                            p3_phones.extend(phones[2:])
                    else:
                        p3_phones.extend([f"{p} ({rec_name})" for p in phones])
                    owner_emails.extend(emails)
                elif is_relative:
                    p4_phones.extend([f"{p} ({rec_name} - Relative)" for p in phones])
                    other_emails.extend(emails)
                else:
                    # Likely Tenant or Previous Seller
                    if "No Associated Contacts" in rec_name:
                        continue
                    p5_phones.extend([f"{p} ({rec_name} - Tenant/Res)" for p in phones])
                    other_emails.extend(emails)
            
            # Format row
            phone_1 = p1_phones[0] if p1_phones else (p5_phones[0] if p5_phones and not target_entity else "")
            phone_2 = p2_phones[0] if p2_phones else (p1_phones[1] if len(p1_phones) > 1 else "")
            phone_3 = ", ".join(p3_phones) if p3_phones else ""
            phone_4 = ", ".join(p4_phones) if p4_phones else ""
            phone_5 = ", ".join(p5_phones) if p5_phones else ""
            phone_6 = ", ".join(p6_phones) if p6_phones else ""
            
            owner_email_str = ", ".join(list(dict.fromkeys(owner_emails)))
            other_email_str = ", ".join(list(dict.fromkeys(other_emails)))
            
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
                owner_email_str,
                other_email_str
            ])
            
    print(f"Writing {len(output_rows)} prioritized rows to {OUTPUT_CSV}...")
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
        
    print("Done generating prioritized buyers list!")

if __name__ == '__main__':
    run_processing()
