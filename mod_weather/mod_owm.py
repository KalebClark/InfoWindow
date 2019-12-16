import requests
from datetime import datetime as dt
import os
import json
import math
from PIL import Image
import logging


class Weather:
    def __init__(self, options):
        logging.debug("Weather API: Open Weather Map")
        self.api_key = options['api_key']
        self.icon_path = "icons/"
        self.city = options['city']
        self.units = options['units']

    def pngToBmp(self, icon):
        img = Image.open(self.icon_path+str(icon))
        r,g,b,a = img.split()
        # img.merge("RGB", (r, g, b))
        basename = os.path.splitext(icon)[0]
        img = img.convert('1')
        img.save(self.icon_path+basename+".bmp")
        return basename+".bmp"

    def getIcon(self, iconUrl):
        # check for icon
        bn = os.path.basename(iconUrl)
        for root, dirs, files in os.walk(self.icon_path):
            if not bn in files:
                with open(self.icon_path+bn, "wb") as file:
                    response = requests.get(iconUrl)
                    file.write(response.content)
                file.close()
        
        return self.pngToBmp(bn)

    def degreesToTextDesc(self, deg):
        if deg > 337.5: return u"N"
        if deg > 292.5: return u"NW"
        if deg > 247.5: return u"W"
        if deg > 202.5: return u"SW"
        if deg > 157.5: return u"S"
        if deg > 122.5: return u"SE"
        if deg >  67.5: return u"E"
        if deg >  22.5: return u"NE"
        return u"N"

    def list(self):
        url = 'http://api.openweathermap.org/data/2.5/weather'
        r = requests.get('{}?q={}&units={}&appid={}'.format(url, self.city, self.units, self.api_key))

        data = r.json()

        # Sunrise and Sunset.
        if self.units == "imperial":
            sunrise = dt.fromtimestamp(data['sys'].get('sunrise')).strftime('%I:%M %p')
            sunset  = dt.fromtimestamp(data['sys'].get('sunset')).strftime('%I:%M %p')
        else:
            sunrise = dt.fromtimestamp(data['sys'].get('sunrise')).strftime('%H:%M')
            sunset  = dt.fromtimestamp(data['sys'].get('sunset')).strftime('%H:%M')

        # Rain and Snow
        wTypes = ['rain', 'snow']
        for wType in wTypes:
            # Check to see if dictionary has values for rain or snow.
            # if it does NOT, set zero values for consistancy.
            if data.has_key(wType):
                setattr(self, wType, {
                    "1h": data[wType].get('1h'),
                    "3h": data[wType].get('3h')
                })
            else:
                setattr(self, wType, {
                    "1h": 0,
                    "3h": 0
                })

        # Fetch Wind Data
        wind = {
            "dir": self.degreesToTextDesc(data['wind'].get('deg')),
            "speed": int(round(data['wind'].get('speed')))
            #"speed": 33
        }

        #icon = self.getIcon("http://openweathermap.org/img/wn/"+data['weather'][0].get('icon')+".png")
        icon = os.path.basename(data['weather'][0].get('icon'))+".bmp"

        return {
            "description": data['weather'][0].get('description'),
            "humidity": data['main'].get('humidity'),
            "temp_cur": int(math.ceil(data['main'].get('temp'))),
            #"temp_cur": int(9),
            "temp_min": int(math.ceil(data['main'].get('temp_min'))),
            "temp_max": int(math.ceil(data['main'].get('temp_max'))),
            #"temp_min": int(100),
            #"temp_max": int(112),
            "sunrise": sunrise,
            "sunset": sunset,
            "rain": self.rain,
            "snow": self.snow,
            "wind": wind,
            "icon": icon
        }


        

