import json
import pymysql
import db_helper 

db_conn = pymysql.connect(host='10.10.0.56', user='root', password='qrwe1423', db='antientropy_cs411', charset='utf8')

def st_gunviolence(db_conn, data):
    id = data["id"]
    url = data["url"]
    title = data["title"]
    date = data["date"]
    address = data["address"]
    latitude = data["geo"][0]
    longitude = data["geo"][1]
    state_id = data["congressional_district"]
    city_id = data["state_senate_district"] 

    sql = "INSERT INTO 'gunviolence_gunviolence'\
                       (id, title, url, state_id, city_id, latitude, longtitude, address, \
                        date, created_at, updated_at)\
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), now())"
    try:
        with db_conn.cursor() as cursor:
            cursor.execute(sql, (id, title, url, state_id, city_id, latitude, longtitude, address, date))

        db_conn.commit()
    except:
        print ("db error")

def st_incidentchar(db_conn, data):
    id = data["id"]
    state_id = data["congressional_district"]
    city_id = data["state_senate_district"] 

    for idx in data["characteristics"]:
        sql = "INSERT INTO 'gunviolence_incidentcharacteristic'\
                    (characteristic, count, city_id, state_id, created_at, updated_at)\
               VALUES (%s, %s, %s, %s, %s, %s,)
        
    

with open('1649473.json') as json_file:
    data = json.load(json_file)


st_gunviolence(data)