from __future__ import annotations

import os
import pymysql
from services.image.img_filedata import FileImageData # type: ignore

class MySliDatabase:
    def __init__(self) -> None:
        self.host = 'localhost'
        self.user = 'hungnp'
        self.password = '1'
        self.db_name = 'slidb'
        self.db_table_name = 'sli_info'
        self.db_root_path = os.path.join(os.getcwd(), 'data/db/')

        try:
            self.conn = pymysql.connect(host=self.host, user=self.user, passwd=self.password, cursorclass=pymysql.cursors.DictCursor)
            print('Connection successful!!')
        except Exception as e:
            print(f'Can not connect to {self.db_name}')
            print(e)
            raise e 

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def create_database(self):
        with self.conn.cursor() as cur:
            cur.execute("SHOW DATABASES LIKE %s", (self.db_name,))
            if cur.fetchone():
                print(f"Database {self.db_name} already exists")
            else:
                cur.execute(f"CREATE DATABASE {self.db_name}")
                print(f"Database {self.db_name} created successfully")

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute(f"USE {self.db_name}")
            cur.execute(f"SHOW TABLES LIKE '{self.db_table_name}'")
            if cur.fetchone():
                print(f"Table {self.db_table_name} already exists")
            else:
                create_table_sql = f"""
                CREATE TABLE {self.db_table_name} (
                deviceID varchar(255),
                imgID varchar(255),
                date varchar(255),
                time varchar(255),
                lat varchar(255),
                lon varchar(255),
                alt varchar(255),
                numSat varchar(255),
                PRIMARY KEY (imgID)
                )
                """
                cur.execute(create_table_sql)
                print(f"Table {self.db_table_name} created successfully")

    def add_item_to_database(self, image_data: FileImageData):
        statement = f"INSERT INTO {self.db_table_name} (deviceID, imgID, date, time, lat, lon, alt, numSat) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
        val = (
            image_data.deviceID, image_data.imgID, image_data.imgDate,
            image_data.imgTime, image_data.lat, image_data.lon, image_data.alt, image_data.numSat
        )
        with self.conn.cursor() as cursor:
            cursor.execute(statement, val)
            self.conn.commit()

    def row_to_img_data(self, row):
        return FileImageData(
            deviceID=row['deviceID'],
            imgID=row['imgID'],
            imgDate=row['date'],
            imgTime=row['time'],
            lat=row['lat'],
            lon=row['lon'],
            alt=row['alt'],
            numSat=row['numSat']
        )

    def get_all_items_as_img_data(self):
        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.db_table_name}")
            for row in cursor.fetchall():
                yield self.row_to_img_data(row)

    def remove_item(self, img_id):
        with self.conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM {self.db_table_name} WHERE imgID = %s", (img_id,))
            self.conn.commit()

    def remove_all_items(self):
        with self.conn.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {self.db_table_name}")
            self.conn.commit()
