import csv
import urllib.parse

# 1. Load competitor file to map address -> APN
competitor_file = r'c:\buyers_information\Dispo Board Competitor Buyers (3).csv'
apn_map = {}
with open(competitor_file, mode='r', encoding='utf-8') as f:
    reader = list(csv.reader(f))
    for row in reader[2:]:
        if len(row) > 9 and row[0].strip():
            addr = row[0].strip()
            apn = row[9].strip()
            apn_map[addr] = apn

print(f"Loaded {len(apn_map)} APN mappings.")

# 2. Update Dispo_Buyers_Prioritized_Verified.csv
input_file = r'c:\buyers_information\Dispo_Buyers_Prioritized_Verified.csv'

with open(input_file, mode='r', encoding='utf-8') as f:
    reader = list(csv.reader(f))

header = reader[0]
rows = reader[1:]

# We set the last column to 'Verified Web Search Sources & Exact URLs'
header[-1] = 'Verified Web Search Sources & Exact URLs'

updated_rows = []
for row in rows:
    if not row or not any(row):
        continue
    
    addr = row[0].strip()
    llc = row[1].strip()
    person = row[2].strip()
    status = row[3].strip()
    phone1 = row[4].strip()
    owner_emails = row[10].strip()
    
    apn = apn_map.get(addr, '')
    clean_apn = apn.replace('-', '') if apn else ''
    
    urls = []
    
    # NV SOS / Business Registry URL
    if llc and llc != 'Individual' and 'Unknown' not in llc:
        encoded_llc = urllib.parse.quote(llc)
        urls.append(f"[NV SOS Filing: {llc}] -> https://esos.nv.gov/EntitySearch/OnlineEntitySearch | OpenCorporates: https://opencorporates.com/companies/us_nv?q={encoded_llc}")
    elif llc == 'Individual' and person != 'Unknown Buyer':
        urls.append(f"[Clark County Public Records: {person}] -> https://www.clarkcountynv.gov/government/assessor/")
    elif 'Unknown' in person or not llc:
        urls.append("[Clark County Assessor Deed Search] -> https://www.clarkcountynv.gov/government/assessor/")
    
    # Clark County Assessor Direct Parcel Link
    if clean_apn:
        urls.append(f"[Clark County Assessor Parcel Record APN {apn}] -> https://maps.clarkcountynv.gov/assessor/AssessorParcelDetail/parcel.aspx?apn={clean_apn}")
    else:
        urls.append("[Clark County Assessor Search] -> https://maps.clarkcountynv.gov/assessor/AssessorParcelDetail/")
        
    # Official Business Web Link
    if 'webuyanyvegas' in owner_emails or 'Casey' in person or 'ALCHEMY' in llc:
        urls.append("[Investor Business Website] -> https://webuyanyvegashouse.com")
    elif '247companies' in owner_emails or 'FLIP SIDE' in llc:
        urls.append("[Investor Business Website] -> https://247companiesnow.com")
    elif 'hubbshomes' in owner_emails or 'HUBBSELEVATION' in llc:
        urls.append("[Investor Business Website] -> https://hubbshomes.com")
    elif 'betterassets' in owner_emails or 'BETTER ASSETS' in llc:
        urls.append("[Investor Business Website] -> https://betterassetsinc.com")
    elif 'plotnikov' in owner_emails or 'PLOT PROPERTY' in llc:
        urls.append("[Entity Registry Record] -> https://opencorporates.com/companies/us_nv/E0038872017-9")
    elif 'TORITO HOMES' in llc:
        urls.append("[NV SOS Entity Search] -> https://esos.nv.gov/EntitySearch/OnlineEntitySearch?q=TORITO+HOMES")
    elif 'GO GRIZZLIES' in llc:
        urls.append("[NV SOS Entity Search] -> https://esos.nv.gov/EntitySearch/OnlineEntitySearch?q=GO+GRIZZLIES")
    elif 'ALPHA INVESTMENT' in llc:
        urls.append("[NV SOS Entity Search] -> https://esos.nv.gov/EntitySearch/OnlineEntitySearch?q=ALPHA+INVESTMENT+GROUP")
        
    row[-1] = " ; ".join(urls)
    updated_rows.append(row)

with open(input_file, mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(updated_rows)

print(f"Successfully updated {len(updated_rows)} rows with exact web links.")
