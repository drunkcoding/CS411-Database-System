import cfscrape
from datetime import datetime
import json
import re
from time import sleep
from os import path
from geopy.geocoders import GoogleV3
from bs4 import BeautifulSoup
from dateutil.parser import parse

start_year = 2019

current_year = datetime.now().year


GOOGLE_GEOCODE_API_KEY="AIzaSyAZbJA9SsNx6vI4yALD8iOB5p0dpwKl6-s"
utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)

MASS_SHOOTINGS_JSON = path.join(
    path.dirname(__file__),
    'data/mass_shootings.json',
)

MASS_SHOOTINGS_COMPACT_JSON = path.join(
    path.dirname(__file__),
    'data/mass_shootings_compact.json',
)

geolocator = GoogleV3(GOOGLE_GEOCODE_API_KEY, timeout=10)
scraper = cfscrape.create_scraper()


def geocode(address, city, state, tries=3):
    address_str = f'{city}, {state}, United States'
    if (address.lower() != 'n/a'):
        address_str = address + ', ' + address_str
    try:
        return geolocator.geocode(address_str)
    except Exception as e:
        print(f'Geocoding failed: {address_str}')
        if tries <= 0:
            raise e
        return geocode(address, city, state, tries=tries-1)

keyed_mass_shooting_data = {}

def scrape_results(year, page):
    url = f'https://www.gunviolencearchive.org/reports/mass-shooting?page={page}&year={year}'

    res = scraper.get(url)
    soup = BeautifulSoup(res.content, features="lxml")
    table = soup.find('table')
    headers = [re.sub(r'[^a-z]', '', th.get_text().lower())
               for th in table.find_all('th')]
    rows = table.find('tbody').find_all('tr')

    results = []
    for row in rows:
        cols = row.find_all('td')
        links = row.select('.links a')
        incident_id = int(re.sub(r'[^\d]', '', links[0].get('href')))
        if not incident_id > 0:
            raise RuntimeError(f'Invalid incident ID {incident_id} at {url}')
        results.append({
            'id': int(re.sub(r'[^\d]', '', links[0].get('href'))),
            'date': parse(cols[headers.index('incidentdate')].get_text()),
            'state': cols[headers.index('state')].get_text(),
            'city': cols[headers.index('cityorcounty')].get_text(),
            'address': cols[headers.index('address')].get_text(),
            'killed': int(cols[headers.index('killed')].get_text()),
            'injured': int(cols[headers.index('injured')].get_text()),
            'source': links[1].get('href') if len(links) > 1 else None,
        })
    return results


def merge_shooting_data(scraped_data):
    total_new = 0
    for shooting in scraped_data:
        if shooting['id'] not in keyed_mass_shooting_data:
            print(f'GV found: {shooting["id"]}, {shooting["date"]}')
            keyed_mass_shooting_data[shooting['id']] = {}
            total_new += 1
        keyed_mass_shooting_data[shooting['id']].update(shooting)
    return total_new


for year in range(start_year, current_year + 1):
    print(f'scraping year {year}')
    page = 0
    done_importing = False
    while not done_importing:
        results = scrape_results(year, page)
        new_results_count = merge_shooting_data(results)
        done_importing = new_results_count == 0
        page += 1
    print(f'Done importing {year}')

print('Geocoding missing data')
for shooting in keyed_mass_shooting_data.values():
    if not shooting.get('lat') and not shooting.get('lng'):
        loc = geocode(shooting['address'], shooting['city'], shooting['state'])
        shooting['lat'] = loc.latitude
        shooting['lng'] = loc.longitude
        print(f'geocoded {loc.address}: {loc.latitude}, {loc.longitude}', file=utf8stdout)

print('Sorting results')
updated_shooting_data = sorted(keyed_mass_shooting_data.values(),
                               key=lambda row: row['date'])

updated_shootings_compact = []
for shooting in updated_shooting_data:
    shooting['date'] = shooting['date'].strftime('%Y-%m-%d')
    updated_shootings_compact.append([
        shooting['id'], shooting['date'], shooting['killed'], shooting['injured'], shooting['lat'], shooting['lng']
    ])


print('Writing results')
with open(MASS_SHOOTINGS_JSON, mode='w', encoding="utf-8") as outfile:
    json.dump(updated_shooting_data, outfile, indent=2, ensure_ascii=False).encode('utf8')

with open(MASS_SHOOTINGS_COMPACT_JSON, 'w', encoding="utf-8") as outfile:
    json.dump(updated_shootings_compact, outfile,
              separators=(',', ':'), ensure_ascii=False).encode('utf8')

print(f'Done! {len(updated_shooting_data)} shootings found')
