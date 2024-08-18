from queue import Queue
from typing import TYPE_CHECKING
from services.image.img_filedata import FileImageData
from services.image.img_metadata import RawImageData

class CameraStore:
    # contructor
    def __init__(self):
        self.img_raw_queue: "Queue[RawImageData]" = Queue()
        self.img_file_queue: "Queue[FileImageData]" = Queue()
        self.gain_sample_img = Queue()

    # Handle for RawImageDb
    #===========================
    def put_img_raw_to_queue(self, imageRaw: RawImageData):
        self.img_raw_queue.put(imageRaw)
        return
    
    def is_img_raw_db_empty(self):
        return self.img_raw_queue.empty()
            
    def get_first_img_raw_from_queue(self):
        return self.img_raw_queue.get(0)
    
    # Handle for FileImageDb
    #===========================
    def put_img_file_to_queue(self, imageFile: FileImageData):
        self.img_file_queue.put(imageFile)
        return
    
    def is_img_file_db_empty(self):
        return self.img_file_queue.empty()
            
    def get_first_img_file_from_queue(self):
        return self.img_file_queue.get(0)
    
    # Handle for Gain Sample Img
    #===========================
    def put_gain_sample_img(self, value):
        self.gain_sample_img.put(value)
        return
    
    def check_gain_sample_img_empty(self):
        return self.gain_sample_img.empty()
    
    def get_gain_sample_img(self):
        return self.gain_sample_img.get(0)