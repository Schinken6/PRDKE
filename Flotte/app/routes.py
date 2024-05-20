from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request, jsonify
#from flask_cors import CORS
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddRailcarForm
from app.models import User, Railcar


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
    railcars = [
        {
            'owner': {'username': 'Max'},
            'track_width': 10.05
        },
        {
            'owner': {'username': 'Anja'},
            'track_width': 33.45
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts, railcars=railcars)


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
        flash('Herzlichen Glückwunsch, Sie sind jetzt ein registrierter Benutzer!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    railcars = db.session.query(Railcar).filter_by(user_id=current_user.id).all()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('wagen_verwalten.html', user=user, posts=posts, railcars=railcars)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Ihre Änderungen wurden gespeichert.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)



@app.route('/addtrain', methods=['GET', 'POST'])
@login_required
def train():
    form = AddRailcarForm()
    if form.validate_on_submit():
        t = Railcar(
            user_id=current_user.id,
            track_width=form.track_width.data,
            max_tensile_force=form.max_tensile_force.data
        )
        db.session.add(t)
        db.session.commit()

        flash('Triebwagen erfolgreich hinzugefügt')
        return redirect(url_for('user', username=current_user.username))
    return render_template('train.html', title='Add railcar', form=form)


@app.route('/delete_railcar/<int:railcar_id>', methods=['POST'])
@login_required
def delete_railcar(railcar_id):
    railcar = Railcar.query.get(railcar_id)
    if railcar:
        if railcar.owner == current_user:
            db.session.delete(railcar)
            db.session.commit()
            flash('Triebwagen erfolgreich gelöscht', 'success')
        else:
            flash('Sie sind nicht berechtigt, diesen Triebwagen zu löschen', 'error')
    else:
        flash('Triebwagen nicht gefunden.', 'error')

    return redirect(url_for('user', username=current_user.username))


@app.route('/update_railcar/<int:railcar_id>', methods=['POST'])
@login_required
def update_railcar(railcar_id):
    railcar = Railcar.query.get(railcar_id)
    if railcar:
        if railcar.owner == current_user:
            new_track_width = request.form.get('track_width')
            railcar.track_width = new_track_width

            new_max_tensile_force = request.form.get('max_tensile_force')
            railcar.max_tensile_force = new_max_tensile_force

            db.session.commit()
            flash('Triebwagen erfolgreich aktualisiert', 'success')
        else:
            flash('Sie sind nicht berechtig wie auch immer dieser Fehler passieren sollte diesen Triebwagen zu aktualisieren', 'error')
    else:
        flash('Triebwagen nicht gefunden', 'error')
    return redirect(url_for('user', username=current_user.username))





@app.route('/api/railcars/<username>', methods=['GET'])
@login_required
def api_railcars(username):
    user = User.query.filter_by(username=username).first_or_404()
    railcars = Railcar.query.filter_by(owner_id=user.id).all()
    return jsonify([{
        'owner': rc.owner.username,
        'track_width': rc.track_width,
        'max_tensile_force': rc.max_tensile_force
    } for rc in railcars])



# no matter the origin it always works
#CORS(app, resources={r"/api/*": {"origins": "1.1.1.1"}})

@app.route('/api/railcars', methods=['GET'])
def get_railcars():
    railcars = Railcar.query.all()
    return jsonify([railcar.serialize() for railcar in railcars])

