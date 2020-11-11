import coffeeBot.Password as pw

passwords = []


def test_Password_Random():

    for _ in range(0, 10):
        global passwords
        password = pw.password()
        passwords.append(str(password))

    assert not all(elem == passwords[0] for elem in passwords)


def test_Password_Change():
    password = pw.password()
    password_1 = str(password)
    password.change()
    password_2 = str(password)
    assert password_1 != password_2


def tews_Password_Length():
    password = pw.password()
    assert len(password) == 4
