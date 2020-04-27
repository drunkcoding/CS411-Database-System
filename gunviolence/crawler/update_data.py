import cfscrape
from datetime import datetime
import json
import re, sys
from time import sleep
from os import path
#from geopy.geocoders import GoogleV3
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.conf import settings

start_year = 2020
current_year = datetime.now().year

MASS_SHOOTINGS_JSON = path.join(
    settings.MEDIA_DIR,
    f'mass_shootings.json',
)

scraper = cfscrape.create_scraper()

keyed_mass_shooting_data = {}

def scrape_results(year, page):
    url = f'https://www.gunviolencearchive.org/mass_shootings?page={page}&year={year}'
    res = scraper.get(url)
    if res.status_code != 200: return []
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

print(f'scraping year {current_year}')
page = 0
done_importing = False
while not done_importing:
    results = scrape_results(current_year, page)
    new_results_count = merge_shooting_data(results)
    done_importing = new_results_count == 0
    page += 1
    sleep(1)
print(f'Done importing {current_year}')

print('Sorting results')
updated_shooting_data = sorted(keyed_mass_shooting_data.values(),
                               key=lambda row: row['date'])

updated_shootings_compact = []
for shooting in updated_shooting_data:
    shooting['date'] = shooting['date'].strftime('%Y-%m-%d')
    updated_shootings_compact.append([
        shooting['id'], shooting['date'], shooting['killed'], shooting['injured']
        , shooting['lat'] if 'lat' in shooting else None
        , shooting['lng'] if 'lng' in shooting else None
    ])


print('Writing results')
with open(MASS_SHOOTINGS_JSON, mode='w', encoding="utf-8") as outfile:
    json.dump(updated_shooting_data, outfile, indent=2, ensure_ascii=False)

print(f'Done! {len(updated_shooting_data)} shootings found')
