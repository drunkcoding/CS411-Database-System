#!/bin/sh
python3 ./update_data.py
python3 ./update_incidents.py
python3 ./import_json2db.py /prj/CS411-Database-System/gv_data/data/incidents /prj/CS411-Database-System/gv_data/processed
