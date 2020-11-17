from coffee_bot.password import Password

def test_Password_Random():
    """Test if 10 generated passwords are different"""
    passwords = []
    for _ in range(0, 10):
        password = Password()
        passwords.append(str(password))

    assert not all(elem == passwords[0] for elem in passwords)


def test_password_change():
    password = Password()
    password_1 = str(password)
    password.change()
    password_2 = str(password)
    assert password_1 != password_2


def test_password_length():
    password = Password()
    assert len(str(password)) == 4
