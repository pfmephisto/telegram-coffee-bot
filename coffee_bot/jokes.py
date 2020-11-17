"""
Discription to be added after reworking the file
"""

import os
import random
import logging
import praw
# import json

logger = logging.getLogger(__name__)

jokes_lib = {
            'OneLiner':
            [
                'Light travels faster than sound. \
                    That\'s why some people appear bright \
                    until you hear them speak',
                'I was wondering why the ball was getting bigger. \
                    Then it hit me',
                'I have a few jokes about unemployed people, \
                    but none of them work',
                'How do you make holy water? You boil the hell out of it',
                'I remaned my iPod The Titanic, so when I plug it in, \
                    it says \"The Titanic is syncing.\"'
            ],
            'SetUpJokes':
            [
                {'setUp': 'What do you call sad coffee?',
                    'answer': 'Despresso.'},
                {'setUp': 'What\'s the best Beatles song?',
                    'answer': 'Latte Be!'},
                {'setUp': 'How are coffee beans like kids?',
                    'answer': 'They\'re always getting grounded!'},
                {'setUp': 'Why do they call coffee mud?',
                    'answer': 'Because it was ground \
                        a couple of minutes ago.'},
                {'setUp': 'What\'s it called when you steal \
                    someone\'s coffee?',
                    'answer': 'Mugging!'},
                {'setUp': 'How does a tech guy drink coffee?',
                    'answer': 'He installs Java!'},
                {'setUp': 'How did the hipster burn his tongue?',
                    'answer': 'He drank his coffee before it was cool.'},
                {'setUp': 'Why are Italians so good at making coffee?',
                    'answer': 'Because they know how \
                        to espresso themselves.'},
                {'setUp': 'How are coffee beans like kids?',
                    'answer': 'They\'re always getting grounded!'},
                {'setUp': 'Where do birds go for coffee?',
                    'answer': 'To the NESTcafe'},
                {'setUp': 'The best ones are rich, hot, \
                    and can keep you up all night.',
                    'answer': 'How are men like coffee?'},
                {'setUp': 'How does Moses make his coffee?',
                    'answer': 'He brews.'},
                {'setUp': 'What\'s the technical name for \
                    a pot of coffee at work?',
                    'answer': 'Break fluid'},
                {'setUp': 'What do you call it when you walk into a cafe \
                    you\'re sure you\'ve been to before?',
                    'answer': 'Deja brew'},
                {'setUp': 'Why should you be wary of 5-cent espresso?',
                    'answer': 'It\'s a cheap shot.'},
                {'setUp': 'Why shouldn\'t you discuss \
                    coffee in polite company?',
                    'answer': 'It can make for a strong and heated debate.'},
                {'setUp': 'Why did the espresso keep checking his watch?',
                    'answer': 'Because he was pressed for time.'},
                {'setUp': 'What do you call sad coffee?',
                    'answer': 'Depresso'}
            ],
            'PickUp':
            [
                'The barista may have forgotten your name, but I sure won\'t.',
                'I can feel something brewing between the two of us.',
                'You\'re like the scent of coffee, \
                    you get me out of bed in the morning.',
                'I like my women like I like my coffee, HOT!',
                'My coffee hasn\'t kicked in yet, \
                    so I can\'t think of anything charming to say.',
                'My coffee is really hot, but you\'re hotter.',
                'You mocha me crazy!',
                'You are just the way I like my coffee. \
                    Tall, dark and strong.',
                'Coffee, tea, or just more of me?',
                'If you were ground coffee, you\'d be \
                    Espresso cause you\'re so fine.',
                'You\'re like my coffee, you keep me up all night.',
                'My coffee isn\'t hot enough! Could you hold it for a while?',
                'I have no idea how you can look so great pre-coffee.'
                'If you need to take it slow, I can cold-brew.'
            ],
            'EndOfDay':
            [
                'If the local coffee shop has awarded you \
                    "Employee of the Month" and you don\'t even work there, \
                    you may be drinking too much coffee.'
            ],
            'StartOfDay':
            [
                'Coffee is the most important meal of the day'
            ]
            }
gif_Lig = {
            'facepam':
            [
                'https://media.giphy.com/media/AjYsTtVxEEBPO/giphy.gif',
                'http://giphygifs.s3.amazonaws.com\
                    /media/6yRVg0HWzgS88/giphy.gif',
                'https://media.giphy.com/media/3og0INyCmHlNylks9O/giphy.gif',
                'https://media.giphy.com/media/yvBAuESRTsETqNFlEl/giphy.gif',
                'http://giphygifs.s3.amazonaws.com\
                    /media/KIqHhQ1TLTEbu/giphy.gif',
                'https://media.giphy.com/media/xT0GqtpF1NWd9VbstO/giphy.gif',
                'https://media.giphy.com/media/3oEhmQ3TGEYvriKaEo/giphy.gif',
                'https://media.giphy.com/media/ystGrJ3SmiTQY/giphy.gif',
                'https://media.giphy.com/media/M7JJpBH0NuE/giphy.gif'
            ],
            'success':
            [
                'https://media.giphy.com/media/d2Z9QYzA2aidiWn6/giphy.gif',
                'https://media.giphy.com/media/MSCzxrLEF25feISTIz/giphy.gif',
                'https://media.giphy.com/media/l4HodBpDmoMA5p9bG/giphy.gif',
                'https://media.giphy.com/media/jpXAdNRiwGL0k/giphy.gif',
                'http://giphygifs.s3.amazonaws.com\
                    /media/6AachtBbwRYm4/giphy.gif',
                'https://media.giphy.com/media/xNBcChLQt7s9a/giphy.gif',
                'https://media.giphy.com/media/a0h7sAqON67nO/giphy.gif',
                'https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/giphy.gif',
                'https://media.giphy.com/media/g9582DNuQppxC/giphy.gif',
                'https://media.giphy.com/media/qjfeT5XdAirCg/giphy.gif'
            ]
}


class RedditDatabase():
    """Class to store the reddit database in"""
    values = []


REDDIT_DB = RedditDatabase()


def categories():
    """"Get all the category names"""
    return list(jokes_lib.keys())


def random_joke(joke_type="All"):
    """Return a random joke"""
    # If no type has been supplied
    if joke_type == "All":
        joke_type = random.choice(categories())

    for types in jokes_lib:
        if types == joke_type:
            return random.choice(jokes_lib[joke_type])

    # Else raise exception
    raise Exception("Type not present in Database")


def format_joke(joke):
    """Format the joke"""
    if isinstance(joke, str):
        print(joke)
        return joke
    if isinstance(joke, dict):
        text = joke['setUp']+"\n"+joke['answer']
        print(joke['setUp'])
        print(joke['answer'])
        return text


reddit_id = os.getenv('Reddit_id')
reddit_secret = os.getenv('Reddit_secret')
reddit_user_name = os.getenv('Reddit_user')
reddit_password = os.getenv('Reddit_password')
reddit_user_agent = os.getenv('Reddit_user_agent')

reddit = praw.Reddit(
    client_id=reddit_id,
    client_secret=reddit_secret,
    #  password=reddit_password,
    user_agent=reddit_user_agent,
    #  username=reddit_user_name
    )


def subredit_hot(subredit, limit=10):
    """Retrive results from subreddit"""
    subreddit = reddit.subreddit(subredit).hot(limit=limit)
    return subreddit


def maybe_news():
    """Is the news games"""
    if len(REDDIT_DB.values) == 0:
        logger.debug("Local cache seems to be missing Updating from source")
        posts = []
        choice = random.choice(['TheOnion', 'nottheonion'])
        for result in subredit_hot(choice, limit=20):
            if not result.stickied:
                posts.append(result)
        post = random.choice(posts)

        truth = ""
        if choice == 'TheOnion':
            truth = "False"
        if choice == 'nottheonion':
            truth = "True"
        dict_result = {'headline': post.title,
                       'truth': truth,
                       'url': post.permalink}
        return dict_result

    logger.debug("Using local Cache")
    return random.choice(REDDIT_DB)


def update_reddit_db(list_names=None):
    """Update the reddit database"""
    if list_names is None:
        list_names = ['TheOnion', 'nottheonion']
    logger.debug("Updating the local reddit DB")

    posts = []
    dicts = []
    # Getting the posts
    for text in list_names:
        sub = subredit_hot(text, limit=20)
        for result in sub:
            if not result.stickied:
                posts.append(result)
    # Formatiing the dict
    for post in posts:
        truth = ""
        result_dict = {'headline': post.title,
                       'truth': truth, 'url': post.permalink}
        dicts.append(result_dict)

    REDDIT_DB.values = dicts


def categories_gif():
    """Get the catigories of the gifs"""
    all_types = []
    for types in gif_Lig:
        all_types.append(types)
    return all_types


def random_gif(joke_type=None):
    """Retrive a random gif"""
    if joke_type is None:
        joke_type = "All"
    # If no type has been supplied
    if joke_type == "All":
        joke_type = random.choice(categories_gif())

    for types in gif_Lig:
        if types == joke_type:
            return random.choice(gif_Lig[joke_type])

    # Else raise exception
    raise Exception("Type not present in Database")


if __name__ == '__main__':
    pass
    # print(randomGIF('facepam'))
