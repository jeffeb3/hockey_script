from pysky import forecast
from astral import Astral
import json
import datetime

import logging
logger = logging.getLogger('event_utils')

class HockeyLocation():
  def __init__(self, name, lat, lon):
    self.mName = name
    self.mLat = float(lat)
    self.mLon = float(lon)

class HockeyEvent():
  def __init__(self, day, time, location):
    self.mDay = day
    self.mTime = time
    self.mHour = int(float(time))
    self.mLocation = location

    self.mWeatherText = self.SetWeather()
    self.SetSunStuff()
   
  def SetWeather(self):
    result = forecast.get_forecast(self.mLocation.mLat,self.mLocation.mLon,True)
    result = json.loads(result)
    line = '\nWeather for ' + self.mDay.strftime('%A %B %e') + ' at ' + self.mLocation.mName + ' (' + str(self.mLocation.mLat) + ',' + str(self.mLocation.mLon) + '):\n'
    for data in result['daily']:
      if data['date'] == str(self.mDay):
        logger.debug('Daily' + str(data))
        if data.has_key('weather') and len(data['weather']) != 0:
          line += data['weather'] + '.\n'
        if data.has_key('high') and data.has_key('low'):
          line += 'Temp: %sF/%sF.\n' %(data['high'], data['low'])
        if data.has_key('wind_gust') and data.has_key('wind_sustained'):
          line += 'Wind: %s MPH (gust) and %s MPH (sustained).\n' %(data['wind_gust'],data['wind_sustained'])
        precip_line = False
        if data.has_key('precip_day'):
          line += '%s%% chance of precipitation.' %data['precip_day']
          precip_line = True
        if data.has_key('rain_amount') and float(data['rain_amount']) > 0:
          line += ' rain: %s in.' %data['rain_amount']
          precip_line = True
        if data.has_key('snow_amount') and float(data['snow_amount']) > 0:
          line += ' snow: %s in.' %data['snow_amount']
          precip_line = True
        if precip_line:
          line += '\n'
  
    line += '\nHourly:'
    for data in result['hourly']:
      if data['date'] == str(self.mDay):
        logger.debug('Hourly:' + str(data))
        time = datetime.datetime.strptime(data['time'], '%H:%M:%S')
        if abs(time.hour - self.mHour) > 3:
          continue
        line += '\n%s' %(time.strftime('%l:%M %p')) 
        if data.has_key('temp'):
          line += '  temp: %sF.' %data['temp']
        if data.has_key('wind_gust') and data.has_key('wind_sustained'):
          line += '  wind: % 4s/% 4s.' %(data['wind_gust'],data['wind_sustained'])
        if data.has_key('sky'):
          line += '  %s%% cloud cover.' %data['sky']
        if data.has_key('precip'):
          line += '  %s%% chance of precipitation.' %data['precip']
        if data.has_key('rain_amount') and float(data['rain_amount']) > 0:
          line += ' rain: %s in.' %data['rain_amount']
        if data.has_key('snow_amount') and float(data['snow_amount']) > 0:
          line += ' snow: %s in.' %data['snow_amount']
        if data.has_key('weather') and len(data['weather']) != 0:
          line += '  %s.' %(data['weather'])
  
    return line

  def GetWeather(self):
    return self.mWeatherText

  def SetSunStuff(self):
    city_name='Denver'
    a = Astral()
    city = a[city_name]
    sun = city.sun(date=self.mDay, local=True)
    self.mSunset = sun['sunset']
    self.mDusk = sun['dusk']

  def GetSun(self):
    line =  'Sunset:  %s\n' % (self.mSunset.strftime('%l:%M'))
    line += 'Dusk:    %s\n' % (self.mDusk.strftime('%l:%M'))
    return line

