#!/usr/bin/env python

# Command line tools
import optparse

# Config file tools
import ConfigParser

# Logger library
import logging, logging.config

# Other
import datetime

# Local files
import hockey_email, event_utils, email_utils

# Todo:
# - Add exception handlers, and a logger that will email you when there is a problem
# - Add error handling for some problems, like missing files, or whatever.

if __name__ == '__main__':  
  logging.config.fileConfig('/home/pi/.hockey/log.cfg')
  logger = logging.getLogger('schedule_hockey')
  logger.info('Starting schedule_hockey.py')
  
  config = ConfigParser.RawConfigParser()
  config.read('/home/pi/.hockey/config')
  dow = int(config.get('HOCKEY_EMAIL','DAY_OF_WEEK'))

  location = event_utils.HockeyLocation(config.get('HOCKEY_EMAIL', 'LOCATION_NAME'),
                                        config.get('HOCKEY_EMAIL', 'LAT_LON').split()[0],
                                        config.get('HOCKEY_EMAIL', 'LAT_LON').split()[1])

  tomorrow = datetime.date.today() + datetime.timedelta(1)
  if (tomorrow).weekday() == dow:
    logger.info('Today is a good day to email')
    email = hockey_email.HockeyEmail(tomorrow, location)
    subject = email.GetSubject()
    email_to = config.get('HOCKEY_EMAIL', 'EMAIL_TO')
    if email.mEvent.mSunset.hour < 18:
      logger.info('not sending the email because it\'s going to be dark before 6:00. sunset: ' + str(email.mEvent.mSunset)) 
      email_to = config.get('HOCKEY_EMAIL', 'EMAIL_FROM')
      subject = 'No Time for hockey tomorrow ' + subject 
    else:
      logger.info('Sending email with subject:' + email.GetSubject() + '\nmessage:\n' + email.GetBody())

    email_utils.sendemail(from_addr    = config.get('HOCKEY_EMAIL', 'EMAIL_FROM'), 
                          to_addr_list = [email_to],
                          cc_addr_list = [''],
                          subject      = subject, 
                          message      = email.GetBody(), 
                          login        = config.get('HOCKEY_EMAIL', 'EMAIL_LOGIN'),
                          password     = config.get('HOCKEY_EMAIL', 'EMAIL_PASSWORD'))
  else:
    logger.info('Not emailng today, because tomorrow is %d and you want %d' % (tomorrow.weekday() , dow))
