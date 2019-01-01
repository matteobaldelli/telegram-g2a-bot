# Telegram G2A Bot

G2A Price the bot that helps you save money on your games. Track you favorite games and buy it when the price goes down

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To run this project you must have installed these programs:

* [python](https://www.python.org/)
* [pipenv](https://github.com/pypa/pipenv)
* [postgresql](https://github.com/postgres/postgres)


### Installing

Create a .env file in project folder:

```
TELEGRAM_TOKEN="TOKEN-TELEGRAM-BOT"
HOST_URL="URL-FOR-WEBHOOK"
DATABASE_URL="postgresql://localhost/test"
```

after create a .env file go to the console

```
$ pipenv install
$ pipenv run python manage.py db upgrade
$ pipenv run python app.py
```

