import os
import requests
import telegram
from json import JSONDecodeError
from flask_sqlalchemy import SQLAlchemy
from telegram.error import Unauthorized

from app import create_app
from models import Track


TOKEN = os.environ.get('TELEGRAM_TOKEN')
PRICE_TRIGGER = 0.9     # 90% of the initial price
G2A_URL = 'https://www.g2a.com/marketplace/product/auctions/?id='
COOKIES = dict(store='italian', currency='EUR')

db = SQLAlchemy()
bot = telegram.Bot(TOKEN)
app = create_app()
app.app_context().push()


tracks = Track.get_all()
for track in tracks:
    try:
        response = requests.get(url=G2A_URL + track.game_id, cookies=COOKIES)
        data = response.json()
        new_price = float(data['lowest_price'])
        if track.game_price is None:
            track.game_price = new_price
        if track.game_price != new_price:
            price_l_notification = track.game_median_price * PRICE_TRIGGER
            price_h_notification = track.game_median_price / PRICE_TRIGGER
            if new_price <= price_l_notification or new_price >= price_h_notification:
                new_message = 'Il prezzo di <a href="' + track.game_link + '">' + track.name + '</a> è '
                if track.game_price > new_price:
                    new_message += 'sceso '
                else:
                    new_message += 'salito '
                new_message += 'a ' + str(new_price)
                track.game_median_price = new_price
                bot.send_message(track.user.chat_id, new_message, parse_mode='HTML')
            track.game_price = new_price
        track.save()
    except JSONDecodeError:
        pass
    except ConnectionError:
        pass
    except Unauthorized:
        user = track.user
        user.delete()
