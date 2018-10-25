from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class CreateForm(FlaskForm):
    user_id = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    title = StringField('Title',
                        validators=[DataRequired(), Length(min=2, max=60)])
    date_posted = DateTimeField('Date and Time', validators=[DataRequired()])
    content = StringField('Content',
                        validators=[DataRequired(), Length(min=2, max=800)])
    submit = SubmitField('Post!')