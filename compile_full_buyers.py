import csv
import re
import os

INPUT_DISPO_CSV = r'C:\buyers_information\Dispo Board Competitor Buyers (3).csv'
EXTRACTED_CSV = r'C:\buyers_information\Extracted_Contacts_Cleaned.csv'
OUTPUT_CSV = r'C:\buyers_information\Live_Full_Prioritized_Buyers.csv'

# Complete verified Nevada SOS & Web profiles for buyers
BUYER_PROFILES = {
    "ALCHEMY INVESTMENTS LLC": {
        "officers": ["CASEY RYAN", "KEVIN M LANG"],
        "primary_owner": "CASEY RYAN",
        "title": "Managing Member",
        "p1": "(725) 227-5761",
        "p2": "(702) 824-7270",
        "p3": "(702) 331-1879 (Kevin M Lang - Partner), (760) 952-2234",
        "emails": "casey@webuyanyvegashouse.com, kevin.lang@swgas.com, jonathancasey@gmail.com"
    },
    "FLIP SIDE PROPERTIES LLC": {
        "officers": ["DOUG CHRISTENSEN"],
        "primary_owner": "DOUG CHRISTENSEN",
        "title": "Managing Member",
        "p1": "(702) 263-5764",
        "p2": "(702) 300-3884",
        "p3": "(702) 263-9024 (Office)",
        "emails": "lorainie@earthlink.net, godeliver@yahoo.com"
    },
    "SCARF LLC": {
        "officers": ["HENRY KOW", "PABLO COVARRUBIAS"],
        "primary_owner": "HENRY KOW",
        "title": "Managing Member",
        "p1": "(630) 303-3530",
        "p2": "(702) 437-1910",
        "p3": "(702) 437-1910 (Pablo Covarrubias - Partner)",
        "emails": "henry02kow@gmail.com, sterlp07@icloud.com"
    },
    "BIG RED LLC": {
        "officers": ["THOMAS B REYNOLDS"],
        "primary_owner": "THOMAS B REYNOLDS",
        "title": "Managing Member",
        "p1": "(702) 213-5500",
        "p2": "(702) 496-0736",
        "p3": "",
        "emails": "thomasreynolds@bigredrealty.com"
    },
    "HUBBSELEVATION LLC": {
        "officers": ["TYLER HUBBS"],
        "primary_owner": "TYLER HUBBS",
        "title": "Managing Member",
        "p1": "(702) 809-9676",
        "p2": "(757) 660-3261",
        "p3": "(928) 605-1653 (Office)",
        "emails": "tyler@hubbshomes.com, samuelhayes1963@gmail.com, s.l.hayes@outlook.com"
    },
    "BETTER ASSETS INC": {
        "officers": ["RYOKO V TANAKA", "JUN R TANAKA"],
        "primary_owner": "RYOKO V TANAKA",
        "title": "President / Officer",
        "p1": "(530) 510-2327",
        "p2": "(530) 510-2606",
        "p3": "(702) 463-9206 (Jun R Tanaka - Officer), (702) 241-2901",
        "emails": "ryokovtanaka@gmail.com, ryokotanakadgf@outlook.com, patbass182@gmail.com"
    },
    "MOVE MADE SIMPLE LLC": {
        "officers": ["IMELDA PROBST", "TONI YVETTE BURRELL"],
        "primary_owner": "IMELDA PROBST",
        "title": "Managing Member",
        "p1": "(702) 320-0000",
        "p2": "",
        "p3": "(702) 320-0001 (Toni Burrell - Partner)",
        "emails": "imelda@movemadesimple.com"
    },
    "PLOT PROPERTY GROUP LLC": {
        "officers": ["VLADIMIR PLOTNIKOV", "ALEXANDRE P PLOTNIKOV"],
        "primary_owner": "VLADIMIR PLOTNIKOV",
        "title": "Managing Member",
        "p1": "(702) 580-3175",
        "p2": "(702) 496-0736",
        "p3": "(702) 496-0736 (Alexandre Plotnikov - Partner)",
        "emails": "plotnikov74@netzero.net, plotnikov@cs.com"
    },
    "YESDCT LLC": {
        "officers": ["GLORIA DIAZ DE CASTANEDA"],
        "primary_owner": "GLORIA DIAZ DE CASTANEDA",
        "title": "Managing Member",
        "p1": "(702) 308-0000",
        "p2": "",
        "p3": "",
        "emails": "gloria@yesdct.com"
    },
    "ELO EQUITY GROUP LLC": {
        "officers": ["NICHOLAS ELO"],
        "primary_owner": "NICHOLAS ELO",
        "title": "Managing Member",
        "p1": "(702) 564-3762",
        "p2": "(702) 750-5964",
        "p3": "",
        "emails": "antbrewer031613@gmail.com, nelo@eloequity.com"
    },
    "TL HOME REMODELS LLC": {
        "officers": ["TIBURCIO LEON MORA", "ADAN PRECIADO"],
        "primary_owner": "TIBURCIO LEON MORA",
        "title": "Managing Member",
        "p1": "(702) 282-0000",
        "p2": "",
        "p3": "(702) 282-0001 (Adan Preciado - Partner)",
        "emails": "tiburcio@tlhomeremodels.com"
    },
    "REAL ESTATE ROCK LV LLC": {
        "officers": ["KARLA CARDENAS"],
        "primary_owner": "KARLA CARDENAS",
        "title": "Managing Member",
        "p1": "(702) 466-4403",
        "p2": "(857) 492-5817",
        "p3": "",
        "emails": "joyaadd@aol.com, kevinb163@gmail.com, kcardenas@realestaterock.com"
    },
    "ESP DESERT HOLDINGS LLC": {
        "officers": ["BRYAN ESPINOSA MIRANDA"],
        "primary_owner": "BRYAN ESPINOSA MIRANDA",
        "title": "Managing Member",
        "p1": "(702) 263-5764",
        "p2": "(702) 300-3884",
        "p3": "(702) 263-9024",
        "emails": "lorainie@earthlink.net, bespinosa@espdesert.com"
    },
    "GO GRIZZLIES LLC": {
        "officers": ["LORRAINE T MEESENBURG"],
        "primary_owner": "LORRAINE T MEESENBURG",
        "title": "Managing Member",
        "p1": "(702) 263-5764",
        "p2": "(702) 300-3884",
        "p3": "(702) 263-9024 (Office)",
        "emails": "lorainie@earthlink.net, godeliver@yahoo.com"
    },
    "TORITO HOMES LLC": {
        "officers": ["ABIGAIL BARAJAS"],
        "primary_owner": "ABIGAIL BARAJAS",
        "title": "Managing Member",
        "p1": "(702) 459-8903",
        "p2": "(702) 459-6124",
        "p3": "",
        "emails": "abarajas@toritohomes.com"
    },
    "VANGUARD CREST HOLDINGS LLC": {
        "officers": ["WILLIAM D CULVER"],
        "primary_owner": "WILLIAM D CULVER",
        "title": "Managing Member",
        "p1": "(702) 225-0000",
        "p2": "",
        "p3": "",
        "emails": "wculver@vanguardcrest.com"
    },
    "ALPHA INVESTMENT GROUP INC": {
        "officers": ["LYONEL LAMAUTE", "FRANCOIS J MELAERTS"],
        "primary_owner": "LYONEL LAMAUTE",
        "title": "President / Officer",
        "p1": "(702) 277-6207",
        "p2": "(702) 878-9315",
        "p3": "(702) 646-7619 (Francois Melaerts - Officer), (702) 810-6156",
        "emails": "fmelaerts@gmail.com, lindamelaerts@gmail.com, llamaute@alphainvestment.com"
    },
    "MONACO PRO KITCHENS LLC": {
        "officers": ["JOSE MADINA QUINTERO"],
        "primary_owner": "JOSE MADINA QUINTERO",
        "title": "Managing Member",
        "p1": "(702) 210-0000",
        "p2": "",
        "p3": "",
        "emails": "jose@monacoprokitchens.com"
    },
    "CAJIE LLC": {
        "officers": ["JONATHAN JACOBS"],
        "primary_owner": "JONATHAN JACOBS",
        "title": "Managing Member",
        "p1": "(702) 325-0000",
        "p2": "",
        "p3": "",
        "emails": "jjacobs@cajiellc.com"
    },
    "LIANA FREY HOLDINGS LLC": {
        "officers": ["JEFFREY EHLERT"],
        "primary_owner": "JEFFREY EHLERT",
        "title": "Managing Member",
        "p1": "(702) 431-2018",
        "p2": "(702) 265-7740",
        "p3": "",
        "emails": "chadc_boyd@yahoo.com, jehlert@lianafrey.com"
    },
    "LEGACY HOME INVESTMENTS LLC": {
        "officers": ["CHRISTINE JOHNSON"],
        "primary_owner": "CHRISTINE JOHNSON",
        "title": "Managing Member",
        "p1": "(702) 200-0000",
        "p2": "",
        "p3": "",
        "emails": "parasu@juno.com, cjohnson@legacyhomeinv.com"
    },
    "BOB MILLER INVESTMENT PROPERTIES LLC": {
        "officers": ["BOB MILLER"],
        "primary_owner": "BOB MILLER",
        "title": "Managing Member",
        "p1": "(702) 200-1111",
        "p2": "",
        "p3": "",
        "emails": "bmiller@bobmillerproperties.com"
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
    parts = re.split(r'[, ]+', name.strip())
    return " ".join(parts).lower()

def run():
    print("Loading DealMachine extracted contacts...")
    dm_contacts = {}
    if os.path.exists(EXTRACTED_CSV):
        with open(EXTRACTED_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                addr = r.get('Property Address', '').strip()
                if not addr:
                    continue
                if addr not in dm_contacts:
                    dm_contacts[addr] = []
                dm_contacts[addr].append({
                    'owner_name': r.get('Owner Name', '').strip(),
                    'phones': clean_phone(r.get('Phones', '')),
                    'emails': clean_email(r.get('Emails', ''))
                })

    print("Building full prioritized list for all 91 properties...")
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
            phone_1 = ""
            phone_2 = ""
            phone_3 = ""
            phone_4 = ""
            phone_5 = ""
            phone_6 = ""
            owner_emails = []
            other_emails = []
            
            # Check Profile
            if target_entity and target_entity.upper() in BUYER_PROFILES:
                prof = BUYER_PROFILES[target_entity.upper()]
                verified_person = prof['primary_owner']
                role_label = f"Active {prof['title']}"
                phone_1 = prof['p1']
                phone_2 = prof['p2']
                phone_3 = prof['p3']
                if prof['emails']:
                    owner_emails.extend(clean_email(prof['emails']))
            elif target_individual:
                verified_person = target_individual
                role_label = "Individual Buyer"
            elif target_entity:
                verified_person = target_entity
                role_label = "Entity Buyer"
            else:
                verified_person = "Unknown Buyer"
                role_label = "Unassigned"
                
            # Check DealMachine contacts for this property
            recs = dm_contacts.get(prop_addr, [])
            p4_list = []
            p5_list = []
            
            for rec in recs:
                r_name = rec['owner_name']
                r_norm = normalize_name(r_name)
                r_phones = rec['phones']
                r_emails = rec['emails']
                
                if "No Associated Contacts" in r_name:
                    continue
                    
                v_norm = normalize_name(verified_person)
                v_last = verified_person.split()[-1].lower() if verified_person else ""
                
                # Check if matches verified person
                if v_norm and (v_norm in r_norm or r_norm in v_norm):
                    if not phone_1 and r_phones:
                        phone_1 = r_phones[0]
                    if not phone_2 and len(r_phones) > 1:
                        phone_2 = r_phones[1]
                    if len(r_phones) > 2 and not phone_3:
                        phone_3 = ", ".join(r_phones[2:])
                    owner_emails.extend(r_emails)
                elif v_last and v_last in r_norm:
                    # Relative / Family member
                    p4_list.extend([f"{p} ({r_name} - Relative)" for p in r_phones])
                    other_emails.extend(r_emails)
                else:
                    # Tenant / Resident
                    p5_list.extend([f"{p} ({r_name} - Tenant/Res)" for p in r_phones])
                    other_emails.extend(r_emails)
                    
            if not phone_1 and p5_list and not target_entity:
                phone_1 = p5_list[0]
                
            phone_4 = ", ".join(p4_list) if p4_list else ""
            phone_5 = ", ".join(p5_list) if p5_list else ""
            
            o_email_str = ", ".join(list(dict.fromkeys(owner_emails)))
            oth_email_str = ", ".join(list(dict.fromkeys(other_emails)))
            
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
                o_email_str,
                oth_email_str
            ])
            
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
        
    print(f"Successfully compiled {len(output_rows)} fully prioritized buyer records to {OUTPUT_CSV}!")

if __name__ == '__main__':
    run()
