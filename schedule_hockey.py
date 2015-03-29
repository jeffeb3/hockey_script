#!/usr/bin/env python

# Main entry point for the cron.

import optparse
import ConfigParser
import logging, logging.config
import datetime
import os
import sys

import hockey_email, event_utils, email_utils

if __name__ == '__main__':  
  logging.config.fileConfig(os.environ['HOME'] + '/.hockey/log.cfg')
  logger = logging.getLogger('schedule_hockey')
  logger.info('Starting schedule_hockey.py')
  
  config = ConfigParser.RawConfigParser()
  config.read(os.environ['HOME'] + '/.hockey/config')
  
  parser = optparse.OptionParser()
  parser.add_option('-d', '--day_of_week', default=None, help='Set to the day of the week, number zero is Monday.')
  parser.add_option('-t', '--time', default=None, help='Set to the time (decimal hours, 24 hours a day. 5:30pm is 17.5')
  parser.add_option('-n', '--dry_run', default=False, action='store_true', help='Set to fake the email, just do everything else.')
  
  options, arguments = parser.parse_args()
  
  if options.day_of_week is None:
    logger.error("No day of week defined.")
    sys.exit(1)

  if options.time is None:
    logger.error("No time defined.")
    sys.exit(1)
  
  dow = int(options.day_of_week)
  time = float(options.time)

  location = event_utils.HockeyLocation(config.get('HOCKEY_EMAIL', 'LOCATION_NAME'),
                                        config.get('HOCKEY_EMAIL', 'LAT_LON').split()[0],
                                        config.get('HOCKEY_EMAIL', 'LAT_LON').split()[1])

  event_day = datetime.date.today()
  while event_day.weekday() != dow:
    event_day = event_day + datetime.timedelta(1)
    
  email = hockey_email.HockeyEmail(event_day, time, location)
  subject = email.GetSubject()
  email_to = config.get('HOCKEY_EMAIL', 'EMAIL_TO')
  sunset_dec = email.mEvent.mSunset.hour + email.mEvent.mSunset.minute / 60.0
  if time + 1.0 > sunset_dec:
    logger.info('not sending the email because it\'s going to be dark before ' + str(time) + ':%02d' % ((time % 1.0) * 60) + '. sunset: ' + str(email.mEvent.mSunset)) 
    email_to = config.get('HOCKEY_EMAIL', 'EMAIL_FROM')
    subject = 'No Time for hockey tomorrow ' + subject 
  else:
    logger.info('Sending email with subject:' + email.GetSubject() + '\nmessage:\n' + email.GetBody())

  if options.dry_run:
    print 'subject:', subject
    print 'body:', email.GetBody()
  else:
    email_utils.sendemail(from_addr    = config.get('HOCKEY_EMAIL', 'EMAIL_FROM'), 
                          to_addr_list = [email_to],
                          cc_addr_list = [''],
                          subject      = subject, 
                          message      = email.GetBody(), 
                          login        = config.get('HOCKEY_EMAIL', 'EMAIL_LOGIN'),
                          password     = config.get('HOCKEY_EMAIL', 'EMAIL_PASSWORD'))
