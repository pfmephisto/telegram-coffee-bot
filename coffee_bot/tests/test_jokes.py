# Load enviroment variables

from coffee_bot.jokes import (random_joke, categories, jokes_lib,
                              format_joke, subredit_hot)


def test_random():
    j_1 = random_joke()
    j_2 = random_joke()
    assert j_1 != j_2


def test_categories():
    assert categories() == list(jokes_lib.keys())

def test_random_joke():
    joke = random_joke()
    assert isinstance(joke, dict) or isinstance(joke, str) 

def test_format_joke():
    joke = random_joke()
    assert isinstance(format_joke(joke), dict) or isinstance(format_joke(joke), str)


def test_subreddit():
    sub = subredit_hot('funny', limit=10)
    posts = []

    for result in sub:
        posts.append(result)

    assert len(posts) == 10
