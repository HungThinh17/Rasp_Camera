import time
from threading import Event
from services.camera.camera_store import CameraStore
from services.database.my_sql_database import MySliDatabase
from services.common.system_store import SystemStore

class Database_Service:
    def __init__(self, system_store: SystemStore, stop_event: Event):
        self.system_store = system_store
        self.sli_database: MySliDatabase = system_store.sli_database
        self.camera_store: CameraStore = system_store.camera_store
        self.logger = system_store.logger
        self.stop_event = stop_event

    def database_init(self):
        self.sli_database.create_database()
        self.sli_database.create_table()

    def run(self):
        self.database_init()
        self.system_store.DataBaseState.set_state(4)  # ready

        while not self.stop_event.is_set():
            if not self.camera_store.is_img_file_db_empty():
                image_data = self.camera_store.get_first_img_file_from_queue()
                if image_data:
                    self.sli_database.add_item_to_database(image_data)
            time.sleep(self.system_store.THREAD_SLEEP_1US)

        self.system_store.DataBaseState.set_state(5)  # stop

def database_service_worker(system_store: SystemStore, stop_event: Event):
    try:
        database_service = Database_Service(system_store, stop_event)
        database_service.run()
    except Exception as e:
        system_store.logger.error(f'Error in database service - {e}')
