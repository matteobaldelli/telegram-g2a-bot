import requests
import telegram
import os
from app import create_app
from flask import request
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

TOKEN = os.environ.get('TELEGRAM_TOKEN')
SENTRY_URL = os.environ.get('SENTRY_URL', '')

G2A_URL = 'https://www.g2a.com/marketplace/product/auctions/?id='
COOKIES = dict(store='italian', currency='EUR')

app = create_app()
bot = telegram.Bot(TOKEN)


@app.route('/' + TOKEN, methods=['POST'])
def web_hook():
    from models import User, Track

    update = telegram.update.Update.de_json(request.get_json(force=True), bot)

    command = update.message.text
    chat_id = update.message.chat_id
    chat_username = update.message.from_user.username

    standard_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='track'), KeyboardButton(text='list')],
        [KeyboardButton(text='delete'), KeyboardButton(text='info')]
    ], resize_keyboard=True)

    new_message = 'Non ho capito, usa info per avere informazioni.'
    # keyboard = ReplyKeyboardRemove()
    keyboard = None
    disable_web_page_preview = False

    user = User.query.filter_by(chat_id=chat_id).first()
    if not user:
        user = User(chat_id=chat_id, state='creation', chat_username=chat_username)
        user.save()

    if command == 'cancel':
        if user.state == 'delete':
            new_message = 'eliminazione annullata'
        elif user.state == 'track':
            new_message = 'track annullata'
        elif user.state == 'track_name':
            track = Track.query.filter_by(user=user, name='temp').first()
            track.delete()
            new_message = 'track annullata'
        keyboard = standard_keyboard
        user.state = 'cancel'
    elif user.state == 'track':
        if command[:20] == 'https://www.g2a.com/':
            if command.find('?') != -1:
                command = command[:command.find('?')]
            url = command
            game_id = url[-14:]
            response = requests.get(url=G2A_URL + game_id, cookies=COOKIES)
            data = response.json()
            if len(data):
                new_price = float(data['lowest_price'])
                track = Track(
                    name='temp',
                    game_id=game_id,
                    game_link=url + '?mkey=5aaxk',
                    game_price=new_price,
                    game_median_price=new_price,
                    user=user
                )
                track.save()
                user.state = 'track_name'
                new_message = 'Con che nome lo vuoi salvare?'
            else:
                new_message = 'Link non valido'
        else:
            new_message = 'Link non valido'
    elif user.state == 'track_name':
        track = Track.query.filter_by(name=command, user=user).first()
        if track:
            new_message = 'Nome non valido'
        else:
            track = Track.query.filter_by(name='temp', user=user).first()
            # TODO: if track is None?
            track.name = command
            user.state = 'track_finish'
            track.save()
            new_message = 'Track salvato'
            keyboard = standard_keyboard
    elif user.state == 'delete':
        track = Track.query.filter_by(user=user, name=command).first()
        if track:
            track.delete()
            user.state = 'delete_finish'
            new_message = 'Track Eliminato'
            keyboard = standard_keyboard
        else:
            new_message = 'Nome non valido'
    elif command == 'track':
        user.state = 'track'
        new_message = 'Inserisci il link di g2a'
        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='cancel')]], resize_keyboard=True)
    elif command == 'delete':
        tracks = Track.query.filter_by(user=user).all()
        if len(tracks):
            command_list = []
            for track in tracks:
                command_list.append([KeyboardButton(text=track.name)])
            command_list.append([KeyboardButton(text='cancel')])
            user.state = 'delete'
            new_message = 'Cosa vuoi eliminare?'
            keyboard = ReplyKeyboardMarkup(keyboard=command_list, resize_keyboard=True)
        else:
            new_message = 'Nessun gioco in lista'
            user.state = 'delete_empty'
    elif command == 'list':
        tracks = Track.query.filter_by(user=user).all()
        if len(tracks):
            new_message = 'Lista dei Track: \n\n'
            for track in tracks:
                new_message += 'Name: <a href="' + track.game_link + '">' + track.name + '</a>\n'
                new_message += 'Price: ' + str(track.game_price) + '\n'
                new_message += '\n'
            user.state = 'list'
            disable_web_page_preview = True
        else:
            new_message = 'Nessun gioco in lista'
            user.state = 'list_empty'
    elif command == 'info' or command == '/start':
        user.state = 'info'
        new_message = 'Benvenuto nel bot \n\n'
        new_message += 'Comandi: \n'
        new_message += 'track - aggiunge il link del gioco alla tua lista \n'
        new_message += 'list - mostra i giochi della tua lista \n'
        new_message += 'delete - cancella elementi dalla tua lista \n\n'
        new_message += 'Se hai problemi o vuoi segnalarmi bug scrivimi a @matteo_baldelli \n'
        new_message += '<a href="https://www.paypal.me/MatteoBaldelli">Donate</a> \n'
        new_message += '<a href="https://telegram.me/storebot?start=g2apricebot">Rate me</a>'
        keyboard = standard_keyboard
        disable_web_page_preview = True
    else:
        user.state = 'error'
        keyboard = standard_keyboard

    user.save()
    bot.send_message(
        chat_id,
        new_message,
        parse_mode='HTML',
        disable_web_page_preview=disable_web_page_preview,
        reply_markup=keyboard,
    )

    return 'OK'
