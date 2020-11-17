"""
First the argument parser is set up and configured.
After importing all other libraries the logger initilased.

The structure of the following code is,
that first the classes are defined and initilased.
This is followed by some general fuctions,
that get more specific towards the bottom.

The main() function then brings everything together and confgures the bot,
while the (if __name__ == '__main__':) deals with handling the arguments
from the argument parser and prepaing the enviroment.
"""

import logging
import sys
import os
from threading import Thread
from functools import wraps
import traceback
import datetime
import weakref
import shelve
import signal
from emoji import emojize
import telegram
from telegram import (ReplyKeyboardMarkup,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup,
                      ParseMode,
                      ChatAction)
from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          ConversationHandler,
                          PicklePersistence,
                          CallbackQueryHandler)
from telegram.utils.helpers import mention_html


from argument_parser import args as command_line_args
from jokes import random_gif, maybe_news, update_reddit_db
from coffee_machine import CoffeeMachine
from password import Password, PASSWORD


# Config logging
LOGLEVEL = command_line_args.level
if command_line_args.quiet is True:
    LOGLEVEL = logging.CRITICAL
logging.basicConfig(format='%(asctime)s - \
                    %(name)s - %(levelname)s - %(message)s',
                    level=LOGLEVEL)
logger = logging.getLogger(__name__)

admins = [os.getenv('admin')]
devs = [os.getenv('dev')]


"""
Classes
"""


class StorableSet(set):
    """Class reoresenting a set that will be stored between sessions"""
    instances = []

    def __init__(self, key, db_name="User", s=None):
        if s is None:
            s = ()
        self.__class__.instances.append(weakref.proxy(self))
        logger.debug("Initiating class '%s' with key '%s' & DB '%s'",
                     self.__class__.__name__, key, db_name)
        super(StorableSet, self).__init__(s)
        self.key = key
        self.db_name = db_name
        self._set = set(s)

    def __repr__(self):
        return f"{self.__class__.__name__} with Key = '{self.key}' & \
            DB = '{self.db_name}'\n'{set(self)}'"

    def load(self):
        """Loading the storred data from the self"""
        local_shelve = shelve.open(self.db_name)
        logger.debug("Going to load '%s' from '%s'",
                     self.key, self.db_name)
        try:
            super(StorableSet, self).__init__(set(local_shelve[self.key]))
            logger.debug("Sucsessfully loaded '%s' from '%s'",
                         self.key, self.db_name)
        except Exception as error_message:
            logger.error("Failed getting '%s' from '%s'",
                         self.key, self.db_name)
            logger.info(error_message)
        finally:
            local_shelve.close()

    def store(self):
        """Store data in the set for later retrival"""
        local_shelve = shelve.open(self.db_name)
        logger.debug("Atempting to store '%s' in '%s'",
                     self.key, self.db_name)
        try:
            local_shelve[self.key] = set(self)
            logger.debug("Sucsessfully stored '%s' in '%s'",
                         self.key, self.db_name)
        except Exception as error_message:
            logger.error("Failed saving '%s' in '%s'",
                         self.key, self.db_name)
            logger.error(error_message)
        finally:
            local_shelve.close()


class StorableList(list):
    """Class representing a list that will be stored between sessions"""
    instances = []

    def __init__(self, key, db_name="User", s=None):
        if s is None:
            s = []
        self.__class__.instances.append(weakref.proxy(self))
        logger.debug("Initiating class '%s' with key '%s' & DB '%s'",
                     self.__class__.__name__, key, db_name)
        super(StorableList, self).__init__(s)
        self.key = key
        self.db_name = db_name
        self._set = list(s)

    def __repr__(self):
        return f"{self.__class__.__name__} with Key = '{self.key}' & \
            DB = '{self.db_name}'\n'{list(self)}'"

    def load(self):
        """Load values form shelve"""
        local_shelve = shelve.open(self.db_name)
        logger.debug("Going to load '%s' from '%s'",
                     self.key, self.db_name)
        try:
            super(StorableList, self).__init__(list(local_shelve[self.key]))
            logger.debug("Sucsessfully loaded '%s' from '%s'",
                         self.key, self.db_name)
        except Exception as error_message:
            logger.error("Failed getting '%s' from '%s'",
                         self.key, self.db_name)
            logger.info(error_message)
        finally:
            local_shelve.close()

    def store(self):
        """Store values in shelve"""
        local_shelve = shelve.open(self.db_name)
        logger.debug("Atempting to store '%s' in '%s'",
                     self.key, self.db_name)
        try:
            local_shelve[self.key] = list(self)
            logger.debug("Sucsessfully stored '%s' in '%s'",
                         self.key, self.db_name)
        except Exception as error_message:
            logger.error("Failed saving '%s' in '%s'",
                         self.key, self.db_name)
            logger.info(error_message)
        finally:
            local_shelve.close()


# class isinstance
cm = CoffeeMachine("The CoffeeNator")
my_chat_ids = StorableSet(key="my_chat_ids")
PASSWORD = Password()


# General Fuctions
def restricted_member(func):
    """Resrict the wrapped functions to only be able to be called by admins"""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in my_chat_ids:
            update.message.reply_text('You don\'t have purmission to do this.\n\
                Please signe in first')
            logger.debug('Unauthorized access attempt by %s with ID: %s',
                         update.effective_user.first_name, user_id)
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def restricted_admin(func):
    """Restrict the wrapped methods to only be able to be called by admins"""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in admins:
            update.message.reply_text('You don\'t have purmission to do this.\n\
                Please signe in first')
            logger.debug('Unauthorized access attempt by %s with ID: %s',
                         update.effective_user.first_name, user_id)
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id,
                                     action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def strfdelta(tdelta, fmt):
    """Make a string from delta"""
    delta = {"days": tdelta.days}
    delta["hours"], rem = divmod(tdelta.seconds, 3600)
    delta["minutes"], delta["seconds"] = divmod(rem, 60)
    return fmt.format(**delta)


def shutdown(signum, frame):
    """Shut down the server"""
    del frame  # Unused
    logger.debug("Statring shoutdow routine")
    if command_line_args.mode is True:
        logger.debug("Running in test mode. Nothing will be saved")
    if (signum == signal.SIGINT or
        signum == signal.SIGTERM or
        signum == signal.SIGABRT) and \
            command_line_args.mode is not True:
        for i in StorableSet.instances:
            i.store()
        for i in StorableList.instances:
            i.store()


def send(msg, chat_id=my_chat_ids, token=os.getenv('tokenTelegram')):
    """Send a message"""
    del token  # Unused
    if len(my_chat_ids) > 0:
        logger.debug('Sending messgae: %s', msg)
        for chat_id in my_chat_ids:
            bot.sendMessage(chat_id=chat_id, text=msg)
    else:
        logger.debug('There is no one to send a message to')


# Non member Functions
def help_message(update, context):
    """Show help messgae to user"""
    del context  # unused
    text = "This bot will inform you about the current state of coffee\n\
        /help\t\t diplay this help message\n\
        /start\t\t subscribe to the update list"

    user_id = update.effective_user.id
    if user_id in my_chat_ids:
        text += "\n\
            /time\t\t get an update on the current state\
            /news\t\t play a game"
    if user_id in admins:
        text += "\n\
            /pw\t\t request the current password\
            /new\t\t set a new global password"
    if user_id in devs:
        text += "\n /restart\t\t will restart the bot"
    update.message.reply_text(text)


def start(update, context):
    """Start bot conversation"""
    del context  # unused
    reply_keyboard = [['subscribe', 'unsubscribe', '/cancel']]

    update.message.reply_text(
        'Hi! My name is CoffeeBot.\n'
        'I will provide you with updates of fresh coffee.\n'
        'Send /cancel to stop talking to me.\n\n'
        'Do you wnat to subscribe or unsubscribe?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True))
    return CHOOSING


def button(update, context):
    """Check the button"""
    query = update.callback_query

    # News Game
    if (query.data == 'NewsTrue') | (query.data == 'NewsFalse'):
        user_id = query['message']['chat']['id']
        j = ""
        try:
            j = context.user_data["currentQuestion"]
        except KeyError:
            update.message.reply_text('There has been an Error.\n\
                                      Your anser was not recived')
            return
        answer = j['truth']
        question = j['headline']
        if 'News' + answer == query.data:
            query.edit_message_text('*Is this a real news aretical?*\n'
                                    + question,
                                    parse_mode="Markdown")
            bot.send_animation(user_id,
                               animation=random_gif('success'),
                               parse_mode='Markdown',
                               caption='*You are correct*')
        else:
            query.edit_message_text('*Is this a real news aretical?*\n'
                                    + question,
                                    parse_mode="Markdown")
            bot.send_animation(user_id,
                               animation=random_gif('facepam'),
                               parse_mode='Markdown',
                               caption='*You are wrong*')

        url = 'https://www.reddit.com'+j['url']
        bot.send_message(user_id,
                         parse_mode='HTML',
                         text='<a href="'+url+'">link</a>')


# Other options
def error(update, context):
    """Log Errors caused by Updates."""
    # we want to notify the user of this problem.
    # This will always work, but not notify users if the update is an
    # callback or inline query, or a poll update.
    # In case you want this, keep in mind that sending the message
    # could fail
    if update.effective_message:
        text = "Hey. I'm sorry to inform you that an error happened while \
            I tried to handle your update. " \
               "My developer(s) will be notified."
        update.effective_message.reply_text(text)

    # This traceback is created with accessing the traceback object
    # from the sys.exc_info, which is returned as the
    # third value of the returned tuple. Then we use the traceback.format_tb
    # to get the traceback as a string, which
    # for a weird reason separates the line breaks in a list,
    # but keeps the linebreaks itself. So just joining an
    # empty string works fine.
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))

    # lets try to get as much information from the telegram update as possible
    payload = ""

    # normally, we always have an user.
    # If not, its either a channel or a poll update.
    if update.effective_user:
        mention = mention_html(update.effective_user.id,
                               update.effective_user.first_name)
        payload += f' with the user {mention}'

    # there are more situations when you don't get a chat
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'

    # but only one where you have an empty payload by now: A poll (buuuh)
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    # lets put this in a "well" formatted text
    text = f"Hey.\n The error <code>{context.error}</code> \
        happened{payload}. The full traceback:\n\n\
        <code>{trace}</code>"
    # and send it to the dev(s)
    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it.
    # If you don't use the logger module, use it.
    raise Exception(text)


# Conversation functions
def sub(update, context):
    """Initiate substribtion proccess"""
    del context  # unused
    user = update.message.from_user
    logger.info("%s is trying to subscribe", user.first_name)
    update.message.reply_text('Please enter the password \
                              that is beeing displayed',
                              reply_markup=telegram.ReplyKeyboardRemove())
    logger.debug('The current password is %s', str(PASSWORD))
    return CHECK


def check(update, context):
    """Check password"""
    del context  # unused
    reply_keyboard = [['subscribe', 'unsubscribe', '/cancel']]
    user = update.message.from_user
    if update.message.text == str(PASSWORD):
        logger.info("%s has entered the correct password", user.first_name)
        try:
            # DB.Add("Subscribers",update.message.chat["id"])
            my_chat_ids.add(update.message.chat["id"])
            logger.debug("%s has been added to the DB", user.first_name)
            update.message.reply_text('You have sucsessfully signed up')
            return ConversationHandler.END
        except Exception as error_message:
            logger.warning("%s could not to added to DB", user.first_name)
            logger.info(error_message)
            return ConversationHandler.END
    else:
        logger.info("%s Entered the wrong password", user.first_name)
        update.message.reply_text('You have endered the wrong password\n'
                                  'what do you want to do?',
                                  reply_markup=ReplyKeyboardMarkup(
                                      reply_keyboard,
                                      one_time_keyboard=True)
                                  )
        return CHOOSING


def cancel(update, context):
    """Cancel conversation"""
    del context  # unused
    user = update.message.from_user
    logger.debug("User %s canceled the conversation.", user.first_name)
    smiley = emojize(":smiley:", use_aliases=True)
    update.message.reply_text(f'Okey, let\'s talk another time {smiley}',
                              reply_markup=telegram.ReplyKeyboardRemove())
    return ConversationHandler.END


def remove(update, context):
    """Remove user from subscribtion list"""
    del context  # unused
    user = update.message.from_user
    try:
        # DB.Remove("Subscribers", update.message.chat["id"])
        my_chat_ids.remove(update.message.chat["id"])
        update.message.reply_text(
            'You have sucsessfully been removed from the mailing list')
        logger.info("%s has been removed from the BD", user.first_name)
        return ConversationHandler.END
    except Exception as error_message:
        logger.warning("%s is not in the BD", user.first_name)
        logger.info(error_message)
        return ConversationHandler.END


# Functions for members
@restricted_admin
def err(update, context):
    """Manualy raise error"""
    raise Exception('ErrorCommand')


@restricted_member
def get_pw(update, context):
    """Get the password"""
    del context  # unused
    user = update.message.from_user
    logger.debug("%s has requested the Password", user.first_name)
    update.message.reply_text('The password is: ' + str(PASSWORD))


@restricted_member
def new_pw(update, context):
    """Request a new password"""
    del context  # unused
    user = update.message.from_user
    logger.debug("%s is requesting to change password", user.first_name)

    PASSWORD.change()
    update.message.reply_text('The password is now: ' + str(PASSWORD))
    logger.debug("%s is requesting to change password", user.first_name)
    logger.info("This is the password: %s", str(PASSWORD))


@restricted_member
@send_typing_action
def news_or_not(update, context):
    """Initiate is this real news game"""
    user = update.message.from_user
    logger.debug("%s wats to play a news game", user.first_name)

    joke = maybe_news()
    question = joke['headline']

    keyboard = [[InlineKeyboardButton("True", callback_data="NewsTrue"),
                InlineKeyboardButton("Fake", callback_data="NewsFalse")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data["currentQuestion"] = joke

    update.message.reply_text('*Is this a real news aretical?*\n'+question,
                              reply_markup=reply_markup,
                              parse_mode="Markdown")


@restricted_member
def time_since_coffee(update, context):
    """Get the time passed since the last coffee was made"""
    del context  # unused
    user = update.message.from_user
    logger.debug("%s wants to know the time \
                 since the last coffee has been brewed",
                 user.first_name)

    text = ""
    if cm.last_coffee is None:
        text = 'No coffee has been made yet'
        update.message.reply_text(text)  # , parse_mode = "Markdown"
        return

    now = datetime.datetime.now()
    time_past = now - cm.last_coffee
    text = strfdelta(time_past,
                     'It has been *{hours}* hours, \
                     *{minutes}* minutes \n'
                     'and *{seconds}* seconds\n'
                     'Since the last coffee has been made\n'
                     '_But who\'s counting_'
                     )  # {days} days {hours}:{minutes}:{seconds}'
    if cm.state is not None:
        text += f"\n\n*State*: {cm.str_state()}"

    update.message.reply_text(text, parse_mode="Markdown")


def update_coffee_state(context):
    """Check the state of the coffee machine"""
    del context  # unused

    def action(state):
        if state is not None:
            return {
                cm.State.BREWING: send("Coffee is being brewed"),
                cm.State.READY: send("Coffee is ready"),
                cm.State.OFF: send("Coffee machine has been shut off"),
                cm.State.ERROR: send("Coffee machine is malfunctioning"),
            }[state]
    logger.debug('The is state is %s', cm.check_state())
    action(cm.check_state())


def machine_off(context):
    """Check if the coffee machine has been turned off"""
    del context  # unused
    logger.debug("checking if the machine is off - State = %s", cm.state)
    if cm.state != cm.State.OFF:
        logger.debug("Machine is still on sending message")
        send("The coffee machine is still on")


def update_reddit(context):
    """Update the reddit dataase"""
    del context  # unused
    update_reddit_db()


# Conversation handlers
CHOOSING, CHECK = range(2)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING: [MessageHandler(Filters.regex('unsubscribe'), remove),
                   MessageHandler(Filters.regex('subscribe'), sub),
                   CommandHandler('cancel', cancel)],
        CHECK: [CommandHandler('cancel', cancel),
                MessageHandler(Filters.all, check)],
    },
    fallbacks=[CommandHandler('cancel', error)])


# Main Function
def main():
    """Main funcion"""
    # Displaying pin  configuration
    logger.debug("Using pin %i for brewing signal",
                 int(os.getenv('brewingPin')))
    logger.debug("Using pin %i for heating signal",
                 int(os.getenv('heatingPin')))

    # Displaying password and PID
    logger.debug("PID: %s", str(os.getpid()))
    logger.debug("This is the password: %s", str(PASSWORD))

    # Create the Updater and pass it your bot's token.
    pickle_persistence = PicklePersistence(filename=os.getenv('Telegram_db'))

    updater = Updater(token=os.getenv('tokenTelegram'),
                      persistence=pickle_persistence,
                      use_context=True,
                      user_sig_handler=shutdown)

    def restart(update, context):
        """Restart the telegram bot"""
        del context  # unused
        user = update.message.from_user
        logger.debug("%s hast triggered a restat of the bot",
                     user.first_name)
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    def stop_and_restart():
        """Gracefully stop the Updater \
            and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)
    job_queue = updater.job_queue

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # log all errors
    dispatcher.add_error_handler(error)

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('pw', get_pw))
    dispatcher.add_handler(CommandHandler('new', new_pw))
    dispatcher.add_handler(CommandHandler('help', help_message))
    dispatcher.add_handler(CommandHandler('news', news_or_not))
    dispatcher.add_handler(CommandHandler('time', time_since_coffee))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler('error', err))
    dispatcher.add_handler(CommandHandler('restart',
                                          restart,
                                          filters=Filters.user(
                                              username=os.getenv('sysadmin'))))

    # Seduled eventes
    job_queue.run_repeating(update_coffee_state, interval=2, first=0)
    job_queue.run_repeating(machine_off,
                            interval=datetime.timedelta(hours=24, minutes=0),
                            first=datetime.time(hour=17, minute=0))
    job_queue.run_repeating(update_reddit,
                            interval=datetime.timedelta(hours=1, minutes=0),
                            first=0)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':

    # Make sure we are running at least Python 3
    if sys.version_info[0] < 3:
        raise Exception("Must be using Python 3")

    # Set up execution enviroment
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logger.info('Startting program')
    logger.info('Token is %s', PASSWORD)

    # Handel Passed arguments
    if command_line_args.eraseDB is True:
        logger.debug('Attempting to remove files for a clean start')
        files = set()  # A set of all files to be removed
        files.add(os.getenv('Telegram_db'))
        for inst in StorableSet.instances:
            files.add(inst.DB)
        for inst in StorableList.instances:
            files.add(inst.DB)
        for file in files:
            try:
                os.remove(file)
                logger.debug("File '%s' removed", file)
            except Exception as error_message:
                logger.error("Failed to remove file '%s' from hard drive\n%s",
                             file, error_message)
        logger.info("All possible files removed. Starting fresh")
    if command_line_args.mode is True:
        logger.debug("Running in test mode olny the following User(s) \
            will be contacted: %s", devs)
        my_chat_ids = devs
    else:
        my_chat_ids.load()

    # Get bot
    bot = telegram.Bot(token=os.getenv('tokenTelegram'))

    main()
