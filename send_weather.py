from pysky import forecast
from datetime import date
import commands
from astral import Astral


def getweather():
  result = forecast.get_forecast(39.54,-104.96,True)
  line = ''
  for data in result['hourly']:
    #print data
    if data['date'] == str(date.today()):
      line += '\nWeather for %s at %s' %(data['date'], data['time']) 
      if data.has_key('weather'):
        line += ' report: %s.' %data['weather']
      if data.has_key('temp'):
        line += ' temp: %sF. ' %data['temp']
      if data.has_key('rain_amount'):
        line += ' rain: %s.' %data['rain_amount']

  return line

def getsun():
    city_name='Denver'
    a = Astral()
    city = a[city_name]
    sun = city.sun(date=date.today(),local=True)
    line =  'Sunset:  %s\n' % str(sun['sunset'])
    line += 'Dusk:    %s\n' % str(sun['dusk'])
    return line


def getbody():
  line ='\n\nWeather Today:'
  line += getweather()
  line +='\n\nYour Fortune Today:\n'
  #line += commands.getoutput('/usr/games/fortune')
  line += "Insert Jeff's snide remark for not coming here."
  line += '\n\n'
  line += 'Sun Stuff:\n'
  line += getsun()
  line += '\n'
  line += 'Enjoy!\nSean'
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
  
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

if __name__ == '__main__':

    sendemail(from_addr    = '******@gmail.com', 
            to_addr_list = ['hockeyoutdoors@googlegroups.com'],
            cc_addr_list = [''], 
            subject      = 'Hockey: Who''s In? Tuesday '+str(date.today()), 
            message      = getbody(),
            login        = '********', 
            password     = '********')

