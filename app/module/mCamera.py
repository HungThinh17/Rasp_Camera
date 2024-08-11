import time
import math
import numpy as np
import os.path

from datetime import datetime, timezone
from picamera2 import *
from PIL import Image as im
from simple_pid import PID
from module.db_main import dbSLI
from module.db_img_metadata import dbImgMetadata

##=====================================================
tuning = Picamera2.load_tuning_file("imx477.json")

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
    roi = img[:4056, 1216:3040, :] # 1216 = 3040*2/5
    return np.dot(roi[...,:3], [.3, .6, .1])

##=====================================================
def image_brightness_grey(img):
    img_grey = rgb_to_grey(img)
               
    return np.average(img_grey)

##=====================================================
def run_picamera(stop, db: dbSLI):
    print("run t1")
    with Picamera2(tuning=tuning) as camera: 
        db.cameraState.set_state(1) # init
        
        config = camera.create_still_configuration()#main={"size": (4056, 3040)})#,"format": "RGB888"}, raw={"format": "SRGGB12", "size" : (2032, 1520)})
        camera.configure(config)
        camera.set_controls({"ExposureTime": db.camPara.ExposureTime, "AnalogueGain": db.camPara.AnalogGain})
        camera.start()
        time.sleep(1)
        
        print("Camera initializing finish")
        print("Waiting capture signal")

        db.cameraState.set_state(2) # ready
        print ("came OK")
        
        while 1: #here waiting for capture signal
            #print (db.cameraState) 
            db.cameraState.set_state(4) # running

            if db.camPara.update == True:
                camera.set_controls({"AnalogueGain": db.camPara.AnalogGain})
                db.camPara.clear_update()

            if db.camera_gain_sample:
                db.clear_camera_gain_sample()

                
                # capture img
                image_arr = camera.capture_array()
                db.put_gain_sample_img(image_arr)

                

            #state = capture_signal
            if db.get_camera_ctrl_signal():
                print("capture now")
                db.clear_camera_ctrl_signal()
                
                # temp id picture
                #db.increse_img_ID(1)
                #picture_id = db.get_img_ID()
                #db.put_image_ID_to_queue(picture_id)
                
                t1 = time.perf_counter()
                
                
                # capture img
                image_arr = camera.capture_array()

                

                # put to imga arr queue
                #db.put_image_array_to_queue(image_arr)

                metadata = Metadata(camera.capture_metadata())

                # create img metadata class and add to queue
                

                db.set_img_data(img_arr= image_arr, year= db.year_now, month = db.month_now, day = db.day_now,
                                hour = db.hour_now, min = db.minute_now, sec = db.second_now, msec = int(db.msec_now / 10),
                                lat =db.lat_now, lon = db.lon_now, alt = db.alt_now, numSat = db.numsat_now)

                # input new img to show on GUI
                db.imgGUI.set_lastImg(image_arr)
                db.imgGUI.set_newImg(True)
                # convert gray scale brightness value
                #grey_brightness = image_brightness_grey(image_arr)
                                            
                t2 = time.perf_counter()
                #sens_temp = image_arr["SensorTemperature"]
                print("Capture", "Brightness: ", db.get_last_img_grey_brightness(), "Gain: ", db.camPara.AnalogGain," time: ", t2-t1)#, "lux:", lux)#, " sensor temp:", sens_temp)
                #print(metadata.ExposureTime, metadata.AnalogueGain)
                
            if stop():
                db.cameraState.set_state(5) # stop
                break
            
            time.sleep(0.01)
            
        camera.stop()

##=====================================================
def convert_array_to_file(stop, db: dbSLI):
    print("run t2")
    # Create a current date directory to save image
    #dirname = YYYYs + MMs + DDs #+ HHs
    dirname1 = ""
    dirname2 = ""
        
    while 1:
        
        if db.year_now != 0:
            dirname1 = str(db.year_now).zfill(4) + str(db.month_now).zfill(2) + str(db.day_now).zfill(2) 
            symlink_path = os.path.join(os.path.dirname(__file__),"../storeImages")

            path = os.path.join(symlink_path, dirname1)

            if not os.path.isdir(path):
                # if dir not exist -> create dir
                os.mkdir(path)
                print ("my path dir ", path)

        if not db.check_img_data_empty():# list_image_array.empty():
            
            img_data = db.get_img_data_0()
            img = img_data.img_arr
            # image id
            #id = db.get_image_ID_from_queue()
            # image file name
            dirname2 = str(img_data.img_hour).zfill(2) + str(img_data.img_min).zfill(2) + str(img_data.img_sec).zfill(2) + str(img_data.img_msec).zfill(2)
            filename = dirname1 + dirname2
            # creating image object of above array
            data = im.fromarray(img)
            data.save(path + "/" + filename + ".jpeg")

            # create data for img DB
            db.set_img_data_db(db.CPU_serial, filename, dirname1, dirname2, img_data.img_lat, img_data.img_lon, img_data.img_alt, img_data.img_numSat)

        if stop():
            break
        
        time.sleep(0.1)


##=====================================================
## https://pypi.org/project/simple-pid/ 

def auto_gain_PID(stop, SP, db: dbSLI):
    # set kp =5, ki =2, kd = 1, setpoint = SP (normally = 40) setpoint is best value grey brightness
    pid = PID(0.02, 0.005, 0.01, setpoint=SP)
    # limit gain value from 5 to 200
    pid.output_limits = (1, 200) 
    # eliminate overshoot
    pid.proportional_on_measurement = True

    #pid.auto_mode = False
    pid.sample_time = 0.01
    
    while 1:
        # calculate grey brightness of the last image.
        if not db.check_gain_sample_img_empty():
            # get last image
            n = db.queue_image_array.qsize()
            last_img = db.get_gain_sample_img()
            # calculate grey brightness
            grey_brightness = image_brightness_grey(last_img)
            db.set_last_img_grey_brightness(grey_brightness)
            # PID
            #pid.set_auto_mode(True, last_output=db.get_last_img_grey_brightness())            
            newGain = pid(grey_brightness)
            #newGain = round(newGain, 0)
            #pid.auto_mode = False
            #if abs(newGain - db.camPara.AnalogGain) > 5:
                
            # update new gain
            db.camPara.set_analog_gain(newGain)
            db.camPara.set_update()

            print("Brightness: ", grey_brightness, "Gain: ", newGain)

        if stop():
            break
        
        time.sleep(0.1)