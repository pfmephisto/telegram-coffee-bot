import coffee_bot

def pas():
    p = coffee_bot.password()
    return p

def test_password():
    assert pas() >= 1000
    assert pas() <= 9999
