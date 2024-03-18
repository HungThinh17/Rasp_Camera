# https://stackoverflow.com/questions/51603089/python-3-6-inserting-values-into-mariadb-via-variable
from __future__ import annotations
import os
import pymysql
import time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from module.db_main import dbSLI

class dbSQL:
    def __init__(self) -> None:
        self.deviceID = ''
        self.imgID = ''
        self.imgDate = ''
        self.imgTime = ''
        self.lat = ''
        self.lon = ''
        self.alt = ''
        self.numSat = ''

    def set_deviceID(self, val):
        self.deviceID = val
        return
    
    def set_imgID(self, val):
        self.imgID = val
        return
    
    def set_imgDate(self, val):
        self.imgDate = val
        return
    
    def set_imgTime(self, val):
        self.imgTime = val
        return
    
    def set_lat(self, val):
        self.lat = val
        return
    
    def set_lon(self, val):
        self.lon = val
        return

    def set_alt(self, val):
        self.alt = val
        return
    
    def set_numSat(self, val):
        self.numSat = val
        return


class m_SQL:
    def __init__(self) -> None:
        self.mariadb_root = '/home/dgmsli/Documents/10_project/00_mini_SLI/data/db/' 

        self.db_to_create = 'slidb'

        self.conn = pymysql.connect(host='127.0.0.1',  user='dgmsli', passwd='20042020',  cursorclass=pymysql.cursors.DictCursor)

        print('Connection successful!!')

    def __del__(self):
        return

    # Check if db exists, if not create
    def check_db_exists_create(self):
        dbfile = os.path.join(self.mariadb_root, self.db_to_create)
        if not os.path.exists(dbfile):
            cur = self.conn.cursor()
            command = "CREATE DATABASE IF NOT EXISTS %s;" % self.db_to_create
            print(command)
            cur.execute(command)
            print("Database created", self.db_to_create)
        else:
            print("Database already exists: %s" % self.db_to_create)
            
    # create table
    def create_table(self):
        cur = self.conn.cursor()
        command = "use %s; " % self.db_to_create
        cur.execute(command)
        create_table = ("""
                    CREATE TABLE IF NOT EXISTS sli_info (
                    deviceID varchar(255),
                    imgID varchar(255),
                    date varchar(255),
                    time varchar(255),
                    lat varchar(255),
                    lon varchar(255),
                    alt varchar(255),
                    numSat varchar(255),
                    PRIMARY KEY (imgID));
                    """)
        print("create table")
        cur.execute(create_table)
        print(command)

# add data to table
def run_add_data(stop, db: 'dbSLI'):
    # check and create DB
    #db.sliSQL.check_db_exists_create()
    dbfile = os.path.join(db.sliSQL.mariadb_root, db.sliSQL.db_to_create)
    if not os.path.exists(dbfile):
        cur = db.sliSQL.conn.cursor()
        command = "CREATE DATABASE IF NOT EXISTS %s;" % db.sliSQL.db_to_create
        print(command)
        cur.execute(command)
        print("Database created", db.sliSQL.db_to_create)
    else:
        print("Database already exists: %s" % db.sliSQL.db_to_create)
            
    
    # check and create table
    #db.sliSQL.create_table()
    cur = db.sliSQL.conn.cursor()
    command = "use %s; " % db.sliSQL.db_to_create
    cur.execute(command)
    create_table = "CREATE TABLE IF NOT EXISTS sli_info (deviceID varchar(255), imgID varchar(255), date varchar(255), time varchar(255), lat varchar(255), lon varchar(255), alt varchar(255), numSat varchar(255), PRIMARY KEY (imgID)); "
    print("create table")
    cur.execute(create_table)
    print(command)

    # use table
    cur = db.sliSQL.conn.cursor()
    command = "use %s; " % db.sliSQL.db_to_create
    cur.execute(command)

    # DB ready
    db.DataBaseState.set_state(4) # ready

    # infinite loop add data to table
    while 1:
        # check list img data db not empty
        if not db.check_img_data_db_empty():
            print ("have data for database")

            data = db.get_img_data_db_0()

            statement = "INSERT INTO sli_info (deviceID, imgID, date, time, lat, lon, alt, numSat) VALUES  (%s,%s,%s,%s,%s,%s,%s,%s);"
            val = (data.deviceID,data.imgID, data.imgDate, data.imgTime, data.lat, data.lon, data.alt, data.numSat)
            cur.execute(statement, val)

            db.sliSQL.conn.commit()
            
            #print("add ok")

        if stop():
            db.DataBaseState.set_state(5) # stop
            break

        time.sleep(0.001)

    cur.close()
    db.sliSQL.conn.close()
