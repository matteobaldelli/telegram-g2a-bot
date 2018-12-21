import os
import time
import telegram

from app import create_app

HOST = os.environ.get('HOST_URL')
PORT = int(os.environ.get('PORT', '8443'))
TOKEN = os.environ.get('TELEGRAM_TOKEN')


app = create_app()
bot = telegram.Bot(TOKEN)

if __name__ == '__main__':
    print('ciao')
    time.sleep(1)
    bot.setWebhook(url='%s/%s' % (HOST, TOKEN))
    app.run(host='0.0.0.0', port=PORT)
