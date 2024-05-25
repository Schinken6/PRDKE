from datetime import datetime

from flask import request, render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, BuyTicketForm, NewPromotionForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app.models import User, Ticket, Promotion
from flask_login import logout_user, login_required
from urllib.parse import urlsplit
from app.forms import EditProfileForm

@app.route('/')
@app.route('/index')
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
    tickets = [
        {
            'owner': {'username': 'Max'},
            'price': 10.05
        },
        {
            'owner': {'username': 'Anja'},
            'price': 33.45
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts, tickets=tickets)

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
        if user.is_admin is True:
            return redirect(url_for('admin'))

        return redirect(url_for('index'))

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
        user = User(
            username=form.username.data,
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            street=form.street.data,
            zip=form.zip.data,
            city=form.city.data,
            is_admin=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Herzlich Willkommen, du bist nun ein registrierter Benutzer!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    tickets = db.session.query(Ticket).filter_by(user_id=current_user.id).all()
    return render_template('user.html', user=user, tickets=tickets)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    promotions = Promotion.query.all()
    return render_template('admin.html', title='Admin Seite', promotions=promotions)

@app.route('/add_promotion', methods=['GET', 'POST'])
@login_required
def new_promotion():
    form = NewPromotionForm()
    today_date = datetime.today().strftime('%Y-%m-%d')
    if form.validate_on_submit():
        promotion = Promotion(
            name=form.name.data,
            discount=form.discount.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            route=form.route.data if form.route.data != '' else None,
            global_promotion=form.global_promotion.data
        )
        db.session.add(promotion)
        db.session.commit()
        flash('Neue Aktion erfolgreich erstellt!')
        return redirect(url_for('admin'))
    return render_template('add_promotion.html', title='Neue Aktion anlegen', form=form, today_date=today_date)

@app.route('/delete_promotion/<int:promotion_id>', methods=['GET'])
@login_required
def delete_promotion(promotion_id):
    promotion = Promotion.query.get_or_404(promotion_id)
    ticket_count = db.session.query(Ticket).filter(Ticket.promotion_id == promotion_id).count()
    if ticket_count > 0:
        flash('Die Aktion kann nicht gelöscht werden, da sie bereits auf %d gekaufte Tickets angewandt wurde!' % ticket_count, 'error')
        return redirect(url_for('admin'))
    db.session.delete(promotion)
    db.session.commit()
    flash('Promotion erfolgreich gelöscht!', 'success')
    return redirect(url_for('admin'))
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Änderungen wurden gespeichert!.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Profil bearbeiten',
                           form=form)

@app.route('/buyticket', methods=['GET', 'POST'])
@login_required
def buy_ticket():
    form = BuyTicketForm()
    if form.validate_on_submit():
        t = Ticket(
            user_id=current_user.id,
            price=form.price.data,
            departure_date=form.departure_date.data,
            arrival_date=form.arrival_date.data,
            start_station=form.start_station.data,
            end_station=form.end_station.data,
            status=form.status.data
        )
        db.session.add(t)
        db.session.commit()

        flash('Ticket erfolgreich gekauft!')
        return redirect(url_for('user', username=current_user.username))
    return render_template('buy_ticket.html', title='Buy Ticket', form=form)

@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        if ticket.owner == current_user:
            db.session.delete(ticket)
            db.session.commit()
            flash('Ticket erfolgreich gelöscht.', 'success')
        else:
            flash('Sie sind nicht berechtigt, dieses Ticket zu löschen.', 'error')
    else:
        flash('Ticket nicht gefunden.', 'error')
    return redirect(url_for('user', username=current_user.username))


@app.route('/update_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        if ticket.owner == current_user:
            new_price = request.form.get('price')
            ticket.price = new_price

            new_departure_date = datetime.strptime(request.form.get('departure_date'), '%Y-%m-%d').date()
            ticket.departure_date = new_departure_date

            new_arrival_date = datetime.strptime(request.form.get('arrival_date'), '%Y-%m-%d').date()
            ticket.arrival_date = new_arrival_date

            new_start_station = request.form.get('start_station')
            ticket.start_station = new_start_station

            new_end_station = request.form.get('end_station')
            ticket.end_station = new_end_station

            new_status = request.form.get('status')
            ticket.status = new_status

            db.session.commit()
            flash('Ticket erfolgreich aktualisiert.', 'success')
        else:
            flash('Sie sind nicht berechtigt, dieses Ticket zu aktualisieren.', 'error')
    else:
        flash('Ticket nicht gefunden.', 'error')
    return redirect(url_for('user', username=current_user.username))