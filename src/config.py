#!/usr/bin/python

#Contributors: Bret Elphick, Dalton Hutchinson, Jimmy Fay
#Project Name - CSC 315: Energy Demand Tool
#Project Description - Tool extracts data from database, creates a table, creates charts, and creates cards for viewing stats
#File Name - config.py
#File Description - File reads database.ini and connects to database

"""
This code is from:
https://www.postgresqltutorial.com/postgresql-python/
"""

from configparser import ConfigParser
 
 
def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return db
