from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User
from wtforms import TextAreaField, DecimalField, SelectField
from wtforms.validators import Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Einloggen')

class RegistrationForm(FlaskForm):
    firstname = StringField('Vorname', validators=[DataRequired()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    zip = StringField('Postleitzahl', validators=[DataRequired()])
    city = StringField('Stadt', validators=[DataRequired()])
    street = StringField('Straße/Nr', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('Vorname', validators=[DataRequired()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    zip = StringField('Postleitzahl', validators=[DataRequired()])
    city = StringField('Stadt', validators=[DataRequired()])
    street = StringField('Straße', validators=[DataRequired()])
    password = PasswordField('Neues Passwort', validators=[EqualTo('confirm', message='Passwörter müssen übereinstimmen')])
    confirm = PasswordField('Passwort bestätigen')
    submit = SubmitField('Änderungen speichern')

    def __init__(self, current_user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.id != self.current_user.id:
            raise ValidationError('Dieser Benutzername ist bereits vergeben.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != self.current_user.id:
            raise ValidationError('Diese E-Mail-Adresse ist bereits vergeben.')


class BuyTicketForm(FlaskForm):
    price = StringField('Preis', validators=[DataRequired()])
    departure_date = DateField('Abfahrtsdatum', validators=[DataRequired()], format='%Y-%m-%d')
    arrival_date = DateField('Ankunftsdatum', validators=[DataRequired()], format='%Y-%m-%d')
    start_station = StringField('Start Haltestelle', validators=[DataRequired()])
    end_station = StringField('End Haltestelle', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()])
    submit = SubmitField('Kaufen')

class NewPromotionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    discount = DecimalField('Rabatt (%)', validators=[DataRequired()])
    start_date = DateField('Startdatum', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('Enddatum', validators=[DataRequired()], format='%Y-%m-%d')
    route = SelectField('Strecke (optional)', validators=[],
                        choices=[('',''), ('LINZ-WELS', 'LINZ-WELS'), ('WIEN-GRAZ', 'WIEN-GRAZ')])
    global_promotion = BooleanField('globale Aktion')
    submit = SubmitField('Speichern')
