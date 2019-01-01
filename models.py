from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer)
    chat_username = db.Column(db.String)
    state = db.Column(db.String)
    update_date = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    creation_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def __init__(self, chat_id, chat_username, state):
        self.chat_id = chat_id
        self.chat_username = chat_username
        self.state = state

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Track(db.Model):
    __tablename__ = 'track'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    game_id = db.Column(db.String)
    game_link = db.Column(db.String)
    game_price = db.Column(db.Float, nullable=True)
    game_median_price = db.Column(db.Float, nullable=True)
    creation_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='track')
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='unique_name'),)

    def __init__(self, name, game_id, game_link, game_price, game_median_price, user):
        self.name = name
        self.game_id = game_id
        self.game_link = game_link
        self.game_price = game_price
        self.game_median_price = game_median_price
        self.user = user

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Track.query.all()
