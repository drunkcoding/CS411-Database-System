import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

page = requests.get("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population")
soup = BeautifulSoup(page.content, 'html.parser')

data = []
table = soup.find_all('table', attrs={'class':'wikitable'})[1]
table_body = table.find('tbody')
rows = table_body.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip().split('[')[0] for ele in cols]
    data.append([ele for ele in cols if ele]) # Get rid of empty values

dataframe = []
fixture = []

for row in data:
    if not row or len(row) < 10: continue
    row_data = []
    m = re.search('(.*)\[?', row[1])
    row_data.append(m.group(0))
    row_data.append(row[2])
    row_data.append(int(row[3].replace(',','')))
    m = re.search('([0-9]+\.?[0-9]+)', row[7].replace(',',''))
    row_data.append(m.group(0))

    print(row_data)
    frame = {'model':'gunviolence.city', 'fields':{'name':row_data[0], 'state':row_data[1], 'population':row_data[2], 'land_area':float(row_data[3])}}
    fixture.append(frame)
    dataframe.append(row_data)

with open('city.json', 'w') as f:
    json.dump(fixture, f)

df = pd.DataFrame(dataframe)
df.to_csv("city.csv", header=False, index=False)