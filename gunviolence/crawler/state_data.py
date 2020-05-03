import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

page = requests.get("https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States")
soup = BeautifulSoup(page.content, 'html.parser')

data = []
tables = soup.find_all('table', attrs={'class':'wikitable'})

for table in tables:
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        name = row.find('th')
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols] + [name.text.strip()]
        data.append([ele for ele in cols if ele]) # Get rid of empty values

dataframe = []

state_fixture = []
#pk = 1

for row in data:
    if not row or len(row) < 10: continue
    row_data = []

    m = re.search('(.*)\[?', row[-1])
    row_data.append(m.group(0))
    # row_data.append(row[-1])
    

    row_data.append(int(row[len(row) - 7].replace(',','')))
    m = re.search('([0-9]+\.?[0-9]+)', row[len(row) - 3].replace(',',''))
    row_data.append(m.group(0))

    print(row_data)

    frame = {'model':'gunviolence.state', 'fields':{'name':row_data[0], 'population':row_data[1], 'land_area':float(row_data[2])}}
    state_fixture.append(frame)
    dataframe.append(row_data)
    #pk += 1

with open('state.json', 'w') as f:
    json.dump(state_fixture, f)

dataframe = [['name','population','land_area']] + dataframe
df = pd.DataFrame(dataframe)
df.to_csv("state.csv", header=False, index=False)
