import cfscrape
from datetime import datetime
import json
import re
from os import path, environ
from time import sleep
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.conf import settings

INCIDENTS_FOLDER = path.join(
    settings.MEDIA_DIR,
    'incidents',
)

MASS_SHOOTINGS_JSON = path.join(
    settings.MEDIA_DIR,
    'mass_shootings.json',
)

MASS_SHOOTINGS_JSON_FULL = path.join(
    settings.MEDIA_DIR,
    'mass_shootings_full.json',
)

# refresh data for incidents less than this many days old
REFRESH_LAST_NUM_DAYS = 30

scraper = cfscrape.create_scraper()

geoloc_regex = re.compile(
    r'Geolocation:\s?(\-?\d+\.\d+),\s?(\-?\d+\.\d+)', flags=re.IGNORECASE)
source_url_regex = re.compile(r'URL:', flags=re.IGNORECASE)


def format_field(field):
    return re.sub(r'\s+', '_', field.lower().strip())


def parse_location(container):
    address_parts = []
    coords = None
    for span in container.find_all('span'):
        geo_match = geoloc_regex.match(span.text)
        if geo_match:
            coords = (float(geo_match[1]), float(geo_match[2]))
        else:
            address_parts.append(span.text)
    return {
        'address': (', '.join(address_parts)).strip(),
        'geo': coords,
    }


def strip_query_string(url):
    return re.sub(r'\?.*$', '', url)


# return a list of objects mapping to multiple ul groups on the page
def parse_attribute_lists(container):
    items = []
    for item_info in container.select('div > ul'):
        item = {}
        for item_detail in item_info.find_all('li', recursive=False):
            detail_parts = item_detail.text.split(':')
            field = format_field(detail_parts[0])

            sub_items = item_detail.find_all('li')
            value = detail_parts[1].strip()
            if field != 'name':
                value = value.lower()
            # sometimes there's a nested list within the value
            if len(sub_items) > 0:
                value = [sub_item.text for sub_item in sub_items]
            item[field] = value
        items.append(item)
    return items


def parse_participants(container):
    return {
        'participants': parse_attribute_lists(container)
    }


def parse_incident_characteristics(container):
    return {
        'characteristics': [li.text for li in container.find_all('li')]
    }


def parse_guns_involved(container):
    return {
        'guns': parse_attribute_lists(container)
    }


def parse_district(container):
    district_info = {}
    for district_str in container.text.strip().split('\n')[1:]:
        if district_str.strip() != '':
            parts = district_str.strip().split(':')
            field = format_field(parts[0])
            value = parts[1].strip()
            district_info[field] = value
    return district_info


def parse_sources(container):
    sources = []
    for source_elm in container.find_all('ul'):
        source = {}
        for source_component in source_elm.find_all('li', recursive=False):
            if source_url_regex.match(source_component.text):
                source['url'] = source_component.find('a')['href']
            elif source_component.find('img'):
                source['img_thumb'] = strip_query_string(
                    source_component.find('img')['src'])
                source['img_full'] = strip_query_string(
                    source_component.find('a')['href'])
        sources.append(source)
    return {
        'sources': sources
    }


def scrape_incident(incident_id):
    url = f'https://www.gunviolencearchive.org/incident/{incident_id}'
    res = scraper.get(url)
    soup = BeautifulSoup(res.content, features="lxml")
    title = soup.find_all('h1')[-1].text
    incident_details = {
        'id': incident_id,
        'url': url,
        'title': title,
        'date': title.split(' ')[0],
    }
    for header in soup.find_all('h2'):
        header_text = header.text.lower()
        if header_text == 'location':
            incident_details.update(parse_location(header.parent))
        elif header_text == 'participants':
            incident_details.update(parse_participants(header.parent))
        elif header_text == 'incident characteristics':
            incident_details.update(
                parse_incident_characteristics(header.parent))
        elif header_text == 'guns involved':
            incident_details.update(
                parse_guns_involved(header.parent))
        elif header_text == 'sources':
            incident_details.update(
                parse_sources(header.parent))
        elif header_text == 'district':
            incident_details.update(
                parse_district(header.parent))
    return incident_details


def write_json(path, data):
    with open(path, mode ='w', encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)


with open(MASS_SHOOTINGS_JSON, encoding="utf-8") as json_file:
    shootings = json.load(json_file)
    for shooting in shootings:
        incident_id = shooting['id']
        incident_date = datetime.strptime(shooting['date'], '%Y-%m-%d')
        incident_age_days = (datetime.now() - incident_date).days
        is_recent = incident_age_days < REFRESH_LAST_NUM_DAYS
        if incident_id == 946496:
            print('Las Vegas shooting is a PDF, cant be scraped')
        else:
            incident_file = path.join(INCIDENTS_FOLDER, f'{incident_id}.json')
            if is_recent or not path.exists(incident_file):
                print(f'scraping incident {incident_id}')
                incident_data = scrape_incident(incident_id)
                write_json(incident_file, incident_data)

print('writing out mass_shootings_full.json')
with open(MASS_SHOOTINGS_JSON, encoding="utf-8") as json_file:
    shootings = json.load(json_file)
    for shooting in shootings:
        incident_id = shooting['id']
        incident_file = path.join(INCIDENTS_FOLDER, f'{incident_id}.json')
        if path.exists(incident_file):
            with open(incident_file, encoding="utf-8") as incident_json_file:
                incident_details = json.load(incident_json_file)
                # remove duplicated data with base
                incident_details.pop('id', None)
                incident_details.pop('geo', None)
                incident_details.pop('date', None)
                incident_details.pop('address', None)
                shooting['details'] = incident_details
    write_json(MASS_SHOOTINGS_JSON_FULL, shootings)

print('Done!')
