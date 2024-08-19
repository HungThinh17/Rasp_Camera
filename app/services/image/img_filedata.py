from __future__ import annotations

import os
import time
import pymysql
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.common.system_store import SystemStore

class FileImageData:
    def __init__(self, deviceID, imgID, imgDate, imgTime , lat, lon, alt, numSat) -> None:
        self.deviceID = deviceID
        self.imgID = imgID
        self.imgDate = imgDate
        self.imgTime = imgTime
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.numSat = numSat

    def set_deviceID(self, val):
        self.deviceID = val
        return
    
    def set_imgID(self, val):
        self.imgID = val
        return
    
    def set_imgDate(self, val):
        self.imgDate = val
        return
    
    def set_imgTime(self, val):
        self.imgTime = val
        return
    
    def set_lat(self, val):
        self.lat = val
        return
    
    def set_lon(self, val):
        self.lon = val
        return

    def set_alt(self, val):
        self.alt = val
        return
    
    def set_numSat(self, val):
        self.numSat = val
        return
