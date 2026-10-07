import csv
import urllib.parse
import re

competitor_file = r'c:\buyers_information\Dispo Board Competitor Buyers (3).csv'
verified_file = r'c:\buyers_information\Dispo_Buyers_Prioritized_Verified.csv'
output_file = r'c:\buyers_information\Dispo_Buyers_Verified_With_Live_Search_Links.csv'

# 1. Load competitor file details (APN, Source Entity, Source Owner, etc.)
comp_data = {}
with open(competitor_file, mode='r', encoding='utf-8') as f:
    reader = list(csv.reader(f))
    for row in reader[2:]:
        if row and row[0].strip():
            addr = row[0].strip()
            apn = row[9].strip() if len(row) > 9 else ''
            source_entity = row[7].strip() if len(row) > 7 else ''
            source_owner = row[8].strip() if len(row) > 8 else ''
            buyer_entity_1 = row[10].strip() if len(row) > 10 else ''
            buyer_name_1 = row[11].strip() if len(row) > 11 else ''
            comp_data[addr] = {
                'apn': apn,
                'source_entity': source_entity,
                'source_owner': source_owner,
                'buyer_entity_1': buyer_entity_1,
                'buyer_name_1': buyer_name_1
            }

# 2. Load existing verified data
verified_data = []
with open(verified_file, mode='r', encoding='utf-8') as f:
    reader = list(csv.reader(f))
    v_header = reader[0]
    for row in reader[1:]:
        if row and row[0].strip():
            verified_data.append(row)

# 3. Known Company Websites & Profiles
company_web_map = {
    'ALCHEMY INVESTMENTS LLC': 'https://webuyanyvegashouse.com',
    'FLIP SIDE PROPERTIES LLC': 'https://247companiesnow.com',
    'HUBBSELEVATION LLC': 'https://hubbshomes.com',
    'BETTER ASSETS INC': 'https://betterassetsinc.com',
    'PLOT PROPERTY GROUP LLC': 'https://opencorporates.com/companies/us_nv/E0038872017-9',
    'MOVE MADE SIMPLE LLC': 'https://www.movemadesimple.com',
    'ELO EQUITY GROUP LLC': 'https://opencorporates.com/companies/us_nv/E0259832020-5',
    'TORITO HOMES LLC': 'https://opencorporates.com/companies/us_nv/E19330992021-3',
    'GO GRIZZLIES LLC': 'https://opencorporates.com/companies/us_nv/E0265262016-7',
    'ALPHA INVESTMENT GROUP INC': 'https://opencorporates.com/companies/us_nv/C28178-2007',
    'BIG RED LLC': 'https://opencorporates.com/companies/us_nv/E0630712015-8',
    'SCARF LLC': 'https://opencorporates.com/companies/us_nv/E0213562017-4',
    'YESDCT LLC': 'https://opencorporates.com/companies/us_nv/E0642432019-3',
    'REAL ESTATE ROCK LV LLC': 'https://opencorporates.com/companies/us_nv/E10382342020-0',
    'ESP DESERT HOLDINGS LLC': 'https://opencorporates.com/companies/us_nv/E0520262020-9',
    'TL HOME REMODELS LLC': 'https://opencorporates.com/companies/us_nv/E0630982020-2',
    'MONACO PRO KITCHENS LLC': 'https://opencorporates.com/companies/us_nv/E0271702016-8',
    'CAJIE LLC': 'https://opencorporates.com/companies/us_nv/E0459802017-8',
    'LIANA FREY HOLDINGS LLC': 'https://opencorporates.com/companies/us_nv/E0182832018-8',
    'BOB MILLER INVESTMENT PROPERTIES LLC': 'https://opencorporates.com/companies/us_nv/E0368292015-8',
    'LEGACY HOME INVESTMENTS LLC': 'https://opencorporates.com/companies/us_nv/E0195652019-5',
    'SHARAN PROPERTIES LP INC': 'https://opencorporates.com/companies/us_nv/E0534202020-4',
    'CASTLE LLC': 'https://opencorporates.com/companies/us_nv/E0034292016-7'
}

new_header = [
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
    'Other Emails',
    'Nevada SOS / Corporate Filing Link',
    'Clark County Assessor Parcel Link',
    'Verified Web Search & Business Link'
]

out_rows = []

for v_row in verified_data:
    addr = v_row[0].strip()
    llc = v_row[1].strip()
    person = v_row[2].strip()
    status = v_row[3].strip()
    phone1 = v_row[4].strip()
    phone2 = v_row[5].strip()
    phone3 = v_row[6].strip()
    phone4 = v_row[7].strip()
    phone5 = v_row[8].strip()
    phone6 = v_row[9].strip()
    owner_emails = v_row[10].strip()
    other_emails = v_row[11].strip()
    
    comp_info = comp_data.get(addr, {})
    apn = comp_info.get('apn', '')
    clean_apn = apn.replace('-', '') if apn else ''
    
    # 1. NV SOS Link
    if llc and llc != 'Individual' and 'Unknown' not in llc:
        encoded_llc = urllib.parse.quote(llc)
        sos_link = f"https://esos.nv.gov/EntitySearch/OnlineEntitySearch?q={encoded_llc}"
    elif llc == 'Individual' and person != 'Unknown Buyer':
        sos_link = "N/A (Individual Buyer Deed)"
    else:
        sos_link = "https://esos.nv.gov/EntitySearch/OnlineEntitySearch"
        
    # 2. Assessor Link
    if clean_apn:
        assessor_link = f"https://maps.clarkcountynv.gov/assessor/AssessorParcelDetail/parcel.aspx?apn={clean_apn}"
    else:
        assessor_link = "https://www.clarkcountynv.gov/government/assessor/"
        
    # 3. Web Search & Business Link
    search_query = f"{person} {llc} Las Vegas real estate".strip()
    encoded_search = urllib.parse.quote(search_query)
    web_link = company_web_map.get(llc, f"https://www.google.com/search?q={encoded_search}")
    
    out_rows.append([
        addr,
        llc,
        person,
        status,
        phone1,
        phone2,
        phone3,
        phone4,
        phone5,
        phone6,
        owner_emails,
        other_emails,
        sos_link,
        assessor_link,
        web_link
    ])

with open(output_file, mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(new_header)
    writer.writerows(out_rows)

print(f"Successfully generated {len(out_rows)} rows in {output_file}")
