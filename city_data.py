import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

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

print(data)

dataframe = []
for row in data:
    if not row or len(row) < 10: continue
    row_data = []
    row_data.append(row[1])
    row_data.append(row[2])
    row_data.append(int(row[3].replace(',','')))
    m = re.search('([0-9]+\.?[0-9]+)', row[7].replace(',',''))
    row_data.append(m.group(0))
    dataframe.append(row_data)

df = pd.DataFrame(dataframe)
df.to_csv("city_data.csv", header=False, index=False)