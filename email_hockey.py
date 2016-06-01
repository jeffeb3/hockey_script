#!/opt/bin/python

import sys
import datetime
import optparse
import random
import smtplib
import urllib2 
import json
from email.mime.text import MIMEText
import settings

''' This script invites people to come play hockey. '''

# Globals, yuk
debug = False
sunset = 24.0

def fetch_forecast(request_type):
    ''' fetches a particular forcast from wunderground.  Returns a dict (from the json).'''
    if debug:
        try:
            with open(request_type.replace('/','_') + '.json', 'r') as fp:
                return json.load(fp)
        except IOError:
            print "Debug mode enabled, but file missing, let's cache it"
            pass

    url = 'http://api.wunderground.com/api/' + settings.api_key + '/' + request_type +'/q/' + settings.location + '.json'

    j = json.load(urllib2.urlopen(url))

    if debug:
        with open(request_type.replace('/','_') + '.json', 'w') as fp:
            json.dump(j, fp, sort_keys=True, indent=4)
    return j

def is_dst(date):
    if date.month < 3 or date.month > 11:
        return False
    if date.month > 3 and date.month < 11:
        return True

    previous_sun = date.day - date.isoweekday()
    if date.month == 3 and previous_sun >= 8:
        return True
    if date.month == 11 and previous_sun <= 0:
        return True
 

def get_snide_remark(date):
    remarks = [
      'If you don\'t come to hockey tomorrow, you\'ll regret it',
      'Hockey is the best exercise',
      'Forget the weather, just come and play hockey',
      'Don\'t you want to be cool like the other kids? They all play hockey',
      'Please reply immediately, or no one will know you want to come, and they will say no. Then no one will come. Then people will stop caring. Then hockey will end.',
      'If you don\'t come to hockey, then no one will. You are the only person that matters at all.',
      'Obesity in America hit an all time record today.',
      'Only you can prevent soccer kids from playing on hockey rinks.',
      'Only you can prevent lacrosse kids from playing on hockey rinks.',
      'If no one plays hockey, they will turn the rink into a pickle ball court',
      'Participation is mandatory. [Insert Boss\'s name here] said so, and (s)he\'s your boss.',
    ]

    # how many weeks are left before the first post dst game?
    games_before_dst = 0
    test_date = date
    if is_dst(date):
        for i in range(52):
            games_before_dst += 1
            test_date += datetime.timedelta(7)
            if not is_dst(test_date):
                break;

    if is_dst(date):
        remarks.append('The summer is almost over. There are only ' + str(games_before_dst) + ' remaining before the end of DST')

    if is_dst(date) and games_before_dst == 1:
        return 'OMG! This is the last game before Daylight Savings Time! You have to come'

    if is_dst(date) and not is_dst(date + datetime.timedelta(-7)):
        return 'DST has made the season possible'

    random.seed()
    return random.choice(remarks)

def build_html_body(date, time):
    # Retrieve information from the Internet
    forecast = fetch_forecast('hourly10day/astronomy/forecast')

    html_body = """\
    <html>
      <head></head>
      <body>
    """

    # Insert Snide Remark
    html_body += "<h2>" + get_snide_remark(date) + "</h2>\n"

    # let's now build the HTML body contents
    html_body += '<h3>Weather for ' + date.strftime("%A %B %e") + ' at ' + settings.location_name + " (" + settings.location + ")" + '</h3>\n'

    found = False
    # Loop through the simple forcast, and come up with the text.
    for period in forecast['forecast']['txt_forecast']['forecastday']:
        date_name = date.strftime("%A")
        if period['title'] == date_name:
            found = True
            html_body += '<p><b>' + period['title'] + '</b>: ' + period['fcttext'] + '</p>\n'
    
    if not found:
        html_body += '<p>No forecast for that day.</p>\n'
    
    # Look through the hourly stuff
    html_body += '<h3>Hourly</h3>\n'
    html_body += '<p>\n'
    for period in forecast['hourly_forecast']:
        if int(period['FCTTIME']['mday']) == date.day:
            hour = int(period['FCTTIME']['hour'])
            if hour >= int(time) and hour - int(time) <= 3:
                hourline = '    ' + period['FCTTIME']['civil'] + " : " + period['condition']
                hourline += " Temp: " + period['temp']['english'] + "F "
                hourline += " Wind: " + period['wspd']['english'] + "mph "
                hourline += " Clouds: " + period['sky'] + "% "
                hourline += " Chance of Precip: " + period['pop'] + "% "
                if float(period['qpf']['english']) > 0.0:
                    hourline += " Rain: " + period['qpf']['english'] + "in "
                if float(period['snow']['english']) > 0.0:
                    hourline += " Snow: " + period['snow']['english'] + "in "
                hourline += "<br>\n"
                html_body += hourline
    html_body += '</p>\n'
    
    # Set the sunset stuff
    global sunset
    sunset = float(forecast['sun_phase']['sunset']['hour']) + float(forecast['sun_phase']['sunset']['minute'])/60.0
    sunset_obj = datetime.time(int(sunset), int((sunset % 1.0) * 60.0))
    html_body += "<h3>Sunset is at " + sunset_obj.strftime('%l:%m %p') + "</h3>\n"

    html_body +=  """
      <p>Enjoy!</p><p>--Hockey Robot created by Sean Gooding and Jeff Eberl</p>
      </body>
    </html>
    """
    return html_body

def send_email(subject, mail_text): 
    # Set up the message subject, etc. Then send it.
    COMMASPACE = ', '
 
    msg = MIMEText(mail_text, 'html')
    msg['Subject'] = subject
    msg['From'] = settings.email_from
    msg['To'] = COMMASPACE.join(settings.email_to)
 
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(settings.email_login, settings.email_pw)
    server.sendmail(settings.email_from, settings.email_to, msg.as_string())
    server.quit()

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-w', '--day_of_week', default=None,
        help="The day of the week, indexed from 0 at Monday.")
    parser.add_option('-t', '--time', default=None,
        help="The time of the event. Decimal hours out of 24. 5:30 is 17.5")
    parser.add_option('-d', '--debug', default=False, action="store_true",
        help="Debug, which will fetch and store the forecast, and it will not email anyone (it will print instead).")
    
    options, _ = parser.parse_args()
    
    if not options.day_of_week:
        parser.error('Day of week not provided.')
        
    if not options.time:
        parser.error('Time not provided.')
        
    debug = options.debug
    
    event_date = datetime.date.today()
    
    dow = int(options.day_of_week)
    dow %= 7
    while event_date.weekday() != dow:
        event_date = event_date + datetime.timedelta(1)

    event_time = float(options.time)
    event_time %= 24.0
    
    mail_text = build_html_body(event_date, event_time)

    if event_time + 1.0 > sunset:
        print 'Not sending email today. Because the sun will set too early.'
        sys.exit(0)
    
    event_time_obj = datetime.time(int(event_time), int(event_time % 1.0 * 60.0))
    subject = "Who's in? " + settings.location_name + ", " + event_date.strftime("%A %B %e") + " at " + event_time_obj.strftime("%l:%M %p")

    if debug:
        print subject
        print mail_text
    else:
        send_email(subject, mail_text)
        print 'Sent email at ', datetime.datetime.now()
