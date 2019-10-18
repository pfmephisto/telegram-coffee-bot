
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the GNU GPLv3 license.
import os

devs = [] #The developers. Will be notified if error ocur on the bot
admins = [] # Users thet shoud have andinistive rights

if (os.getenv('CI') != 'true'):
    #Telegram
    os.environ['sysadmin'] = 'username' #User handle of main admin

    os.environ['tokenTelegram'] = 'username' #Telegram api token
    os.environ['Telegram_db'] = 'username' # Telegram DB for persistance

    os.environ['Reddit_secret'] = 'username' #Rddit secret
    os.environ['Reddit_id'] = 'username' #Reddit ID
    os.environ['Reddit_user'] = 'username' #Reddit user name
    os.environ['Reddit_password'] = 'username' #Reddit password
    os.environ['Reddit_user_agent'] = 'username' #Reddit bot useragent

    os.environ['brewingPin'] = '0' # Singal pin on rassberryPi
    os.environ['user_agent'] = '0' # Signal pin on rassberryPi
