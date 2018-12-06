from flaskDemo import db, login_manager
from flask_login import UserMixin

db.Model.metadata.reflect(db.engine)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['user']


class Landmarks(db.Model):
    __table__ = db.Model.metadata.tables['landmarks']


class Favorites(db.Model):
    __table__ = db.Model.metadata.tables['favorites']

class Neighborhoods(db.Model):
    __table__ = db.Model.metadata.tables['neighborhoods']
    
