from flask import render_template, flash, redirect, url_for, jsonify
from wtforms.fields.list import FieldList
from wtforms.fields.simple import StringField, BooleanField

from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import db
from app.forms import RegistrationForm
from app.models import User, Stationplan
from flask_login import logout_user
from flask_login import login_required
from flask import request
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.forms import EditProfileForm
from app.forms import StationplanForm

@app.route('/')
@app.route('/index')
@login_required
def index():
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
    return render_template("index.html", title='Home Page', posts=posts)

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
        return redirect(url_for('index'))
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)




@app.route('/stationplan', methods=['GET', 'POST'])
@login_required
def stationplan():
    form = StationplanForm()
    if request.method == 'POST':
        name_ = request.form['name']
        startstation_= request.form['startstation']
        endstation_ = request.form['endstation']
        price_ = request.form['price']
        new_stationplan= Stationplan(name=name_,startstation=startstation_, endstation=endstation_, price=price_)
        try:
            db.session.add(new_stationplan)
            db.session.commit()
            stationplans = Stationplan.query.order_by(Stationplan.id).all()
            return render_template('stationplan.html', title='Halteplan',
                               stationplans=stationplans, form=form)
        except:
            return 'There was an error'
    else:
        stationplans= Stationplan.query.order_by(Stationplan.id).all()
    return render_template('stationplan.html', title='Halteplan',
                            stationplans=stationplans ,form=form)

@app.route('/stationplan/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    station_delete= Stationplan.query.get_or_404(id)
    try:
        db.session.delete(station_delete)
        db.session.commit()

        return redirect(url_for('stationplan'))
        stationplans = Stationplan.query.order_by(Stationplan.id).all()
        return render_template('stationplan.html', title='Halteplan',
                               stationplans=stationplans)
    except:
        'There was an issue'
    else:
        stationplans = Stationplan.query.order_by(Stationplan.id).all()
    return render_template('stationplan.html', title='Halteplan',
                           stationplans=stationplans)

@app.route('/stationplan/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    station_update= Stationplan.query.get_or_404(id)
    if request.method == 'POST':
        station_update.name= request.form['name']
        station_update.startstation= request.form['startstation']
        station_update.endstation = request.form['endstation']
        station_update.price = request.form['price']
        try:
            db.session.commit()
            return redirect(url_for('stationplan'))
            stationplans = Stationplan.query.order_by(Stationplan.id).all()
            return render_template('stationplan.html', title='Halteplan',
                                   stationplans=stationplans)
        except:
            return 'There was an issue'
    else:
        stationplans = Stationplan.query.order_by(Stationplan.id).all()
        return render_template('stationplanupdate.html', title='Halteplan', stationplan=station_update)


