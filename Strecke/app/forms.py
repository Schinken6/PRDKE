from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, TextAreaField, \
    DateTimeField, DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from .models import Station

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class TrainstationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    street = StringField('Street', validators=[DataRequired()])
    no = StringField('No', validators=[DataRequired()])
    zipcode = StringField('Zipcode', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    street = StringField('Street', validators=[DataRequired()])
    no = StringField('No', validators=[DataRequired()])
    zipcode = StringField('Zipcode', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    is_admin = BooleanField('Admin')
    submit = SubmitField('Register')


class SegmentForm(FlaskForm):
    startStation = SelectField('Start Station', coerce=int, validators=[DataRequired()])
    endStation = SelectField('End Station', coerce=int, validators=[DataRequired()])
    trackWidth = IntegerField('Track Width', validators=[DataRequired()])
    length = StringField('Length', validators=[DataRequired()])
    maxSpeed = IntegerField('Max Speed', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SegmentForm, self).__init__(*args, **kwargs)
        self.startStation.choices = [(station.id, station.name) for station in Station.query.all()]
        self.endStation.choices = [(station.id, station.name) for station in Station.query.all()]


    def validate_endStation(self, endStation):
        if self.startStation.data == endStation.data:
            raise ValidationError('Start station cannot be the same as the end station.')





class WarningForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    validFrom = DateField('Valid From', format='%Y-%m-%d', validators=[DataRequired()])
    validTo = DateField('Valid To', format='%Y-%m-%d', validators=[DataRequired()])
    segment = SelectField('Segment', coerce=int)
    submit = SubmitField('Create')