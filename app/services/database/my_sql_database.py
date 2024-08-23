from __future__ import annotations

import os
import pymysql
from pymysql.cursors import DictCursor
from threading import Lock
from contextlib import contextmanager
from typing import List
from services.image.img_filedata import FileImageData

class MySliDatabase:
    def __init__(self) -> None:
        self.host = 'localhost'
        self.user = 'hungnp'
        self.password = '1'
        self.db_name = 'slidb'
        self.db_table_name = 'sli_info'
        self.db_root_path = os.path.join(os.getcwd(), 'data/db/')
        self.lock = Lock()
        self.connection_pool = self._create_connection_pool()

    def _create_connection_pool(self):
        try:
            return pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db_name,
                cursorclass=DictCursor,
                autocommit=False
            )
        except Exception as e:
            print(f'Cannot connect to {self.db_name}')
            print(e)
            raise

    @contextmanager
    def get_connection(self):
        if self.connection_pool.open:
            yield self.connection_pool
        else:
            new_connection = self._create_connection_pool()
            try:
                yield new_connection
            finally:
                new_connection.close()

    def create_database(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SHOW DATABASES LIKE %s", (self.db_name,))
                if cur.fetchone():
                    print(f"Database {self.db_name} already exists")
                else:
                    cur.execute(f"CREATE DATABASE {self.db_name}")
                    print(f"Database {self.db_name} created successfully")

    def create_table(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
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
                        file_path varchar(255),
                        PRIMARY KEY (imgID)
                    )"""
                    cur.execute(create_table_sql)
                    print(f"Table {self.db_table_name} created successfully")

    def add_item_to_database(self, image_data: FileImageData):
        with self.lock:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        statement = f"INSERT INTO {self.db_table_name} (deviceID, imgID, date, time, lat, lon, alt, numSat, file_path) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                        val = (
                            image_data.deviceID, image_data.imgID, image_data.imgDate, image_data.imgTime, 
                            image_data.lat, image_data.lon, image_data.alt, image_data.numSat, image_data.file_path
                        )
                        cursor.execute(statement, val)
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        raise e

    def row_to_img_data(self, row: dict) -> FileImageData:
        return FileImageData(
            deviceID=row['deviceID'],
            imgID=row['imgID'],
            imgDate=row['date'],
            imgTime=row['time'],
            lat=row['lat'],
            lon=row['lon'],
            alt=row['alt'],
            numSat=row['numSat'],
            file_path=row['file_path']
        )
    
    def get_number_of_items(self) -> int:
        with self.lock:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {self.db_table_name}")
                    return cursor.fetchone()['COUNT(*)']

    def get_all_items_as_img_data(self) -> List[FileImageData]:
        with self.lock:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT * FROM {self.db_table_name}")
                    return [self.row_to_img_data(row) for row in cursor.fetchall()]

    def remove_item(self, img_id: str):
        with self.lock:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(f"DELETE FROM {self.db_table_name} WHERE imgID = %s", (img_id,))
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        raise e

    def remove_all_items(self):
        with self.lock:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(f"TRUNCATE TABLE {self.db_table_name}")
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        raise e
