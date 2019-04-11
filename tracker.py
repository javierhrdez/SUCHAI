
import sys
import time
import datetime
from math import *

import ephem

#https://gist.github.com/andresv/920f7bbf03f91a5967ee
#http://blog.thetelegraphic.com/2012/gps-sattelite-tracking-in-python-using-pyephem/
#https://www.sharebrained.com/2011/10/18/track-the-iss-pyephem/

#https://brainwagon.org/2009/09/27/how-to-use-python-to-predict-satellite-locations/



#1 42788U 17036Z   18241.90286423 +.00001425 +00000-0 +65153-4 0  9992
#2 42788 097.3945 300.5830 0012215 169.9252 190.2231 15.22116615065809

ec1_tle = { "name": "SUCHAI",                  
            "tle1": "1 42788U 17036Z   18241.90286423 +.00001425 +00000-0 +65153-4 0  9992",
            "tle2": "2 42788 097.3945 300.5830 0012215 169.9252 190.2231 15.22116615065809"} 


#http://spel.ing.uchile.cl/20170926-suchai.tle
#ec1_tle = { "name": "SUCHAI",                  
#            "tle1": "1 42788U 17036Z   17269.21852571  .00002361  00000-0  10958-3 0  9990",
#            "tle2": "2 42788  97.4398 327.8516 0010602 282.7619  77.2431 15.20972277 14457"}            

tallinn = ("59.4000", "24.8170", "0")
cdmx = ("19.3854456","-99.1763016", "2200")

class Tracker():
    # http://stackoverflow.com/questions/15954978/ecef-from-azimuth-elevation-range-and-observer-lat-lon-alt

    def __init__(self, satellite, groundstation=("59.4000", "24.8170", "0")):

        self.groundstation = ephem.Observer()
        self.groundstation.lat = groundstation[0]
        self.groundstation.lon = groundstation[1]
        self.groundstation.elevation = int(groundstation[2])

        self.satellite = ephem.readtle(satellite["name"], satellite["tle1"], satellite["tle2"])

    def set_epoch(self, epoch=time.time()):
        ''' sets epoch when parameters are observed '''

        self.groundstation.date = datetime.datetime.utcfromtimestamp(epoch)
        self.satellite.compute(self.groundstation)

    def azimuth(self):
        ''' returns satellite azimuth in degrees '''
        return degrees(self.satellite.az)

    def elevation(self):
        ''' returns satellite elevation in degrees '''
        return degrees(self.satellite.alt)

    def latitude(self):
        ''' returns satellite latitude in degrees '''
        return degrees(self.satellite.sublat)

    def longitude(self):
        ''' returns satellite longitude in degrees '''
        return degrees(self.satellite.sublong)

    def range(self):
        ''' returns satellite range in meters '''
        return self.satellite.range


    def ecef_coordinates(self):
        ''' returns satellite earth centered cartesian coordinates
            https://en.wikipedia.org/wiki/ECEF
        '''
        x, y, z = self._aer2ecef(self.azimuth(), self.elevation(), self.range(), float(self.groundstation.lat), float(self.groundstation.lon), self.groundstation.elevation)
        return x, y, z

    def _aer2ecef(self, azimuthDeg, elevationDeg, slantRange, obs_lat, obs_long, obs_alt):

        #site ecef in meters
        sitex, sitey, sitez = llh2ecef(obs_lat,obs_long,obs_alt)

        #some needed calculations
        slat = sin(radians(obs_lat))
        slon = sin(radians(obs_long))
        clat = cos(radians(obs_lat))
        clon = cos(radians(obs_long))

        azRad = radians(azimuthDeg)
        elRad = radians(elevationDeg)

        # az,el,range to sez convertion
        south  = -slantRange * cos(elRad) * cos(azRad)
        east   =  slantRange * cos(elRad) * sin(azRad)
        zenith =  slantRange * sin(elRad)

        x = ( slat * clon * south) + (-slon * east) + (clat * clon * zenith) + sitex
        y = ( slat * slon * south) + ( clon * east) + (clat * slon * zenith) + sitey
        z = (-clat *        south) + ( slat * zenith) + sitez

        return x, y, z




tracker = Tracker(satellite=ec1_tle, groundstation=cdmx)

#t = 1415459755.08
while 1:
    ts = time.time()
    tracker.set_epoch(ts)
    #tracker.set_epoch(time.time() + 60*45)
    print("ts :", ts ) 
    print("lon: %0.5f " %  tracker.longitude() )  
    print("az   : %0.1f" % tracker.azimuth() )
    print("ele  : %0.1f" % tracker.elevation() ) 
    print("range: %0.0f km" % (tracker.range()/1000) )
    print("lat: %0.5f " %  tracker.latitude() )
    print("lon: %0.5f " %  tracker.longitude() )
       

    time.sleep(0.5)