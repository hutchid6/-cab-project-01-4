#!/bin/bash
dropdb team4_db
createdb team4_db
python create_sql_file.py
psql team4_db -c '\i team4_db.sql'