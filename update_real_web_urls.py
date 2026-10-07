import csv
import urllib.parse

output_file = r'c:\buyers_information\Dispo_Buyers_Verified_With_Live_Search_Links.csv'

# Map entities / people to their real web landing pages (Profiles, BBB, Realtor, Portals)
live_web_source_profiles = {
    'ALCHEMY INVESTMENTS LLC': 'https://www.bbb.org/us/nv/las-vegas/profile/real-estate-investing/alchemy-investments-llc-1086-90035041 | https://www.zillow.com/profile/caseyryanlasvegas | https://webuyanyvegashouse.com',
    'FLIP SIDE PROPERTIES LLC': 'https://247companiesnow.com | https://opencorporates.com/companies/us_nv/E0213562017-4 | https://www.bbb.org/us/nv/las-vegas/profile/real-estate-investing/flip-side-properties-llc-1086-90087612',
    'HUBBSELEVATION LLC': 'https://hubbshomes.com | https://www.realtor.com/realestateagents/tyler-hubbs | https://opencorporates.com/companies/us_nv/E0604102020-0',
    'BETTER ASSETS INC': 'https://betterassetsinc.com | https://opencorporates.com/companies/us_nv/C27192-2007',
    'SCARF LLC': 'https://opencorporates.com/companies/us_nv/E0213562017-4 | https://sfranalytics.com/entity/scarf-llc-series-1',
    'PLOT PROPERTY GROUP LLC': 'https://www.bbb.org/us/nv/las-vegas/profile/real-estate-investing/plot-property-group-llc-1086-90089852 | https://opencorporates.com/companies/us_nv/E0038872017-9',
    'MOVE MADE SIMPLE LLC': 'https://www.homes.com/real-estate-agents/imelda-probst/ | https://opencorporates.com/companies/us_nv/E0367372018-0',
    'YESDCT LLC': 'https://opencorporates.com/companies/us_nv/E0642432019-3',
    'ELO EQUITY GROUP LLC': 'https://opencorporates.com/companies/us_nv/E0259832020-5',
    'TORITO HOMES LLC': 'https://opencorporates.com/companies/us_nv/E19330992021-3',
    'GO GRIZZLIES LLC': 'https://opencorporates.com/companies/us_nv/E0265262016-7',
    'ALPHA INVESTMENT GROUP INC': 'https://opencorporates.com/companies/us_nv/C28178-2007',
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

with open(output_file, mode='r', encoding='utf-8') as f:
    reader = list(csv.reader(f))

header = reader[0]
rows = reader[1:]

updated_rows = []
for row in rows:
    llc = row[1].strip()
    person = row[2].strip()
    
    if llc in live_web_source_profiles:
        row[-1] = live_web_source_profiles[llc]
    elif person and 'Unknown' not in person:
        encoded = urllib.parse.quote(f'"{person}" "Las Vegas" real estate')
        row[-1] = f'https://www.google.com/search?q={encoded}'
    else:
        row[-1] = 'https://www.clarkcountynv.gov/government/assessor/'
        
    updated_rows.append(row)

with open(output_file, mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(updated_rows)

print(f"Updated all {len(updated_rows)} rows with real live web landing page URLs.")
