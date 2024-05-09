from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app
from app.forms import LoginForm, TrainstationForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User
from urllib.parse import urlsplit
from app.models import Station

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home',  posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/trainstation')
@login_required
def trainstation():
    stations = Station.query.all()
    return render_template('trainstation.html', title='Trainstation',stations = stations)

@app.route('/trainsstationNew', methods=['GET', 'POST'])
@login_required
def trainstationNew():
    form = TrainstationForm()
    if form.validate_on_submit():
        trainstation = Station(name=form.name.data, street=form.street.data, no=form.no.data, zipcode=form.zipcode.data,city=form.city.data, country=form.country.data)
        db.session.add(trainstation)
        db.session.commit()
        flash('Bahnhof angelegt!')
        return redirect(url_for('trainstation'))

    return render_template('trainstationNew.html', title='New Trainstation', form = form)

@app.route('/trainsstationEdit/<station_id>', methods=['GET', 'POST'])
@login_required
def trainstationEdit(station_id):
    station = Station.query.get_or_404(station_id)
    form = TrainstationForm(obj=station)
    if form.validate_on_submit():
        station.name = form.name.data
        station.street = form.street.data
        station.no = form.no.data
        station.zipcode = form.zipcode.data
        station.city = form.city.data
        station.country = form.country.data
        db.session.add(station)
        db.session.commit()
        flash('Änderungen gespeichert!')
        return redirect(url_for('trainstation'))
    return render_template('trainstationNew.html', title='Edit Trainstation', form=form)

@app.route('/trainsstationDelete/<station_id>', methods=['GET', 'POST'])
@login_required
def trainstationDelete(station_id):
    deletestation = Station.query.get_or_404(station_id)
    # if request.method == 'POST':
    db.session.delete(deletestation)
    db.session.commit()
    return redirect(url_for('trainstation'))

@app.route('/Bahnhof/all')
def all_stations():
    stations = Station.query.all()
    stations_list = []

    for station in stations:
        station_dict = {
            'id': station.id,
            'name': station.name,
            'street': station.street,
            'no': station.no,
            'zipcode': station.zipcode,
            'city': station.city,
            'country': station.country
        }
        stations_list.append(station_dict)

    return jsonify(stations_list)
