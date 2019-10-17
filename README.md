# Telegram CoffeeBot

This bot is designed to run on an raspberryPI and update its user about the state of the coffee machine at our lab.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

 * A coffee that is simple enough that to signals can be electrically monitored indicating the state of the coffee machine.
For this example its two LED lights that indicate heating (= The coffee machine is on) & brewing (= The coffee machine is brewing coffee).

  (With little work this functionality can easily be expanded.)

* Also a raspberry PI or similar is required
* Telegram API key [Link](telegram.com)
* Reddit API key [Link](reddit.com)

### Installing

In short, fork and clone the git to your local drive and run [coffee_bot.py](coffee_bot.py)

In  a bit more word:

```
git clone https://github.com/pfmephisto/telegram-coffee-bot.git

```
Make sure you are running python3 or newer and have the following external libraries installed.
And repeat

```
python -V
pip install ...
```
After that copy the [config_default.py](config_default.py) to config.py an fill out the required information.


```
cp config_default.py config.py
nano config.py

```
Edit the file and the save using control-o and control-x
```
^O
^X
```
Run the bot using:
```
python3 coffee_bot.py
```
More info can be found under:
```
python3 coffee_bot.py --help
```

## Built With

* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - The bot framework used

## Authors

* **Povl Filip Sonne-Frederiksen** - *Initial work* - [pfMephisto](https://github.com/pfmephisto)

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details.
