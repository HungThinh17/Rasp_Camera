import time
from threading import Event
from services.camera.camera_store import CameraStore
from services.database.my_sql_database import MySliDatabase
from services.common.system_store import SystemStore

class Database_Service:
    def __init__(self, system_store: SystemStore, stop_event: Event, sli_database: MySliDatabase):
        self.system_store = system_store
        self.camera_store: CameraStore = system_store.camear_store
        self.stop_event = stop_event
        self.sli_database = sli_database
        self.db_cursor = None
        self.logger = system_store.logger

    def database_init(self):
        # check and create DB
        self.sli_database.check_db_exists_create() 
        # check and create table
        self.sli_database.create_table()
        # use table
        self.db_cursor = self.sli_database.conn.cursor()
        command = "use %s; " % self.sli_database.db_to_create
        self.db_cursor.execute(command)
    
    def run(self):
        self.database_init()
        self.system_store.DataBaseState.set_state(4) # ready

        # infinite loop add data to table
        while not self.stop_event.is_set():
            if not self.camera_store.is_img_file_db_empty():
                image_data = self.camera_store.get_first_img_file_from_queue()
                # check list img data system_store not empty
                if image_data:
                    self.logger.info(f"{__class__.__name__}:have data for database")
                    statement = "INSERT INTO sli_info (deviceID, imgID, date, time, lat, lon, alt, numSat) VALUES  (%s,%s,%s,%s,%s,%s,%s,%s);"
                    val = (
                        image_data.deviceID, image_data.imgID, image_data.imgDate, \
                        image_data.imgTime, image_data.lat, image_data.lon, image_data.alt, image_data.numSat
                    )
                    self.db_cursor.execute(statement, val)
                    self.sli_database.conn.commit()
                    self.logger.info(f"{__class__.__name__}:__" + statement)
                time.sleep(0.001)

        self.system_store.DataBaseState.set_state(5) # stop
        self.db_cursor.close()
        self.sli_database.conn.close()

def database_service_worker(system_store: SystemStore, stop_event: Event, sli_database: MySliDatabase):
    try:
        database_service = Database_Service(system_store, stop_event, sli_database)
        database_service.run()
    except Exception as e:
        system_store.logger.error(f'Error in data base server - {e}')
