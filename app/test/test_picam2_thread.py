import time
import math
import numpy as np
import queue
import keyboard
import threading
import os.path
#import datetime

from datetime import datetime, timezone
from picamera2 import *
from PIL import Image as im
from threading import Thread


##=====================================================
tuning = Picamera2.load_tuning_file("imx477.json")

exposures = [50, 100, 150, 250, 400, 650, 1050, 1700, 2750]
gain_def = [5, 10, 20, 50, 100, 200, 400, 800, 1000, 1250, 1600]

list_image_array = queue.Queue()

capture_signal = threading.Event()# False

picture_id = 0

picture_id_queue = queue.Queue()

##=====================================================
dt = datetime.now(timezone.utc)
utc_time = dt.replace(tzinfo=timezone.utc)
utc_timestamp = int(utc_time.timestamp())
utc_timestamps = str(utc_timestamp)

SS = datetime.now(timezone.utc).second
MI = datetime.now(timezone.utc).minute
HH = datetime.now(timezone.utc).hour
DD = datetime.now(timezone.utc).day
MM = datetime.now(timezone.utc).month
YYYY = datetime.now(timezone.utc).year

YYYYs = str(YYYY).zfill(4)
MMs = str(MM).zfill(2)
DDs = str(DD).zfill(2)
HHs = str(HH).zfill(2)


##=====================================================
def rgb_to_grey(img):
    return np.dot(img[...,:3], [.3, .6, .1])

##=====================================================
def image_brightness_grey(img):
    img_grey = rgb_to_grey(img)
               
    return np.average(img_grey)

##=====================================================


##=====================================================
def run_picamera(stop):
    print("run t1")
    with Picamera2(tuning=tuning) as camera: 
        config = camera.create_still_configuration()#main={"size": (4056, 3040)})#,"format": "RGB888"}, raw={"format": "SRGGB12", "size" : (2032, 1520)})
        camera.configure(config)
        camera.set_controls({"ExposureTime": 10000})#, {"AnalogueGain": 200})
        camera.start()
        time.sleep(1)
        
        print("Camera initializing finish")
        print("Waiting capture signal")
        
        while True: #here waiting for capture signal
        #for exp in exposures:
        #for exp in range (10):
            
            #state = capture_signal
            if capture_signal.is_set():
                print("capture now")
                capture_signal.clear()
                
                # temp id picture
                global picture_id
                picture_id +=1
                picture_id_queue.put(picture_id)
                
                t1 = time.perf_counter()
                #camera.set_controls({"AnalogueGain": gain})#, "ColourGains": (1.0,1.0)})
                metadata = camera.capture_array()
                list_image_array.put(metadata)
                            
                t2 = time.perf_counter()
                #sens_temp = metadata["SensorTemperature"]
                print("ID:", picture_id, "Brightness: ", "time: ", t2-t1)#, "lux:", lux)#, " sensor temp:", sens_temp)
            
            if stop():
                break
            
            time.sleep(0.001)
            
        camera.stop()
        

##=====================================================
def convert_array_to_file(stop):
    print("run t2")
    # Create a current date directory to save image
    dirname = YYYYs + MMs + DDs #+ HHs
    symlink_path = "/home/dgmsli/Desktop/test_image"

    path = symlink_path + "/" + dirname

    if not os.path.isdir(path):
        # if dir not exist -> create dir
        os.mkdir(path)
        
    while True:
        if not list_image_array.empty():
            img = list_image_array.get(0)
            id = picture_id_queue.get(0)
            # creating image object of above array
            data = im.fromarray(img)
            # saving the final output a file
            data.save(path + f"/{id}.jpeg")
        
        if stop():
            break
        
        time.sleep(0.05)
        
##=====================================================
# define a main function
def main():      

    print("Hello test camera")
    
    stop_threads = False
    
    # 1. Define thread
    # Thread: capture camera
    t1 = Thread(target=run_picamera, args =(lambda : stop_threads, ))
    # Thread: save image array to file
    t2 = Thread(target=convert_array_to_file, args =(lambda : stop_threads, ))
    # Thread: PID control analog gain
    #t3 = Thread(target=control_analog_gain)
    
    # 2. Run thread
    t1.start()
    t2.start()
    
    # 3. Control program status by keyboard
    while True:
        kb = keyboard.read_key()
        if kb == "a":
            capture_signal.set()
        
        if kb == "c":
            stop_threads = True
            break
            
        time.sleep(0.2)
        
    # 4. waiting thread finish
    t1.join()
    t2.join()
  

##=====================================================
if __name__ == "__main__":
    main()
