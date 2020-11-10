#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the GNU GPLv3 license.

"""
First the argument parser is set up and configured.
After importing all other libraries the logger initilased.

The structure of the following code is, that first the classes are defined and initilased.
This is followed by some general fuctions, that get more specific towards the bottom.

The main() function then brings everything together and confgures the bot,
while the (if __name__ == '__main__':) deals with handling the arguments from the argument parser and prepaing the enviroment.
"""

from argparse import ArgumentParser
import logging
import sys
import os
from ArgumentParser import args


#Load enviroment variables
from dotenv import load_dotenv
if (load_dotenv()):
    pass # If no variables have been imported

if (os.getenv('CI') != 'true'):
    pass

#### Libraries
import telegram
from telegram import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatAction)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence, CallbackQueryHandler)
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html

from threading import Thread
from functools import wraps
import traceback
import random
import datetime

import Jokes.jokes as jokes
import CoffeeMachine.coffeeMachine as coffeeM
from emoji import emojize

# Config logging
loglevel = args.level
if (args.quiet == True):
    loglevel = logging.CRITICAL
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=loglevel)
logger = logging.getLogger(__name__)

admins = [os.getenv('admin')]
devs = [os.getenv('dev')]

"""
Classes
"""
class storableSet(set):
    instances = []
    def __init__ (self, key, DB="User", s=()):
        import weakref
        self.__class__.instances.append(weakref.proxy(self))
        logger.debug(f"Initiating class '{self.__class__.__name__} with key '{key} & DB '{DB}'")
        super(storableSet, self).__init__(s)
        self.key = key
        self.DB = DB
        self._set = set(s)
    def __repr__(self):
        return f"{self.__class__.__name__} with Key = '{self.key}' & DB = '{self.DB}'\n'{set(self)}'"
    def load(self):
        import shelve
        shelve = shelve.open(self.DB)
        logger.debug(F"Going to load '{self.key}' from '{self.DB}'")
        try:
            super(storableSet, self).__init__(set(shelve[self.key]))
            logger.debug(F"Sucsessfully loaded '{self.key}' from '{self.DB}'")
        except:
            logger.error(F"Failed getting '{self.key}' from '{self.DB}'")
        finally:
            shelve.close()
    def store(self):
        import shelve
        shelve = shelve.open(self.DB)
        logger.debug(F"Atempting to store '{self.key}' in '{self.DB}'")
        try:
            shelve[self.key] = set(self)
            logger.debug(F"Sucsessfully stored '{self.key}' in '{self.DB}'")
        except:
            logger.error(F"Failed saving '{self.key}' in '{self.DB}'")
        finally:
            shelve.close()
class storableList(list):
    instances = []
    def __init__ (self, key, DB="User", s=[]):
        import weakref
        self.__class__.instances.append(weakref.proxy(self))
        logger.debug(f"Initiating class '{self.__class__.__name__} with key '{key} & DB '{DB}'")
        super(storableList, self).__init__(s)
        self.key = key
        self.DB = DB
        self._set = list(s)
    def __repr__(self):
        return f"{self.__class__.__name__} with Key = '{self.key}' & DB = '{self.DB}'\n'{list(self)}'"
    def load(self):
        import shelve
        shelve = shelve.open(self.DB)
        logger.debug(F"Going to load '{self.key}' from '{self.DB}'")
        try:
            super(storableList, self).__init__(list(shelve[self.key]))
            logger.debug(F"Sucsessfully loaded '{self.key}' from '{self.DB}'")
        except:
            logger.error(F"Failed getting '{self.key}' from '{self.DB}'")
        finally:
            shelve.close()
    def store(self):
        import shelve
        shelve = shelve.open(self.DB)
        logger.debug(F"Atempting to store '{self.key}' in '{self.DB}'")
        try:
            shelve[self.key] = list(self)
            logger.debug(F"Sucsessfully stored '{self.key}' in '{self.DB}'")
        except:
            logger.error(F"Failed saving '{self.key}' in '{self.DB}'")
        finally:
            shelve.close()
class password():
    def __init__(self):
        import random
        val = random.randrange(1000, 9999)
        self._val = int(val)
    def change(self):
        import random
        val = random.randrange(1000, 9999)
        self._val = int(val)
    def __str__(self):
        return str(self._val)

"""
Variable declaration
"""
# class isinstance
cm = coffeeM.coffeeMachine("The CoffeeNator")
my_chat_ids = storableSet(key="my_chat_ids")
password = password()


"""
Functions
"""
#General Fuctions
def restrictedMember(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in my_chat_ids:
            update.message.reply_text('You don\'t have purmission to do this.\nPlease signe in first')
            logger.debug(f'Unauthorized access attempt by {update.effective_user.first_name} with ID: {user_id}')
            return
        return func(update, context, *args, **kwargs)
    return wrapped
def restrictedAdmin(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in admins:
            update.message.reply_text('You don\'t have purmission to do this.\nPlease signe in first')
            logger.debug(f'Unauthorized access attempt by {update.effective_user.first_name} with ID: {user_id}')
            return
        return func(update, context, *args, **kwargs)
    return wrapped
def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func
def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)
def shutdown(signum, frame):
    import signal
    logger.debug("Statring shoutdow routine")
    if(args.mode == True):
        logger.debug("Running in test mode. Nothing will be saved")
    if (signum == signal.SIGINT) & (args.mode != True):
        for i in storableSet.instances:
            i.store()
        for i in storableList.instances:
            i.store()
    if (signum == signal.SIGTERM) & (args.mode != True):
        for i in storableSet.instances:
            i.store()
        for i in storableList.instances:
            i.store()
    if (signum == signal.SIGABRT) & (args.mode != True):
        for i in storableSet.instances:
            i.store()
        for i in storableList.instances:
            i.store()

#Sent a Message
def send(msg, chat_id=my_chat_ids, token=os.getenv('tokenTelegram')):
    if (len(my_chat_ids) > 0):
        logger.debug('Sending messgae: ' + msg)
        for chat_id in my_chat_ids:
            bot.sendMessage(chat_id=chat_id, text=msg)
    else:
        logger.debug('There is no one to send a message to')
#Non member Functions
def help(update, context):
    text =  """ This bot will inform you about the current state of coffee

/help\t\t diplay this help message
/start\t\t subscribe to the update list"""

    user_id = update.effective_user.id
    if user_id in my_chat_ids:
        text +="""\n
/time\t\t get an update on the current state
/news\t\t play a game"""
    if user_id in admins:
        text += """\n
/pw\t\t request the current password
/new\t\t set a new global password"""
    if user_id in devs:
        text += """\n
/restart\t\t will restart the bot"""
    update.message.reply_text(text)
def start(update, context):
    reply_keyboard = [['subscribe', 'unsubscribe', '/cancel']]

    update.message.reply_text(
        'Hi! My name is CoffeeBot.\n'
        'I will provide you with updates of fresh coffee.\n'
        'Send /cancel to stop talking to me.\n\n'
        'Do you wnat to subscribe or unsubscribe?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CHOOSING
def button(update, context):
    query = update.callback_query

    #News Game
    if ((query.data == 'NewsTrue') | (query.data == 'NewsFalse')):
        id = query['message']['chat']['id']
        j = ""
        try:
            j = context.user_data["currentQuestion"]
        except KeyError:
            update.message.reply_text('There has been an Error.\nYour anser was not recived')
            return
        a = j['truth']
        q = j['headline']
        if ('News'+a == query.data):
            query.edit_message_text('*Is this a real news aretical?*\n'+q, parse_mode = "Markdown")
            bot.send_animation(id, animation=jokes.randomGIF('success'), parse_mode='Markdown', caption='*You are correct*')
        else:
            query.edit_message_text('*Is this a real news aretical?*\n'+q, parse_mode = "Markdown")
            bot.send_animation(id, animation=jokes.randomGIF('facepam'), parse_mode='Markdown', caption='*You are wrong*')

        url = 'https://www.reddit.com'+j['url']
        bot.send_message(id, parse_mode='HTML', text='<a href="'+url+'">link</a>')
#Other options
def error(update, context):
    """Log Errors caused by Updates."""
    """
    logger.warning('Update "%s" caused error "%s"', update, error)
    return ConversationHandler.END
    """
    # add all the dev user_ids in this list. You can also add ids of channels or groups.
    devs = [117226628]
    # we want to notify the user of this problem. This will always work, but not notify users if the update is an
    # callback or inline query, or a poll update. In case you want this, keep in mind that sending the message
    # could fail
    if update.effective_message:
        text = "Hey. I'm sorry to inform you that an error happened while I tried to handle your update. " \
               "My developer(s) will be notified."
        update.effective_message.reply_text(text)
    # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ""
    # normally, we always have an user. If not, its either a channel or a poll update.
    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
    # there are more situations when you don't get a chat
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
           f"</code>"
    # and send it to the dev(s)
    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise Exception(text)

#Conversation functions
def sub(update, context):
    user = update.message.from_user
    logger.info("%s is trying to subscribe", user.first_name)
    update.message.reply_text('Please enter the password that is beeing displayed', reply_markup= telegram.ReplyKeyboardRemove())
    return CHECK
def check(update, context):
    reply_keyboard = [['subscribe', 'unsubscribe', '/cancel']]
    user = update.message.from_user
    if(update.message.text == str(password)):
        logger.info("%s has entered the correct password", user.first_name)
        try:
            #DB.Add("Subscribers",update.message.chat["id"])
            my_chat_ids.add(update.message.chat["id"])
            logger.debug("%s has been added to the DB", user.first_name)
            update.message.reply_text('You have sucsessfully signed up')
            return ConversationHandler.END
        except:
            logger.warning("%s could not to added to DB", user.first_name)
            return ConversationHandler.END
    else:
        logger.info("%s Entered the wrong password", user.first_name)
        update.message.reply_text('You have endered the wrong password\n'
                                'what do you want to do?',
                                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CHOOSING
def cancel(update, context):
    user = update.message.from_user
    logger.debug("User %s canceled the conversation.", user.first_name)
    smiley = emojize(":smiley:", use_aliases=True)
    update.message.reply_text(f'Okey, let\'s talk another time {smiley}', reply_markup = telegram.ReplyKeyboardRemove() )
    return ConversationHandler.END
def rm(update, context):
    user = update.message.from_user
    try:
            #DB.Remove("Subscribers", update.message.chat["id"])
            my_chat_ids.remove(update.message.chat["id"])
            update.message.reply_text('You have sucsessfully been removed from the mailing list')
            logger.info("%s has been removed from the BD", user.first_name)
            return ConversationHandler.END
    except:
        logger.warning("%s is not in the BD", user.first_name)
        return ConversationHandler.END

#Functions for members
@restrictedAdmin
def err(update, context):
    raise Exception('ErrorCommand')
@restrictedMember
def getPW(update, context):
    user = update.message.from_user
    logger.debug("%s has requested the Password", user.first_name)
    update.message.reply_text('The password is: '+ str(password))
@restrictedMember
def newPW(update, context):
    user = update.message.from_user
    logger.debug("%s is requesting to change password", user.first_name)

    password.change()
    update.message.reply_text('The password is now: '+ str(password))
    logger.debug("%s is requesting to change password", user.first_name)
    logger.info("This is the password: %s", password)
@restrictedMember
@send_typing_action
def newsOrnot(update, context):
    user = update.message.from_user
    logger.debug("%s wats to play a news game", user.first_name)

    j = jokes.maybeNews()
    q = j['headline']

    keyboard = [[InlineKeyboardButton("True", callback_data="NewsTrue"),
                InlineKeyboardButton("Fake", callback_data="NewsFalse")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data["currentQuestion"] = j

    update.message.reply_text('*Is this a real news aretical?*\n'+q, reply_markup = reply_markup, parse_mode = "Markdown")
@restrictedMember
def timeSinceCoffee(update, context):
    user = update.message.from_user
    logger.debug(f"{user.first_name} Wants to know the time since the last coffee has been brewed")

    text = ""
    if (cm.lastCoffee == None):
        text = 'No coffee has been made yet'
        update.message.reply_text(text) #, parse_mode = "Markdown"
        return

    now = datetime.datetime.now()
    timePast = now - cm.lastCoffee
    text = strfdelta(timePast,  'It has been *{hours}* hours, *{minutes}* minutes \n'
                                'and *{seconds}* seconds\n'
                                'Since the last coffee has been made\n'
                                '_But who\'s counting_'
                                )  #{days} days {hours}:{minutes}:{seconds}'
    if (cm.state is not None):
        text += f"\n\n*State*: {cm.strState()}"

    update.message.reply_text(text, parse_mode = "Markdown")

def updateCoffeeState(context):
    def action(state):
        return {
            cm.State.BREWING : send("Coffee is being brewed"),
            cm.State.READY : send("Coffee is ready"),
            cm.State.OFF : send("Coffee machine has been shut off"),
            cm.State.ERROR : send("Coffee machine is malfunctioning"),
        }[state]
    action(cm.checkState())
def machineOff(context):
    logger.debug(f"checking if the machine is off - State = {cm.state}")
    if not(cm.state == cm.State.OFF):
        logger.debug("Machine is still on sending message")
        send("The coffee machine is still on")
def updateReddit(context):
    jokes.updateRedditDB()

#Conversation handlers
CHOOSING, CHECK  = range(2)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING: [     MessageHandler(Filters.regex('unsubscribe'),rm),
                        MessageHandler(Filters.regex('subscribe'),sub),
                        CommandHandler('cancel', cancel)
                    ],
        CHECK: [    CommandHandler('cancel', cancel),
                    MessageHandler(Filters.all, check)
                    ],
    },
    fallbacks=[CommandHandler('cancel', error)])

#Main Function
def main():
    # Displaying pin  configuration
    logger.debug(f"Using pin {int(os.getenv('brewingPin'))} for brewing signal")
    logger.debug(f"Using pin {int(os.getenv('heatingPin'))} for heating signal")

    # Displaying password and PID
    logger.debug(f"PID: {str(os.getpid())}")
    logger.debug(f"This is the password: {password}")

    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename=os.getenv('Telegram_db'))

    updater = Updater(token=os.getenv('tokenTelegram'), persistence=pp, use_context=True, user_sig_handler=shutdown)
    def restart(update, context):
        user = update.message.from_user
        logger.debug(f"{user.first_name} hast triggered a restat of the bot")
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()
    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)
    jq = updater.job_queue

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # log all errors
    dp.add_error_handler(error)

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('pw', getPW))
    dp.add_handler(CommandHandler('new', newPW))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('news', newsOrnot))
    dp.add_handler(CommandHandler('time', timeSinceCoffee))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler('error', err))
    dp.add_handler(CommandHandler('restart', restart, filters=Filters.user(username=os.getenv('sysadmin'))))

    #Seduled eventes
    jq.run_repeating(updateCoffeeState, interval=2, first=0)
    jq.run_repeating(machineOff, interval = datetime.timedelta(hours=24, minutes=0), first= datetime.time(hour=17, minute=0))
    jq.run_repeating(updateReddit, interval= datetime.timedelta(hours=1, minutes=0), first=0)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

"""
Start of programm
"""
if __name__ == '__main__':
    #Make sure we are running at least Python 3
    if sys.version_info[0] < 3:
        raise Exception("Must be using Python 3")

    #Set up execution enviroment
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logger.info('Startting program')


    # Handel Passed arguments
    if (args.eraseDB == True):
        logger.debug('Attempting to remove files for a clean start')
        files = set() #A set of all files to be removed
        files.add(os.getenv('Telegram_db'))
        for inst in storableSet.instances:
            files.add(inst.DB)
        for inst in storableList.instances:
            files.add(inst.DB)
        for file in files:
            try:
                os.remove(file)
                logger.debug(f"File '{file}' removed")
            except Exception as e:
                logger.error(f"Failed to remove file '{file}' from hard drive\n{e}")
        logger.info("All possible files removed. Starting fresh")
    if (args.mode == True):
        logger.debug(f"Running in test mode olny the following User(s) will be contacted: {devs}")
        my_chat_ids = devs
    else:
        my_chat_ids.load()

    #Get bot
    bot = telegram.Bot(token=os.getenv('tokenTelegram'))

    main()
