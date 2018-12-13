from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import create_engine
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://<username>:<password>@localhost/chicago_landmarks'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

try:
    conn = mysql.connector.connect(host='localhost',
                                   database='chicago_landmarks',
                                   user='<username>',
                                   password='<password>')
except Error as e:
    print(e)

from landmarkProject import routes
from landmarkProject import models

models.db.create_all()