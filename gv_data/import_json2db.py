import json
import re
import sys
import pymysql
import shutil
from os import listdir
from os.path import isfile, join

def CRV(data, item):
    try:
        ret_val = data[item]
    except:
        ret_val = "null"
    return ret_val

def st_gunviolence(db_conn, data):
    ret_val = 1
    id  = CRV(data, "id")
    url = CRV(data, "url")
    title = CRV(data, "title")
    date = CRV(data, "date")
    address = CRV(data, "address")
    latitude = data["geo"][0]
    longitude = data["geo"][1]
    state_id = CRV(data, "congressional_district")
    city_id = CRV(data, "state_senate_district")

    sql = "INSERT INTO gunviolence_gunviolence\
                       (id, title, url, date, city_id, state_id, latitude, longitude, address, created_at, updated_at)\
                  VALUES ('{}', '{}', '{}', STR_TO_DATE('{}','%m-%d-%Y'), '{}', '{}', '{}', '{}', '{}', now(), now())".format(id, title, url, date, 
                                                                                                      city_id, state_id, latitude, longitude, address)
    #print ("sql -> %s" % (sql))
    try:
        with db_conn.cursor() as cursor:
            cursor.execute(sql)
        db_conn.commit()
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))

def st_incidentchar(db_conn, data):
    ret_val = 1
    gv_id = data["id"]

    for idx in data["characteristics"]:
        sql = "INSERT INTO gunviolence_incidentcharacteristic\
                      (gv_id, characteristic, created_at, updated_at)\
               VALUES ('{}', '{}', now(), now())".format(gv_id, idx) 
        #print ("sql -> %s" % (sql))
        try:
            with db_conn.cursor() as cursor:
                cursor.execute(sql)
            db_conn.commit()
        except pymysql.MySQLError as error:
            print ("db error: %s" % (error))
            ret_val = 0
            break
    return ret_val

def st_participants(db_conn, data):
    ret_val = 1
    gv_id = data["id"]
    for idx in data["participants"]:
        type = CRV(idx, "type")
        name = CRV(idx, "name")
        age  = CRV(idx, "age")
        age_group = CRV(idx, "age_group")
        gender = CRV(idx, "gender")
        status = CRV(idx, "status")

        sql = "INSERT INTO gunviolence_participant\
                      (gv_id, type, name, age, age_group, gender, status, created_at, updated_at)\
               VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', now(), now())".format(
                       gv_id, type, name, age, age_group, gender, status) 
        #print ("sql -> %s" % (sql))
        try:
            with db_conn.cursor() as cursor:
                cursor.execute(sql)
            db_conn.commit()
        except pymysql.MySQLError as error:
            print ("db error: %s" % (error))
            ret_val = 0
            break
    return ret_val
    
def main(np_dir, p_dir):
    list_tp_files = [f for f in listdir(np_dir) if isfile(join(np_dir, f))]
    if len(list_tp_files) == 0:
        print ("no data file exist in the data directory")
        exit(1)

    print ("directory: %s, %d target files" % (np_dir, len(list_tp_files)))

    try:
        db_conn = pymysql.connect(host='10.10.0.56', user='sean', password='qrwe1423', db='sean', charset='utf8')
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
        exit(1)
   
    count = 1
    for idx_file in list_tp_files:
        print ("[%d] filename: %s" % (count, idx_file))
        list_fn = re.split(".", idx_file)
        if list_fn[1] != "json":
            pass
        try:
            with open(np_dir+"/"+idx_file, encoding='utf-8') as json_file:
                data = json.load(json_file)

                st_gunviolence(db_conn, data)
                st_incidentchar(db_conn, data)
                st_participants(db_conn, data)

                src_path = np_dir+"/"+idx_file
                dst_path = p_dir+"/"+idx_file

                print ("move %s to %s" % (src_path, dst_path))
                shutil.move(src_path, dst_path)
        except IOError as error:
            print ("file open error: %s: %s" % (idx_file, error))
            break
    db_conn.close()
        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("%s np-dir p-dir" % (sys.argv[0]))
        exit(1)
    main(sys.argv[1], sys.argv[2])