from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db, conn
from flaskDemo.models import User, Landmarks, Neighborhoods, Favorites
import mysql.connector
from sqlalchemy import not_


landmark_neighborhood = Landmarks.query.with_entities(Landmarks.neighborhood).distinct()
ln_choices = [(row[0],row[0]) for row in landmark_neighborhood]

landmark_architect = Landmarks.query.with_entities(Landmarks.architect).distinct()
la_choices = [(row[0],row[0]) for row in landmark_architect]

user_neighborhood = Neighborhoods.query.with_entities(Neighborhoods.neighborhood).distinct()
un_choices = [(row[0],row[0]) for row in user_neighborhood]

# this wasn't updating without restarting the program, after googling I believe it was because it is on a separate db connection than the update
# not_favorite = []

# if conn.is_connected():
#     cursor = conn.cursor(dictionary=True)
#     try:
#         if_user = " OR favorites.user_id!=" + str(current_user.id)
#     except:
#         if_user = ""
#     cursor.execute("SELECT landmarks.name, landmarks.id FROM landmarks LEFT JOIN favorites ON landmarks.id = favorites.landmark_id WHERE favorites.user_id IS NULL" + if_user + ";")
#     row = cursor.fetchone()
#     while row is not None:
#         not_favorite.append((row['id'], row['name']))
#         row = cursor.fetchone()

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    neighborhood = SelectField("Select your Neighborhood", choices=un_choices)
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    neighborhood = SelectField("Select your Neighborhood", choices=un_choices)
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class HomeForm(FlaskForm):
    neighborhood = SelectField("Choose a Neighborhood", choices=ln_choices)
    submit1 = SubmitField('Explore!')

class HomeForm2(FlaskForm):
    architect = SelectField("Choose an Architect", choices=la_choices)
    submit2 = SubmitField('Explore!')

def add_query():
    return Landmarks.query.filter(not_(Landmarks.id.in_(Favorites.query.filter_by(user_id=2).with_entities(Favorites.landmark_id).all()))).all()

def delete_query():
    return Favorites.query.filter_by(user_id=current_user.id) \
    .join(Landmarks,Landmarks.id == Favorites.landmark_id).with_entities(Landmarks)

class AddFavForm(FlaskForm):
    landmark = QuerySelectField('Select Landmark', query_factory=add_query, get_label='name', validators=[DataRequired()])
    # landmark = SelectField('Select Landmark', choices=not_favorite, coerce=int, validators=[DataRequired()])
    visited = BooleanField('Visited?')
    submit1 = SubmitField('Add to my Favorites')

class UpdateFavForm(FlaskForm):
    landmark = QuerySelectField('Select Landmark', query_factory=delete_query, get_label='name', validators=[DataRequired()])
    visited = BooleanField('Visited?')
    submit2 = SubmitField('Update Favorites')

class DeleteFavForm(FlaskForm):
    landmark = QuerySelectField('Select Landmark', query_factory=delete_query, get_label='name', validators=[DataRequired()])
    submit3 = SubmitField('Remove from Favorites')

class AddFavForm2(FlaskForm):
    visited = BooleanField('Visited?')
    submit = SubmitField('Add to my Favorites')