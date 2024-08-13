# https://maker.pro/raspberry-pi/tutorial/how-to-use-a-gps-receiver-with-raspberry-pi-4
# https://www.rfwireless-world.com/Terminology/GPS-sentences-or-NMEA-sentences.html 
# https://stackoverflow.com/questions/1134579/smooth-gps-data
# https://thekalmanfilter.com/kalman-filter-explained-simply/
# sudo gpsmon
# sudo cgps -s

import time
import serial, time, pynmea2

from module.db_main import dbSLI

def run_GPS(stop, db: dbSLI):
    print("run t4")

    db.GpsState.set_state(1) # init
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
                db.set_year_now(msg.datetime.year)
                db.set_month_now(msg.datetime.month)
                db.set_day_now(msg.datetime.day)
                db.set_speed_now(msg.spd_over_grnd * 1.852) # knot to km/h: horizontal speed
            except Exception as e:
                print(e)
    
        if str.find('GGA') > 0: # GGA
            try:
                msg = pynmea2.parse(str)
                if msg.altitude == None:
                    msg.altitude = 0
                
                # GGA msg
                print(msg.timestamp,'Lat:',round(msg.latitude,6),'Lon:',round(msg.longitude,6),'Alt:',msg.altitude,'Sats:',msg.num_sats, 'Speed: ', db.speed_now)
                
                # Set time info
                db.set_hour_now(msg.timestamp.hour)
                db.set_minute_now(msg.timestamp.minute)
                db.set_second_now(msg.timestamp.second)

                # Set GPS info
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
