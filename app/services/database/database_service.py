import time
from multiprocessing import Queue
from services.common.shared_keys import SharedKey
from services.database.my_sql_database import MySliDatabase
from services.common.system_store import SystemStore

class Database_Service:
    def __init__(self, system_store, stop_event, shared_data_queue: Queue, sli_database: MySliDatabase):
        self.system_store:SystemStore =system_store
        self.stop_event = stop_event
        self.shared_data_queue = shared_data_queue
        self.sli_database = sli_database
        self.db_cursor = None

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
        while not self.stop_event:
            image_data = self.shared_data_queue.get()
            # check list img data system_store not empty
            if image_data:
                try:
                    print ("have data for database")
                    statement = "INSERT INTO sli_info (deviceID, imgID, date, time, lat, lon, alt, numSat) VALUES  (%s,%s,%s,%s,%s,%s,%s,%s);"
                    val = (
                        image_data.deviceID,image_data.imgID, image_data.imgDate, \
                        image_data.imgTime, image_data.lat, image_data.lon, image_data.alt, image_data.numSat
                    )
                    self.db_cursor.execute(statement, val)
                    self.sli_database.conn.commit()
                    print("__",statement)
                except Exception as e:
                    print(e)
            time.sleep(0.001)

        if self.stop_event:
            self.system_store.DataBaseState.set_state(5) # stop

        self.db_cursor.close()
        self.sli_database.conn.close()

def database_service_worker(system_store, stop_event, shared_data_queue, sli_database):
    database_service = Database_Service(system_store, stop_event, shared_data_queue, sli_database)
    database_service.run()