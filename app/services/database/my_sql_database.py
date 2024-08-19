from __future__ import annotations

import os
import pymysql # type: ignore

class MySliDatabase:
    def __init__(self) -> None:
        try:
            # TODO - need to define this info as a config file or arguments
            self.mariadb_root = os.path.join(os.getcwd(),'data/db/')
            self.db_to_create = 'slidb'
            self.conn = pymysql.connect(host='localhost',  user='hungnp', passwd='1',  cursorclass=pymysql.cursors.DictCursor)
            print('Connection successful!!')

        except Exception as e:
            print('Can not connect to %s' % self.db_to_create)
            print(e)

    def __del__(self):
        return

    # Check if db exists, if not create
    def check_db_exists_create(self):
        dbfile = os.path.join(self.mariadb_root, self.db_to_create)
        if not os.path.exists(dbfile):
            try:
                cur = self.conn.cursor()
                command = "CREATE DATABASE IF NOT EXISTS %s;" % self.db_to_create
                print(command)
                cur.execute(command)
                print("Database created!", self.db_to_create)

            except Exception as e:
                print("Database creating failed!", self.db_to_create)
                print(e)
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
