# https://maker.pro/raspberry-pi/tutorial/how-to-use-a-gps-receiver-with-raspberry-pi-4
# https://www.rfwireless-world.com/Terminology/GPS-sentences-or-NMEA-sentences.html 
# https://stackoverflow.com/questions/1134579/smooth-gps-data
# https://thekalmanfilter.com/kalman-filter-explained-simply/
# sudo gpsmon
# sudo cgps -s

import time
import serial
import pynmea2
from threading import Event
from services.gps.gps_data import GPSCaptureData
from services.common.system_store import SystemStore

class GPS_Service:
    def __init__(self, system_store: SystemStore, stop_event: Event):
        self.system_store = system_store
        self.stop_event = stop_event
        self.logger = system_store.logger

    def run(self):
        port = '/dev/serial0'
        baud = 9600

        self.system_store.GpsState.set_state(1) # init
        serialPort = serial.Serial(port, baudrate=baud, timeout=0.5)
        self.system_store.GpsState.set_state(2) # ready
        gpsData = GPSCaptureData()

        while not self.stop_event.is_set():
            self.system_store.GpsState.set_state(4) # running
            str_data = serialPort.readline().decode().strip()
            
            if str_data.find('RMC') > 0: # GGA
                msg = pynmea2.parse(str_data)
                # RMC msg
                gpsData.set_year_now(msg.datetime.year)
                gpsData.set_month_now(msg.datetime.month)
                gpsData.set_day_now(msg.datetime.day)
                spd_over_grnd = msg.spd_over_grnd if msg.spd_over_grnd is not None else 0
                gpsData.set_speed_now(spd_over_grnd * 1.852) # knot to km/h: horizontal speed
                self.system_store.set_gps_captured_data(gpsData)
        
            if str_data.find('GGA') > 0: # GGA
                msg = pynmea2.parse(str_data)
                if msg.altitude is None:
                    msg.altitude = 0
                
                # GGA msg
                self.logger.info(f"{msg.timestamp} Lat: {round(msg.latitude, 6)} Lon: {round(msg.longitude, 6)} Alt: {msg.altitude} Sats: {msg.num_sats} Speed: {gpsData.speed_now}")
                
                # Set time info
                gpsData.set_hour_now(msg.timestamp.hour)
                gpsData.set_minute_now(msg.timestamp.minute)
                gpsData.set_second_now(msg.timestamp.second)

                # Set GPS info
                gpsData.set_lat_now(msg.latitude)
                gpsData.set_lon_now(msg.longitude)
                gpsData.set_alt_now(msg.altitude)
                gpsData.set_numsat_now(msg.num_sats)
                gpsData.set_reset_msec(True)
                self.system_store.set_gps_captured_data(gpsData)
                    
            self.system_store.GpsState.set_state(5) # stop
            time.sleep(0.1)
        return

def gps_service_worker(system_store: SystemStore, stop_event: Event):
    try:
        gps_service = GPS_Service(system_store, stop_event)
        gps_service.run()
    except Exception as e:
        system_store.GpsState.set_state(3) # error
        system_store.logger.error(f"Error in GPS service: {e}")
