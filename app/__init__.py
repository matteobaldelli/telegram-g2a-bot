import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

SENTRY_URL = os.environ.get('SENTRY_URL', '')


db = SQLAlchemy()


def create_app():
    sentry_sdk.init(
        dsn=SENTRY_URL,
        integrations=[FlaskIntegration()]
    )
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    db.init_app(app)

    return app
