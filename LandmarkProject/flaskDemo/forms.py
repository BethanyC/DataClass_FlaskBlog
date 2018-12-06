from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import User, Landmarks, Neighborhoods, Favorites

landmark_neighborhood = Landmarks.query.with_entities(Landmarks.neighborhood).distinct()
ln_choices = [(row[0],row[0]) for row in landmark_neighborhood]

user_neighborhood = Neighborhoods.query.with_entities(Neighborhoods.neighborhood).distinct()
un_choices = [(row[0],row[0]) for row in user_neighborhood]

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
    submit = SubmitField('Explore!')

def add_query():
    return Landmarks.query.all()
    # return Landmarks.query \
    # .outerjoin(Favorites,Favorites.landmark_id == Landmarks.id) \
    # .filter(Favorites.user_id != current_user.id).with_entities(Landmarks)

class AddFavForm(FlaskForm):
    landmark = QuerySelectField('Select Landmark', query_factory=add_query, get_label='name')
    visited = BooleanField('Visited?')
    submit1 = SubmitField('Add to my Favorites')

def delete_query():
    return Favorites.query.filter_by(user_id=current_user.id) \
    .join(Landmarks,Landmarks.id == Favorites.landmark_id).with_entities(Landmarks)

class UpdateFavForm(FlaskForm):
    landmark = QuerySelectField('Select Landmark', query_factory=delete_query, get_label='name')
    visited = BooleanField('Visited?')
    submit2 = SubmitField('Update Favorites')

class DeleteFavForm(FlaskForm):
    landmark = QuerySelectField('Select Landmark', query_factory=delete_query, get_label='name')
    submit3 = SubmitField('Remove from Favorites')

