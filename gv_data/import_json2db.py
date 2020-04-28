import json
import re
import sys
import pymysql
from os import listdir
from os.path import isfile, join
import shutil

def CRV(data, item):
    try:
        item_data = data[item]
    except:
        item_data = "null"
    return item_data

def st_gunviolence(db_conn, data):
    ret_val = 1
    id  = CRV(data, "id")
    url = CRV(data, "url")
    title = CRV(data, "title")
    date = CRV(data, "date")
    address = CRV(data, "address")
    try:
        latitude = data["geo"][0]
        longitude = data["geo"][1]
    except:
        latitude = 0
        longitude = 0

    state_id = CRV(data, "congressional_district")
    city_id = CRV(data, "state_senate_district")

    if state_id == "null":
        state_id = "1"
    elif (int(state_id) <= 0 or int(state_id) >= 53):
        state_id = "1"
    if city_id == "null":
        city_id = "1"

    address = re.sub("'","", address)
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
        ret_val = 0
    return ret_val

def st_incidentchar(db_conn, data):
    ret_val = 1
    gv_id = data["id"]

    try:
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
    except:
        ret_val = 0
    return ret_val

def st_participants(db_conn, data):
    ret_val = 1
    gv_id = data["id"]

    try:
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
    except:
        ret_val = 0
    return ret_val

def st_guntype(db_conn, data):
    ret_val = 1
    gv_id = data["id"]

    try:
        for idx in data["guns"]:
            type = CRV(idx, "type")
            name = CRV(idx, "stolen")

            sql = "INSERT INTO gunviolence_guntype\
                          (gv_id, gun_type, stolen, created_at, updated_at)\
                   VALUES ('{}', '{}', '{}', now(), now())".format(
                           gv_id, type, name)
            #print ("sql -> %s" % (sql))
            try:
                with db_conn.cursor() as cursor:
                    cursor.execute(sql)
                db_conn.commit()
            except pymysql.MySQLError as error:
                print ("db error: %s" % (error))
                ret_val = 0
                break
    except:
        ret_val = 0
    return ret_val

def insert_update_log(db_conn):
    ret_val = 1
    last_id = 0
    sql1 = "INSERT INTO gunviolence_update_log\
                 (source, started_at, ended_at, no_incident)\
                  VALUES ('official-website', now(), now(), 0)"
    sql2 = "SELECT LAST_INSERT_ID() AS last_id"
    try:
        with db_conn.cursor() as cursor:
            cursor.execute(sql1)
            cursor.execute(sql2)
            for row in cursor:
                last_id = int(row[0])
        db_conn.commit()
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
        ret_val = 0
   
    if ret_val != 0:
        ret_val = last_id
         
    return ret_val

def update_ended_at_log(db_conn, row_id, no_incident):
    ret_val = 1
    last_id = 0
    sql = "UPDATE gunviolence_update_log SET ended_at = now(), no_incident = {}\
                  WHERE id = {} ".format(no_incident, row_id)
    print (sql)
    try:
        with db_conn.cursor() as cursor:
            cursor.execute(sql)
        db_conn.commit()
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
        ret_val = 0
         
    return ret_val

def IS_SUCCESSFUL(ret_val):
    if ret_val:
        print ("successful")
    else:
        print ("error")
    return ret_val

def main(np_dir, p_dir):
    last_id = 0
    list_tp_files = [f for f in listdir(np_dir) if isfile(join(np_dir, f))]
    if len(list_tp_files) == 0:
        print ("no data file exist in the data directory")
        exit(1)

    print ("directory: %s, %d target files" % (np_dir, len(list_tp_files)))

    try:
        db_conn = pymysql.connect(host='10.10.0.26', user='sean', password='qrwe1423', db='sean', charset='utf8')
        last_id = insert_update_log(db_conn)
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
        exit(1)
    
    count = 0
    for idx_file in list_tp_files:
        count += 1
        print ("[%d] gv data: %s " % (count, idx_file))
        list_fn = re.split(".", idx_file)
        if list_fn[1] != "json":
            pass
        try:
            with open(np_dir+"/"+idx_file, encoding='utf-8') as json_file:
                data = json.load(json_file)

                print ("\tphase 1", end=' -> ')
                if IS_SUCCESSFUL(st_gunviolence(db_conn, data)) == 0:
                    pass
                print ("\tphase 2", end=' -> ')
                if IS_SUCCESSFUL(st_incidentchar(db_conn, data)) ==0:
                    pass
                print ("\tphase 3", end=' -> ')
                if IS_SUCCESSFUL(st_participants(db_conn, data)) == 0:
                    pass
                print ("\tphase 4", end=' -> ')
                if IS_SUCCESSFUL(st_guntype(db_conn, data)) == 0:
                    pass

                src_path = np_dir+"/"+idx_file
                dst_path = p_dir+"/"+idx_file

                print ("\tphase 5", end=' -> ')
                print ("move %s to %s" % (src_path, dst_path))
                shutil.move(src_path, dst_path)
                print ("successful")
                print ("-")
        except IOError as error:
            print ("file open error: %s: %s" % (idx_file, error))
            break
    update_ended_at_log(db_conn, last_id, count)
    
        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("%s np-dir p-dir" % (sys.argv[0]))
        exit(1)
    main(sys.argv[1], sys.argv[2])
