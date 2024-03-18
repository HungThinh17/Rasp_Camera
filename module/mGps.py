# https://maker.pro/raspberry-pi/tutorial/how-to-use-a-gps-receiver-with-raspberry-pi-4
# https://www.rfwireless-world.com/Terminology/GPS-sentences-or-NMEA-sentences.html 
# https://stackoverflow.com/questions/1134579/smooth-gps-data
# https://thekalmanfilter.com/kalman-filter-explained-simply/
# sudo gpsmon
# sudo cgps -s

#from gps import *
import gps
import time
import os

import serial,time,pynmea2
from module.db_main import dbSLI

def run_GPS(stop, db: dbSLI):
    db.GpsState.set_state(1) # init

    print("run t4")
    #try:
    port = '/dev/serial0'
    baud = 9600

    serialPort = serial.Serial(port, baudrate = baud, timeout = 0.5)

    db.GpsState.set_state(2) # ready
    while True:
        
        db.GpsState.set_state(4) # running

        str = ''
        try:
            str = serialPort.readline().decode().strip()
        except Exception as e:
            db.GpsState.set_state(3) # error
            print(e)
        
        if str.find('RMC') > 0: # GGA
            try:
                msg = pynmea2.parse(str)
                # RMC msg
                #print(msg.datetime.date(), "ngay ",msg.datetime.day, "thang ",msg.datetime.month, "nam ",msg.datetime.year)
                #db.set_datetime_now(msg.datetime)
                db.set_year_now(msg.datetime.year)
                db.set_month_now(msg.datetime.month)
                db.set_day_now(msg.datetime.day)
                db.set_speed_now(msg.spd_over_grnd * 1.852) # knot to km/h: horizontal speed

                #print(msg.datetime.date(), "ngay ",db.day_now, "thang ",db.month_now, "nam ",db.year_now)
            except Exception as e:
                print(e)
    
        if str.find('GGA') > 0: # GGA
            try:
                msg = pynmea2.parse(str)
                if msg.altitude == None:
                    msg.altitude = 0
                # GGA msg
                print(msg.timestamp,'Lat:',round(msg.latitude,6),'Lon:',round(msg.longitude,6),'Alt:',msg.altitude,'Sats:',msg.num_sats, 'Speed: ', db.speed_now)
                db.set_hour_now(msg.timestamp.hour)
                db.set_minute_now(msg.timestamp.minute)
                db.set_second_now(msg.timestamp.second)
                
                db.set_lat_now(msg.latitude)
                db.set_lon_now(msg.longitude)
                db.set_alt_now(msg.altitude)
                db.set_numsat_now(msg.num_sats)
                db.set_reset_msec(True)
                
            except Exception as e:
                print(e)

        if stop():
            db.GpsState.set_state(5) # stop
            break
        
        time.sleep(0.1)


"""
def run_GPS(stop):
    print("run t4")
    #try:
    
    
    #os.system('sudo systemctl stop gpsd.socket')
    time.sleep(1)
    #os.system('sudo gpsd /dev/serial0 -F /var/run/gpsd.sock')
    time.sleep(1)
    print ("Application started!")

    session = gps.gps(mode=gps.WATCH_ENABLE)

    while 1:
        session.read()

        if not (gps.MODE_SET & session.valid):
            # not useful, probably not a TPV message
            continue

        print('Mode: %s(%d) Time: ' %
              (("Invalid", "NO_FIX", "2D", "3D")[session.fix.mode],
               session.fix.mode), end="")
        # print time, if we have it
        if session.valid:#gps.TIME_SET & session.valid:
            print(session.fix.time, end="")
        else:
            print('n/a', end="")

        if ((gps.isfinite(session.fix.latitude) and
             gps.isfinite(session.fix.longitude))):
            print(" Lat %.6f Lon %.6f" %
                  (session.fix.latitude, session.fix.longitude))
        else:
            print(" Lat n/a Lon n/a")
   
        if stop():
            break

        #time.sleep(0.1)

"""
"""

def run_GPS(stop):
    print("run t4")
    #try:
    
    
    #os.system('sudo systemctl stop gpsd.socket')
    time.sleep(1)
    #os.system('sudo gpsd /dev/serial0 -F /var/run/gpsd.sock')
    time.sleep(1)
    print ("Application started!")

    gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

    while 1:
        nx = gpsd.next()
        # For a list of all supported classes and fields refer to:
        # https://gpsd.gitlab.io/gpsd/gpsd_json.html
        if nx['class'] == 'TPV':
            latitude = getattr(nx,'lat', "Unknown")
            longitude = getattr(nx,'lon', "Unknown")
            altitude = getattr(nx,'altHAE', "Unknown")
            #timeUTC = getattr(nx,'time', "Unknown")
            #speed = getattr(nx,'speed', "Unknown")
            print ("Your position: lon = " + str(longitude) + ", lat = " + str(latitude) + ", alt = " + str(altitude) +
                ", time = ")# + timeUTC)# + ", speed = " + str(speed))
        
        time.sleep(0.1)

        if stop():
            break

    #except:
    #    print ("Applications closed!")
"""
