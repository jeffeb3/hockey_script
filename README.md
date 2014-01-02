hockey_script
=============

Collect the script that will create hockey notifications for my outdoor hockey group.

schedule_hockey.py
------------------
Gets called by the cronjob. Determines if it's a good idea to send the email today.

hockey_email.py
---------------
Object that creates the subject and body of an email.

email_utils.py
--------------
Send an email using this helper function

event_utils.py
--------------
Uses pysky (which uses grib2 and json) and astral (which uses pytz) to determine the weather and sunset tomorrow.

templates/example_crontab
-------------------------
crontab to run the schedule_hockey.py everyday.

templates/example_dot_hockey_config
-----------------------------------
put in ~/.hockey/config and change email and other settings

templates/example_dot_hockey_log
--------------------------------
put in ~/.hockey/log.cfg to configure the logging. Should be set to send nothing to the command line, and everything to log files in ~/.hockey/hockey.log


