import json
import pymysql

pymysql.install_as_MySQLdb()

with open('1649473.json') as json_file:
    data = json.load(json_file)

def st_gunviolence(data)
    id = data["id"]
    url = data["url"]
    title = data["title"]
    date = data["date"]
    address = data["address"]
    latitude = data["geo"][0]
    longitude = data["geo"][1]
    state_id = data["congressional_district"]
    city_id = data["state_senate_district"] 


    sql = "INSERT INTO 'gunviolence' (id, url, state_id, city_id,\ 
                                      latitude, longtitude, address, date)  



for idx in data.items():
    print ("-> %s" % idx[0])