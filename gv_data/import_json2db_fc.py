import json
import re
import sys
import pymysql
from os import listdir
from os.path import isfile, join
import shutil

field_deli = "[|][|]"

def CRV(data, item = "none", filter=False):
    try:
        if item == "none":
            if len(data) == 0:
                item_data = "null"
            else: 
                list_rc = re.split("[:][:]", data)
                if len(list_rc) > 1:
                    filtered_data = list_rc[1]
                else:
                    filtered_data = data

                if filter:
                    item_data = re.sub("[^a-zA-Z0-9- ]", "", filtered_data)
                else:
                    item_data = filtered_data
        else:
            if filter:
                item_data = re.sub("[^a-zA-Z0-9- ]", "", data[item])
                if len(item_data) == 0:
                    item_date = "null"
            else:
                item_data = data[item]
    except:
        item_data = "null"

    #print ("item_data = %s" % item_data)
    return item_data

def st_gunviolence(cursor, data):
    ret_val = 1
    id  = CRV(data, "incident_id")
    url = CRV(data, "incident_url")
    title = CRV(data, "notes", filter=True)
    date = CRV(data, "date")
    address = CRV(data, "address", filter=True)
    latitude = CRV(data["latitude"])
    longitude = CRV(data["longitude"])

    state_name = CRV(data, "state", filter=True)
    city_name = CRV(data, "city_or_county", filter=True)

    address = re.sub("'","", address)
    sql = "INSERT INTO gunviolence_gunviolence\
                       (id, title, url, date, city, state, latitude, longitude, address, created_at, updated_at)\
                  VALUES ('{}', '{}', '{}', STR_TO_DATE('{}','%Y-%m-%d'), '{}', '{}', '{}', '{}', '{}', now(), now())".format(id, title, url, date, 
                                                                                                      city_name, state_name, latitude, longitude, address)
    #print ("sql -> %s" % (sql))
    try:
        cursor.execute(sql)
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
        print ("SQL = %s" % sql)
        ret_val = 0
    return ret_val

def st_incidentchar(cursor, data):
    ret_val = 1
    gv_id = data["incident_id"]

    #print ("%s" % data["incident_characteristics"])
    list_ic_data = re.split(field_deli, data["incident_characteristics"])
    try:
        for idx in list_ic_data:
            sql = "INSERT INTO gunviolence_incidentcharacteristic\
                          (gv_id, characteristic, created_at, updated_at)\
                   VALUES ('{}', '{}', now(), now())".format(gv_id, idx) 
            #print ("sql -> %s" % (sql))
            cursor.execute(sql)
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
        print ("SQL = %s" % sql)
        ret_val = 0
    except:
        ret_val = 0

    return ret_val

def IS_EMPTY_LIST(list, curr_idx):
    no_items = len(list)

    #print("len(list) = %d, curr_idx = %d" % (no_items, curr_idx))
    if no_items == 0:
        return True
    elif no_items <= curr_idx:
        return True
    return False

def st_participants(cursor, data):
    ret_val = 1
    gv_id = data["incident_id"]

    list_age = re.split(field_deli, data["participant_age"])
    list_age_group = re.split(field_deli, data["participant_age_group"])
    list_name = re.split(field_deli, data["participant_name"])
    list_gender = re.split(field_deli, data["participant_gender"])
    list_status = re.split(field_deli, data["participant_status"])
    list_type = re.split(field_deli, data["participant_type"])

    #print ("-=> %s" % data["participant_type"])
    #print ("list_type -> %s" % list_type)

    idx = 0
    try:
        for idx in range(0, len(list_type)):
            #print ("len(list_type = %d), idx = %d" % (len(list_type), idx))
            if IS_EMPTY_LIST(list_type, idx) == False:
                type = CRV(list_type[idx], filter = True)
            if IS_EMPTY_LIST(list_name, idx) == False:
                name = CRV(list_name[idx], filter=True)
            if IS_EMPTY_LIST(list_age, idx) == False:
                age  = CRV(list_age[idx], filter=True)
            if IS_EMPTY_LIST(list_age_group, idx) == False:
                age_group = CRV(list_age_group[idx], filter=True)
            if IS_EMPTY_LIST(list_gender, idx) == False:
                gender = CRV(list_gender[idx], filter=True)
            if IS_EMPTY_LIST(list_status, idx) == False:
                status = CRV(list_status[idx], filter=True)

            sql = "INSERT INTO gunviolence_participant\
                          (gv_id, type, name, age, age_group, gender, status, created_at, updated_at)\
                   VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', now(), now())".format(
                           gv_id, type, name, age, age_group, gender, status) 
            cursor.execute(sql)

            #print ("sql -> %s" % (sql))
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
        print ("SQL = %s" % sql)
        ret_val = 0
    except:
        ret_val = 0

    return ret_val

def st_guntype(cursor, data):
    ret_val = 1
    gv_id = data["incident_id"]

    list_gun_type = re.split(field_deli, data["gun_type"])
    list_gun_stolen = re.split(field_deli, data["gun_stolen"])

    idx = 0
    try:
        for idx in range(0, len(list_gun_type)):
            if IS_EMPTY_LIST(list_gun_type, idx) == False:
                gun_type = CRV(list_gun_type[idx])
            else:
                gun_type = "null"
            if IS_EMPTY_LIST(list_gun_stolen, idx) == False:
                stolen = CRV(list_gun_stolen[idx])
            else:
                stolen = "null"
            sql = "INSERT INTO gunviolence_guntype\
                          (gv_id, gun_type, stolen, created_at, updated_at)\
                   VALUES ('{}', '{}', '{}', now(), now())".format(\
                           gv_id, gun_type, stolen)
            #print ("sql -> %s" % (sql))
            cursor.execute(sql)
    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
        print ("SQL = %s" % sql)
        ret_val = 0
    except:
        print("Unexpected error:", sys.exc_info()[0])
        ret_val = 0

    return ret_val

def IS_SUCCESSFUL(ret_val):
    if ret_val:
        print ("successful")
    else:
        print ("error")
    return ret_val

def main(json_file):
    try:
        db_conn = pymysql.connect(host='10.10.0.23', user='sean', password='qrwe1423', db='sean', charset='utf8')

        with open(json_file, encoding='utf-8') as json_file:
            data = json.load(json_file)
       
        count = 0 
        failed = 0
        for gvi_idx in data:
            with db_conn.cursor() as cursor:
                #print ("raw_data ---> %s" % data[count])
                print ("\tphase 1", end=' -> ')
                if IS_SUCCESSFUL(st_gunviolence(cursor, gvi_idx)) == 0:
                    failed += 1
                    pass
                print ("\tphase 2", end=' -> ')
                if IS_SUCCESSFUL(st_incidentchar(cursor, gvi_idx)) ==0:
                    failed += 1
                    pass
                print ("\tphase 3", end=' -> ')
                if IS_SUCCESSFUL(st_participants(cursor, gvi_idx)) == 0:
                    failed += 1
                    pass
                print ("\tphase 4", end=' -> ')
                if IS_SUCCESSFUL(st_guntype(cursor, gvi_idx)) == 0:
                    failed += 1
                    pass
                print ("\tphase 5", end=' -> ')
                #print ("move %s to %s" % (src_path, dst_path))
                #shutil.move(src_path, dst_path)
                print ("successful")
                print ("-")
            db_conn.commit()
            count += 1
        print ("%d successful, %d failed" % (count, failed))

    except pymysql.MySQLError as error:
        print ("db error: %s" % (error))
    except IOError as error:
        print ("file open error: %s: %s" % (idx_file, error))


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print ("%s .json" % (sys.argv[0]))
        exit(1)
    main(sys.argv[1])
