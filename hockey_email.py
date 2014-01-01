from pysky import forecast
from datetime import date
from datetime import timedelta 
from datetime import datetime 
import commands
from astral import Astral
import json
import random

def getweather(date):
  result = forecast.get_forecast(39.53,-104.99,True)
  line = '\nWeather for ' + date.strftime('%A %B %e') + ' at (39.53, -104.99):\n'
  result = json.loads(result)
  for data in result['daily']:
    if data['date'] == str(date):
      #print 'Daily',data
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
    if data['date'] == str(date):
      #print 'Hourly',data
      time = datetime.strptime(data['time'], '%H:%M:%S')
      if abs(time.hour - 17) > 3:
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

def getsun(date):
    city_name='Denver'
    a = Astral()
    city = a[city_name]
    sun = city.sun(date=date, local=True)
    #print 'sun:',sun
    line =  'Sunset:  %s\n' % (sun['sunset'].strftime('%l:%M'))
    line += 'Dusk:    %s\n' % (sun['dusk'].strftime('%l:%M'))
    return line


def getSnideRemark():
  remarks = [
    'If you don\'t come to hockey today, you\'ll regret it',
    'Hockey is the best exercise',
    'Forget the weather, just come and play hockey',
    'Don\'t you want to be cool like the other kids? They all play hockey'
    'Please reply immediately, or no one will know you want to come, and they will say no. Then no one will come. Then people will stop caring. Then hockey will end.',
    'If you don\'t come to hockey, then no one will. You are the only person that matters at all.',
    'Obesity in America hit an all time record today.',
    'Only you can prevent soccer kids from playing on hockey rinks.',
    'Participation is mandatory. Ed said so, and he\'s your boss.',
  ]
  random.seed()
  return random.choice(remarks)

def getbody(day):
  line = getSnideRemark() + '\n'
  line += getweather(day)
  line += '\n\n'
  line += 'Sun Stuff:\n'
  line += getsun(day)
  line += '\n'
  line += 'Enjoy!\n--Hockey Robot created by Sean Gooding and Jeff Eberl'
  return line

import smtplib
  
def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    #print 'Header',header
    #print 'Message:\n',message
    #return
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

if __name__ == '__main__':
    
    day = date.today()
    #print getweather(day)
    day += timedelta(1)
    #print getweather(day)
    #day += timedelta(1)
    #print getweather(day)
    #day += timedelta(1)
    #print getweather(day)
    sendemail(from_addr    = 'jeffeb3@gmail.com', 
              to_addr_list = ['jeffeb3@gmail.com'],
              #to_addr_list = ['hockeyoutdoors@googlegroups.com'],
              cc_addr_list = [''], 
              subject      = 'Who\'s In? Tanks Park, ' + day.strftime('%A %B %e'),
              message      = getbody(day),
              login        = 'jeffeb3',
              password     = 'uyvsojijljalddww')

