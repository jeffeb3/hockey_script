
import random, datetime

import event_utils

def IsDST(date):
  if date.month < 3 or date.month > 11:
    return False 
  if date.month > 3 and date.month < 11:
    return True

  previous_sun = date.day - date.isoweekday()
  if date.month == 3 and previous_sun >= 8:
    return True
  if date.month == 11 and previous_sun <= 0:
    return True

class HockeyEmail():
  def __init__(self, day, location):
    self.mDay = day
    self.mLocation = location
    self.mEvent = event_utils.HockeyEvent(day, location)
    self.mSnideRemark = self.GetSnideRemark()
    self.mSubject = 'Who\'s In? ' + self.mLocation.mName + ', ' + self.mDay.strftime('%A %B %e')

  def GetSnideRemark(self):
    remarks = [
      'If you don\'t come to hockey tomorrow, you\'ll regret it',
      'Hockey is the best exercise',
      'Forget the weather, just come and play hockey',
      'Don\'t you want to be cool like the other kids? They all play hockey',
      'Please reply immediately, or no one will know you want to come, and they will say no. Then no one will come. Then people will stop caring. Then hockey will end.',
      'If you don\'t come to hockey, then no one will. You are the only person that matters at all.',
      'Obesity in America hit an all time record today.',
      'Only you can prevent soccer kids from playing on hockey rinks.',
      'Participation is mandatory. Ed said so, and he\'s your boss.',
    ]
     
    is_dst = IsDST(self.mDay)

    # how many weeks are left before the first post dst game?
    games_before_dst = 0
    test_date = self.mDay
    if is_dst:
      for i in range(52):
        games_before_dst += 1
        test_date += datetime.timedelta(7)
        if not IsDST(test_date):
          break;

    if is_dst:
      remarks.append('The summer is almost over. There are only ' + str(games_before_dst) + ' remaining before the end of DST')

    if is_dst and games_before_dst == 1:
      return 'OMG! This is the last game before Daylight Savings Time! You have to come'
   
    if is_dst and not IsDST(self.mDay + datetime.timedelta(-7)):
      return 'DST has made the season possible'
 
    random.seed()
    return random.choice(remarks)

  def GetSubject(self):
    return self.mSubject

  def GetBody(self):
    line = self.mSnideRemark + '\n'
    line += self.mEvent.GetWeather()
    line += '\n\n'
    line += 'Sun Stuff:\n'
    line += self.mEvent.GetSun()
    line += '\n'
    line += 'Enjoy!\n--Hockey Robot created by Sean Gooding and Jeff Eberl'
    return line
