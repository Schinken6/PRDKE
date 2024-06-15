from datetime import date, datetime, timedelta
from flask import session, request, render_template, flash, redirect, url_for, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm, BuyTicketForm, NewPromotionForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app.models import User, Ticket, Promotion, Section
from flask_login import logout_user, login_required
from urllib.parse import urlsplit
from app.forms import EditProfileForm
import requests


@app.route('/')
@app.route('/index')
def index():
    response = requests.get('http://localhost/api/railwayschedules')
    data = response.json()

    start_stations = set()
    end_stations = set()
    for item in data:
        for schedule in item['stationplan']:
            start_stations.add(schedule['start'])
            end_stations.add(schedule['end'])

    start_stations = sorted(list(start_stations))
    end_stations = sorted(list(end_stations))

    return render_template('index.html', title='Home Page', start_stations=start_stations, end_stations=end_stations)


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

    # Überprüfen, ob alle Routen eines Tickets veraltet sind und den Status aktualisieren
    for ticket in tickets:
        sections = db.session.query(Section).filter_by(ticket_id=ticket.id).all()
        all_sections_expired = True
        for section in sections:
            if section.end_date > datetime.now().date() or (
                    section.end_date == datetime.now().date() and section.end_time > datetime.now().time()):
                all_sections_expired = False
                break

        if all_sections_expired and ticket.status != 'verbraucht':
            ticket.status = 'verbraucht'
            db.session.commit()

    return render_template('user.html', user=user, tickets=tickets,
                           sections={ticket.id: db.session.query(Section).filter_by(ticket_id=ticket.id).all() for
                                     ticket in tickets})


@app.route('/cancel_ticket/<int:ticket_id>', methods=['POST'])
def cancel_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = 'storniert'
    db.session.commit()
    flash('Ticket erfolgreich storniert', 'success')
    return redirect(url_for('user', username=current_user.username))

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

    # API-Aufruf, um die Strecken zu erhalten
    response = requests.get('http://localhost:5001/Strecken')
    if response.status_code == 200:
        routes = response.json()
        form.route.choices = [(route['id'], f"{route['startbahnhof']} - {route['endbahnhof']}") for route in routes]

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

        if start_date < datetime.today().date():
            flash('Das Startdatum darf nicht in der Vergangenheit liegen.', 'error')
            form.global_promotion.checked = False  # soll im Fehlerfall wieder zurückgesetzt werden
        elif end_date < start_date:
            flash('Das Enddatum darf nicht vor dem Startdatum liegen.', 'error')
            form.global_promotion.checked = False  # soll im Fehlerfall wieder zurückgesetzt werden
        else:
            promotion = Promotion(
                name=form.name.data,
                discount=form.discount.data,
                start_date=start_date,
                end_date=end_date,
                route=form.route.data if form.route.data else None,
                global_promotion=form.global_promotion.data
            )
            db.session.add(promotion)
            db.session.commit()
            flash('Neue Aktion erfolgreich erstellt!')
            return redirect(url_for('admin'))
    else:
        print("Form validation failed")
        print(form.errors)

    return render_template('add_promotion.html', title='Neue Aktion anlegen', form=form, today_date=today_date)
@app.route('/delete_promotion/<int:promotion_id>', methods=['GET'])
@login_required
def delete_promotion(promotion_id):
    promotion = Promotion.query.get_or_404(promotion_id)
    if(check_promotion_editable(promotion_id, promotion)): #überprüfen ob schon Tickets verkauft wurden
        db.session.delete(promotion)
        db.session.commit()
        flash('Promotion erfolgreich gelöscht!', 'success')
    return redirect(url_for('admin'))

@app.route('/edit_promotion/<int:promotion_id>', methods=['GET', 'POST'])
@login_required
def edit_promotion(promotion_id):
    promotion = Promotion.query.get_or_404(promotion_id)
    if(check_promotion_editable(promotion_id, promotion)): #überprüfen ob schon Tickets verkauft wurden
        form = NewPromotionForm(obj=promotion) # automatisch befüllen

        # API-Aufruf, um die Strecken zu erhalten
        response = requests.get('http://localhost:5001/Strecken')
        if response.status_code == 200:
            routes = response.json()
            route_choices = [(route['id'], f"{route['startbahnhof']} - {route['endbahnhof']}") for route in routes]

        if(form.route.data):
                form.route.data = form.route.data
        else:
            route_choices.insert(0, (0, ""))
            form.route.data = 0

        form.route.choices = route_choices

        if form.validate_on_submit():
            start_date = form.start_date.data
            end_date = form.end_date.data

            if start_date < datetime.today().date():
                flash('Das Startdatum darf nicht in der Vergangenheit liegen.', 'error')
                form.global_promotion.checked = False  # soll im Fehlerfall wieder zurückgesetzt werden
            elif end_date < start_date:
                flash('Das Enddatum darf nicht vor dem Startdatum liegen.', 'error')
                form.global_promotion.checked = False  # soll im Fehlerfall wieder zurückgesetzt werden
            else:
                promotion.name = form.name.data
                promotion.discount = form.discount.data
                promotion.start_date = start_date
                promotion.end_date = end_date
                promotion.route = form.route.data if not form.global_promotion.data else None
                promotion.global_promotion = form.global_promotion.data

                db.session.commit()
                flash('Aktion erfolgreich bearbeitet!', 'success')
                return redirect(url_for('admin'))
    else:
        return redirect(url_for('admin'))

    return render_template('edit_promotion.html', title='Aktion bearbeiten', form=form, promotion=promotion)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user, obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.zip = form.zip.data
        current_user.city = form.city.data
        current_user.street = form.street.data
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Dein Profil wurde aktualisiert.', 'success')
        return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)

def check_promotion_editable(promotion_id, promotion):
    ticket_count = db.session.query(Section).filter(Section.promotion_id == promotion_id).count()
    if ticket_count > 0:
        flash(
            'Die Aktion kann nicht editiert bzw. gelöscht werden, da sie bereits auf %d gekaufte Tickets angewandt wurde!' % ticket_count,
            'error')
        return False
    return True

@app.route('/buyticket', methods=['GET', 'POST']) # Wurde nur für technischen Durchstich zur Veranschauligung der Persistierung einer Entität verwendet
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


@app.route('/update_ticket/<int:ticket_id>', methods=['POST']) # war nur für technischen Durchstich
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

@app.route('/search_tickets', methods=['POST'])
def search_tickets():
    # Zwischenspeicher löschen
    session.pop('ticketswithswitch', None)
    session.pop('tickets', None)

    form_start_station = request.form['from']
    form_end_station = request.form['to']
    date = request.form['date']
    start_time = request.form['time']

    # Prüfen, ob Datum und Zeit ausgefüllt sind
    if not date or not start_time:
        flash('Bitte geben Sie sowohl ein Datum als auch eine Startzeit an.', 'error')
        return redirect(url_for('index'))

    # Prüfen, ob sich Start- und Endbahnhof unterscheiden
    if form_start_station == form_end_station:
        flash('Startbahnhof und Endbahnhof müssen sich unterscheiden.', 'error')
        return redirect(url_for('index'))

    start_time = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    end_time = start_time + timedelta(hours=24)  # Ergebnisse sollen maximal 24h nach Startzeit angezeigt werden

    print(f"Startzeit als datetime: {start_time}, Endzeit: {end_time}")

    response = requests.get('http://localhost/api/railwayschedules') # alle Fahrpläne von API abfragen
    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")
    schedules = [schedule for schedule in response.json() if schedule['date'] == formatted_date] # alle Pläne vom selben Tag filtern
    print(schedules)

    filtered_schedules = find_transfer(schedules, form_start_station, form_end_station, start_time, end_time) # Direktverbindung suchen

    if isinstance(filtered_schedules, list): # Direktverbindung gefunden?
        print(f"Gefundene Fahrten: {filtered_schedules}")
        session['tickets'] = filtered_schedules  # Zwischenspeichern für Kauf-Methode
        return redirect(url_for('show_tickets'))
    else: # keine Direktverbindung gefunden
        print("Keine direkten Fahrten gefunden, suche nach möglichen Umstiegen.")
        after_switch = "Fehler"
        for schedule in schedules:
            route_stations = [segment['start'] for segment in schedule['stationplan']] + [schedule['stationplan'][-1]['end']] # alle Bahnhöfe des Stationplans (alle Startbahnhöfe und der letzte Endbahnhof)
            print(f"Route-Stationen für den Zeitplan {schedule['railwayscheduleid']}: {route_stations}")
            for segment in schedule['stationplan']: # jeder Abschnitt im Stationplan
                actual_station = segment['start'] # aktuelle Station
                print(f"Überprüfung der Station {actual_station} für mögliche Umstiege.")
                if (form_start_station in route_stations and actual_station in route_stations and \
                        route_stations.index(form_start_station) < route_stations.index(actual_station)): # Starthaltestelle muss auf der selben Strecke wie die Endhaltestelle liegen und in der Reihenfolge davor
                    print(f"Before Switch grundsätzlich möglich: Von {form_start_station} bis {actual_station}")
                    before_switch = find_transfer(schedules, form_start_station, actual_station, start_time, end_time) # Strecke vor der potentiellen Umstiegsstelle abfragen
                    if isinstance(before_switch, list): # Wenn mindestens eine Strecke verfügbar ist
                        print(f"Checke Route von {actual_station} nach {form_end_station}")
                        after_switch = find_transfer(schedules, actual_station, form_end_station, # Strecke nach der potentiellen Umstiegsstelle berechnen
                                                     datetime.strptime(before_switch[0]['arrival_time'], "%H:%M"),
                                                     end_time)
                        if isinstance(after_switch, list): # Umstiegsstelle ist vorhanden
                            print(f"Vor dem Umstieg gefundene Fahrten: {before_switch}")
                            print(f"Nach dem Umstieg gefundene Fahrten: {after_switch}")

                            # Gibt es Fahrten, die bei der Umstiegsstelle mehr als 0min und weniger als 4h Wartezeit haben?
                            valid_tickets = []
                            for before in before_switch:
                                for after in after_switch:
                                    before_arrival_time = datetime.strptime(before['arrival_time'], "%H:%M")
                                    after_departure_time = datetime.strptime(after['departure_time'], "%H:%M")
                                    # Prüfe ob die Umstiegszeit innerhalb einer akzeptablen Spanne liegt (zwischen 0 min und 4 Stunden)
                                    if 0 < (after_departure_time - before_arrival_time).total_seconds() / 60 <= 240:
                                        waiting_time = datetime.strptime(after['departure_time'], "%H:%M") - datetime.strptime(before['arrival_time'], "%H:%M") # Wartezeit berechnen
                                        combined_ticket = { # Pseudo Ticket erstellen
                                            'train_name': f"{before['train_name']} mit Umstieg auf {after['train_name']} in {actual_station} um {after['departure_time']} (mit {waiting_time} Minuten Wartezeit)",
                                            'departure_time': before['departure_time'],
                                            'departure_date': before['departure_date'],
                                            'arrival_time': after['arrival_time'],
                                            'arrival_date': after['arrival_date'],
                                            'before_switch': before,
                                            'after_switch': after,
                                            'price': f"{(float(before['price'].strip('€')) + float(after['price'].strip('€'))):.2f}€",
                                            'discount': "siehe Kauf-Zusammenfassung"
                                        }
                                        valid_tickets.append(combined_ticket) # zu Liste hinzufügen
                                        print(f"Gefundene gültige Verbindung: {combined_ticket}")

                            if valid_tickets: # wenn Tickets vorhanden sind, auf nächster Seite anzeigen
                                session['ticketswithswitch'] = valid_tickets # Zwischenspeichern für Kauf-Methode
                                return redirect(url_for('show_tickets'))
                            else:
                                print("Keine gültigen Verbindungen mit akzeptabler Umstiegszeit gefunden.")
                        else:
                            print("Keine nach dem Umstieg gefundenen Fahrten verfügbar.")
                    else:
                        print("Keine vor dem Umstieg gefundenen Fahrten verfügbar.")

        print("Fehler oder keine gültigen Umstiegsverbindungen gefunden.")
    return render_template('error.html')


def find_transfer(schedules, form_start_station, form_end_station, start_time, end_time):
    filtered_schedules = []
    valid_route_found = False

    for schedule in schedules: # Alle Stationspläne durchiterieren
        schedule_start_time = datetime.strptime(f"{schedule['date']} {schedule['time']}", "%d.%m.%Y %H:%M")
        current_time = schedule_start_time # für Berechnung der Zeit je Station
        total_price = 0 # für aufsummierung von Preis
        processing_route = False
        route_stations = [segment['start'] for segment in schedule['stationplan']] + [
            schedule['stationplan'][-1]['end']]  # Erstelle Liste von Bahnhöfen

        # Gültigkeitsprüfung:
        # beide Bahnhöfe müssen in Stationsplan enthalten sein
        # der Zielbahnhof muss nach dem Startbahnhof liegen
        if not (form_start_station in route_stations and form_end_station in route_stations and \
                route_stations.index(form_start_station) < route_stations.index(form_end_station)):
            continue # zu nächstem Schleifendurchgang springen

        # Suche die Verbindung vom mitgegebenen Start- zum Endbahnhof
        # Summiere den Preis und aktualisiere die Zeit immer über die Duration (ab Startbahnhof)
        for segment in schedule['stationplan']:
            if segment['start'] == form_start_station: # Wenn Startbahnhof gefunden wurde
                if not (start_time <= current_time <= end_time): # Zeit bei dieser Haltestelle muss zwischen eingegebener Startzeit und festgelegter Endzeit liegen
                    continue # zu nächstem Schleifendurchgang springen
                processing_route = True # Bedingung für untenstehendes IF
                departure_time = current_time

            current_time += timedelta(minutes=segment['duration']) # aktualisierung der Zeit für aktuelle Station

            if processing_route: # Wenn Startbahnhof gefunden wurde
                if segment['end'] == form_end_station: # Wenn Endbahnhof gefunden wurde
                    arrival_time = current_time
                    total_price += segment['nutzungsentgeld']
                    break
                total_price += segment['nutzungsentgeld']

        if processing_route:
            valid_route_found = True # für Return
            discounted_price, promotion_id, best_discount = apply_best_promotion(schedule['routeid'], total_price)

            valid_route_found = True  # für Return
            filtered_schedules.append({
                'train_name': schedule['train']['train_name'],
                'departure_time': departure_time.strftime("%H:%M"),
                'departure_date': departure_time.strftime("%d.%m.%Y"),
                'arrival_time': arrival_time.strftime("%H:%M"),
                'arrival_date': arrival_time.strftime("%d.%m.%Y"),
                'start_station': form_start_station,
                'end_station': form_end_station,
                'price': f"{discounted_price:.2f}€",
                'route_id': schedule['routeid'],
                'promotion_id': promotion_id,
                'discount': f"{best_discount}%" if best_discount > 0 else None
            })

    if valid_route_found: # wenn mindestens eine Kombination von Start- und Endbahnhof gefunden wurde
        return filtered_schedules
    else: # Rückgabe von Fehlermeldung (keine Liste )
        return jsonify({'error': 'Die Fahrt ist in dieser Konstellation nicht möglich.'}), 400

def apply_best_promotion(route_id, price):
    today = date.today()
    promotions = db.session.query(Promotion).filter(
        ((Promotion.route == route_id) | (Promotion.global_promotion == True)) &
        (Promotion.start_date <= today) & (Promotion.end_date >= today)
    ).all()
    print(promotions)

    best_discount = 0
    best_promotion_id = None
    for promotion in promotions:
        if promotion.discount > best_discount:
            best_discount = promotion.discount
            best_promotion_id = promotion.id

    if best_discount > 0:
        price = price * (1 - best_discount / 100)

    return price, best_promotion_id, best_discount

@app.route('/show_tickets', methods=['GET']) # Tickets anzeigen
def show_tickets():
    if 'ticketswithswitch' in session:
        return render_template('show_tickets.html', tickets=enumerate(session.get('ticketswithswitch'))) # Umwandlung der Tickets aus Zwischenspeicher in enum mit Index
    elif 'tickets' in session:
        return render_template('show_tickets.html', tickets=enumerate(session.get('tickets'))) # Umwandlung der Tickets aus Zwischenspeicher in enum mit Index

@app.route('/purchase_ticket', methods=['POST']) # Ticket kaufen
def purchase_ticket():
    seat_info = "Es wurde kein Sitzplatz reserviert!" # für flash unten
    ticket_index = int(request.form.get('ticket_index')) # Index aus dem Formular holen
    reserve_seat = request.form.get('reserve_seat') == 'yes'  # Prüfen, ob Sitzplatz reserviert werden soll
    if 'ticketswithswitch' in session: # Wenn Tickets mit Umstieg vorhanden sind
        ticket_data = session['ticketswithswitch'][ticket_index]
    elif 'tickets' in session: # Wenn Tickets ohne Umstieg vorhanden sind
        ticket_data = session['tickets'][ticket_index]

    ## Für Sitzplatz 3€ ergänzen falls angekreuzt
    base_price = float(ticket_data['price'].replace('€', ''))
    total_price = base_price + 3 if reserve_seat else base_price

    # Ticket-Objekt erstellen
    ticket = Ticket(
        user_id=current_user.id,
        total_price=total_price,
        status='aktiv'
    )
    db.session.add(ticket)
    print("db session added:")
    print(ticket)

    if 'before_switch' in ticket_data:  # Hat das Ticket einen Umstieg
        if reserve_seat:
            seat_number_before = get_seat_number(ticket_data['before_switch'])
            seat_number_after = get_seat_number(ticket_data['after_switch'])
            if seat_number_before is None or seat_number_after is None:
                flash('Keine verfügbaren Sitzplätze für eine der Strecken', 'error')
                db.session.rollback()
                return redirect(url_for('show_tickets'))
            save_section(ticket_data['before_switch'], ticket, seat_number_before)
            save_section(ticket_data['after_switch'], ticket, seat_number_after)
            seat_info = f" Sitzplatznummern: {seat_number_before} (von {ticket_data['before_switch']['start_station']} bis {ticket_data['before_switch']['end_station']}) und {seat_number_after} (von {ticket_data['after_switch']['start_station']} bis {ticket_data['after_switch']['end_station']})"
        else:
            save_section(ticket_data['before_switch'], ticket)
            save_section(ticket_data['after_switch'], ticket)
    else:  # Kein Umstieg im Ticket
        if reserve_seat:
            seat_number = get_seat_number(ticket_data)
            if seat_number is None:
                flash('Keine verfügbaren Sitzplätze für die Strecke', 'error')
                db.session.rollback()
                return redirect(url_for('show_tickets'))
            save_section(ticket_data, ticket, seat_number)
            seat_info = f" Sitzplatznummer: {seat_number} (von {ticket_data['start_station']} bis {ticket_data['end_station']})"
        else:
            save_section(ticket_data, ticket)

    db.session.commit()
    flash(f'Ticket erfolgreich gekauft. {seat_info}', 'success')
    return redirect(url_for('user', username=current_user.username))


def get_seat_number(section_data):
    max_seats = 2 # muss noch von API abgefragt werden
    start_date = datetime.strptime(section_data['departure_date'], '%d.%m.%Y').date()
    start_time = datetime.strptime(section_data['departure_time'], '%H:%M').time()
    end_date = datetime.strptime(section_data['arrival_date'], '%d.%m.%Y').date()
    end_time = datetime.strptime(section_data['arrival_time'], '%H:%M').time()

    reserved_seats = db.session.query(Section).filter(
        Section.train_name == section_data['train_name'],
        Section.start_date == start_date,
        Section.seat_number.isnot(None)
    ).all()

    # Überprüfen, welche Sitzplatzreservierungen in diesem Zug zu der Zeit überlappend sind
    overlapping_reservations = 0
    for seat in reserved_seats:
        seat_start_time = datetime.combine(seat.start_date, seat.start_time)
        seat_end_time = datetime.combine(seat.end_date, seat.end_time)
        section_start_time = datetime.combine(start_date, start_time)
        section_end_time = datetime.combine(end_date, end_time)

        # Prüfen, ob es eine Überlappung der Zeiten gibt
        if (seat_start_time <= section_start_time < seat_end_time) or (
                seat_start_time < section_end_time <= seat_end_time):
            overlapping_reservations += 1

    if overlapping_reservations < max_seats:
        return overlapping_reservations + 1
    return None

def save_section(section_data, ticket, seat_number=None):
    section = Section(
        train_name=section_data['train_name'],
        seat_number=seat_number,
        start_station=section_data['start_station'],
        end_station=section_data['end_station'],
        start_date=datetime.strptime(section_data['departure_date'], '%d.%m.%Y').date(),
        end_date=datetime.strptime(section_data['arrival_date'], '%d.%m.%Y').date(),
        start_time=datetime.strptime(section_data['departure_time'], '%H:%M').time(),
        end_time=datetime.strptime(section_data['arrival_time'], '%H:%M').time(),
        price=float(section_data['price'].replace('€', '')),
        ticket=ticket,
        promotion_id=section_data['promotion_id']
    )
    db.session.add(section)
    print("db session added:")
    print(section)

@app.route('/ticket_details', methods=['POST']) # Ticket kaufen
def ticket_details():
    ticket_index = int(request.form.get('ticket_index')) # Index aus dem Formular holen
    if 'ticketswithswitch' in session:  # Wenn Tickets mit Umstieg vorhanden sind
        ticket_data = session['ticketswithswitch'][ticket_index]
    elif 'tickets' in session:  # Wenn Tickets ohne Umstieg vorhanden sind
        ticket_data = session['tickets'][ticket_index]
    else:
        flash('Kein Ticket in der Session gefunden.', 'error')
        return redirect(url_for('ticket_listing_route'))

    # Warnings von API abfragen
    warnings = []

    if 'before_switch' in ticket_data:  # Ticket mit Umstieg
        before_switch = ticket_data['before_switch']
        after_switch = ticket_data['after_switch']
        before_departure_time = datetime.strptime(
            f"{before_switch['departure_date']} {before_switch['departure_time']}", '%d.%m.%Y %H:%M')
        before_arrival_time = datetime.strptime(f"{before_switch['arrival_date']} {before_switch['arrival_time']}",
                                                '%d.%m.%Y %H:%M')
        after_departure_time = datetime.strptime(f"{after_switch['departure_date']} {after_switch['departure_time']}",
                                                 '%d.%m.%Y %H:%M')
        after_arrival_time = datetime.strptime(f"{after_switch['arrival_date']} {after_switch['arrival_time']}",
                                               '%d.%m.%Y %H:%M')

        warnings.extend(
            get_warnings(before_switch['route_id'], before_switch['start_station'], before_switch['end_station'],
                         before_departure_time, before_arrival_time))
        warnings.extend(
            get_warnings(after_switch['route_id'], after_switch['start_station'], after_switch['end_station'],
                         after_departure_time, after_arrival_time))
    else:  # Ticket ohne Umstieg
        departure_time = datetime.strptime(f"{ticket_data['departure_date']} {ticket_data['departure_time']}",
                                           '%d.%m.%Y %H:%M')
        arrival_time = datetime.strptime(f"{ticket_data['arrival_date']} {ticket_data['arrival_time']}",
                                         '%d.%m.%Y %H:%M')
        warnings.extend(get_warnings(ticket_data['route_id'], ticket_data['start_station'], ticket_data['end_station'],
                                     departure_time, arrival_time))

    print("Warnungen:", warnings)

    return render_template('ticket_details.html', ticket_data=ticket_data, ticket_index=ticket_index, warnings=warnings)


def get_warnings(route_id, departure_station, arrival_station, departure_time, arrival_time):
    url = f"http://localhost:5001/StreckeVonBis/{route_id}/{departure_station}/{arrival_station}/Warnungen"
    print(f"Abfrage von: {url}")

    response = requests.get(url)

    if response.status_code == 200:
        warnings = response.json()
        print(f"Warnings received: {warnings}")
        valid_warnings = []
        for warning in warnings:
            startzeitpunkt = datetime.strptime(warning['startzeitpunkt'], "%Y-%m-%dT%H:%M:%S")
            endzeitpunkt = datetime.strptime(warning['endzeitpunkt'], "%Y-%m-%dT%H:%M:%S")
            if startzeitpunkt <= departure_time <= endzeitpunkt or startzeitpunkt <= arrival_time <= endzeitpunkt:
                valid_warnings.append(f"{warning['name']}: {warning['beschreibung']}")
            else:
                print({warning['name']})
                print("Datum dieser Warning passt nicht zusammen")
        return valid_warnings
    else:
        print(f"Konnte Warnings nicht abgreifen: {response.status_code}")

    return []

@app.route('/api/railwayschedules', methods=['GET']) # temporäre eigene API, bis die API von Marko fertig ist
def api_railwayschedules():
    data = [
        {
            "date": "01.01.2024",
            "time": "08:00",
            "priceadjust_percent": 10,
            "railwayscheduleid": 1,
            "routeid": 6,
            "startstation": "Steyr Bahnhof",
            "endstation": "St.Valentin Bahnhof",
            "stationplan": [
                {
                    "start": "Steyr Bahnhof",
                    "end": "Steyr Munichholz Bahnhof",
                    "nutzungsentgeld": 5,
                    "duration": 15
                },
                {
                    "start": "Steyr Munichholz Bahnhof",
                    "end": "Ramingdorf",
                    "nutzungsentgeld": 18,
                    "duration": 10
                },
                {
                    "start": "Ramingdorf",
                    "end": "Enns",
                    "nutzungsentgeld": 2,
                    "duration": 20
                },
                {
                    "start": "Enns",
                    "end": "St.Valentin Bahnhof",
                    "nutzungsentgeld": 1.75,
                    "duration": 15
                }
            ],
            "crew": [
                {
                    "personalid": 1,
                    "name": "Tom Baum"
                },
                {
                    "personalid": 2,
                    "name": "Andrea Baum"
                }
            ],
            "train": {
                "trainid": 1,
                "train_name": "WB100"
            }
        },
        {
            "date": "01.01.2024",
            "time": "09:00",
            "priceadjust_percent": 10,
            "railwayscheduleid": 1,
            "routeid": 6,
            "startstation": "Steyr Bahnhof",
            "endstation": "St.Valentin Bahnhof",
            "stationplan": [
                {
                    "start": "Steyr Bahnhof",
                    "end": "Steyr Munichholz Bahnhof",
                    "nutzungsentgeld": 5,
                    "duration": 15
                },
                {
                    "start": "Steyr Munichholz Bahnhof",
                    "end": "Ramingdorf",
                    "nutzungsentgeld": 18,
                    "duration": 10
                },
                {
                    "start": "Ramingdorf",
                    "end": "Enns",
                    "nutzungsentgeld": 2,
                    "duration": 20
                },
                {
                    "start": "Enns",
                    "end": "St.Valentin Bahnhof",
                    "nutzungsentgeld": 1.75,
                    "duration": 15
                }
            ],
            "crew": [
                {
                    "personalid": 1,
                    "name": "Tom Baum"
                },
                {
                    "personalid": 2,
                    "name": "Andrea Baum"
                }
            ],
            "train": {
                "trainid": 1,
                "train_name": "WB100"
            }
        },
        {
            "date": "01.01.2024",
            "time": "10:00",
            "priceadjust_percent": 10,
            "railwayscheduleid": 1,
            "routeid": 6,
            "startstation": "Steyr Bahnhof",
            "endstation": "St.Valentin Bahnhof",
            "stationplan": [
                {
                    "start": "Steyr Bahnhof",
                    "end": "Steyr Munichholz Bahnhof",
                    "nutzungsentgeld": 5,
                    "duration": 15
                },
                {
                    "start": "Steyr Munichholz Bahnhof",
                    "end": "Ramingdorf",
                    "nutzungsentgeld": 18,
                    "duration": 10
                },
                {
                    "start": "Ramingdorf",
                    "end": "Enns",
                    "nutzungsentgeld": 2,
                    "duration": 20
                },
                {
                    "start": "Enns",
                    "end": "St.Valentin Bahnhof",
                    "nutzungsentgeld": 1.75,
                    "duration": 15
                }
            ],
            "crew": [
                {
                    "personalid": 1,
                    "name": "Tom Baum"
                },
                {
                    "personalid": 2,
                    "name": "Andrea Baum"
                }
            ],
            "train": {
                "trainid": 1,
                "train_name": "WB100"
            }
        },
        {
            "date": "01.06.2024",
            "time": "17:00",
            "priceadjust_percent": 10,
            "railwayscheduleid": 1,
            "routeid": 6,
            "startstation": "Steyr Bahnhof",
            "endstation": "St.Valentin Bahnhof",
            "stationplan": [
                {
                    "start": "Steyr Bahnhof",
                    "end": "Steyr Munichholz Bahnhof",
                    "nutzungsentgeld": 5,
                    "duration": 15
                },
                {
                    "start": "Steyr Munichholz Bahnhof",
                    "end": "Ramingdorf",
                    "nutzungsentgeld": 18,
                    "duration": 10
                },
                {
                    "start": "Ramingdorf",
                    "end": "Enns",
                    "nutzungsentgeld": 2,
                    "duration": 20
                },
                {
                    "start": "Enns",
                    "end": "St.Valentin Bahnhof",
                    "nutzungsentgeld": 1.75,
                    "duration": 15
                }
            ],
            "crew": [
                {
                    "personalid": 1,
                    "name": "Tom Baum"
                },
                {
                    "personalid": 2,
                    "name": "Andrea Baum"
                }
            ],
            "train": {
                "trainid": 1,
                "train_name": "WB100"
            }
        },
        {
            "date": "01.01.2024",
            "time": "11:00",
            "priceadjust_percent": 10,
            "railwayscheduleid": 1,
            "routeid": 9,
            "startstation": "Salzburg",
            "endstation": "Wien",
            "stationplan": [
                {
                    "start": "Salzburg",
                    "end": "Wels",
                    "nutzungsentgeld": 24,
                    "duration": 55
                },
                {
                    "start": "Wels",
                    "end": "Enns",
                    "nutzungsentgeld": 10,
                    "duration": 25
                },
                {
                    "start": "Enns",
                    "end": "Amstetten",
                    "nutzungsentgeld": 4,
                    "duration": 15
                },
                {
                    "start": "Amstetten",
                    "end": "Wien",
                    "nutzungsentgeld": 15,
                    "duration": 45
                }
            ],
            "crew": [
                {
                    "personalid": 1,
                    "name": "Tom Baum"
                },
                {
                    "personalid": 2,
                    "name": "Andrea Baum"
                }
            ],
            "train": {
                "trainid": 1,
                "train_name": "WB100"
            }
        },
        {
            "date": "01.01.2024",
            "time": "12:00",
            "priceadjust_percent": 15,
            "railwayscheduleid": 2,
            "routeid": 2,
            "startstation": "Linz HBF",
            "endstation": "Graz HBF",
            "stationplan": [
                {
                    "start": "Linz HBF",
                    "end": "Steyr Bahnhof",
                    "nutzungsentgeld": 8,
                    "duration": 40
                },
                {
                    "start": "Steyr Bahnhof",
                    "end": "Kapfenberg",
                    "nutzungsentgeld": 12,
                    "duration": 60
                },
                {
                    "start": "Kapfenberg",
                    "end": "Graz HBF",
                    "nutzungsentgeld": 10,
                    "duration": 50
                }
            ],
            "crew": [
                {
                    "personalid": 3,
                    "name": "Michaela Klein"
                },
                {
                    "personalid": 4,
                    "name": "Stephan Groß"
                }
            ],
            "train": {
                "trainid": 2,
                "train_name": "RB202"
            }
        },
        {
            "date": "01.01.2024",
            "time": "13:30",
            "priceadjust_percent": 10,
            "railwayscheduleid": 3,
            "routeid": 3,
            "startstation": "St.Valentin Bahnhof",
            "endstation": "Linz",
            "stationplan": [
                {
                    "start": "St.Valentin Bahnhof",
                    "end": "Enns",
                    "nutzungsentgeld": 2.5,
                    "duration": 15
                },
                {
                    "start": "Enns",
                    "end": "Linz",
                    "nutzungsentgeld": 5,
                    "duration": 25
                }
            ],
            "crew": [
                {
                    "personalid": 5,
                    "name": "Lara Müller"
                },
                {
                    "personalid": 6,
                    "name": "Jan Hofer"
                }
            ],
            "train": {
                "trainid": 3,
                "train_name": "IC300"
            }
        },
        {
            "date": "01.06.2024",
            "time": "13:30",
            "priceadjust_percent": 10,
            "railwayscheduleid": 3,
            "routeid": 1,
            "startstation": "WienHBF",
            "endstation": "Salzburg HBF",
            "stationplan": [
                {
                    "start": "WienHBF",
                    "end": "Wels HBF",
                    "nutzungsentgeld": 22.5,
                    "duration": 65
                },
                {
                    "start": "Wels HBF",
                    "end": "Salzburg HBF",
                    "nutzungsentgeld": 19,
                    "duration": 55
                }
            ],
            "crew": [
                {
                    "personalid": 5,
                    "name": "Lara Müller"
                },
                {
                    "personalid": 6,
                    "name": "Jan Hofer"
                }
            ],
            "train": {
                "trainid": 3,
                "train_name": "IC300"
            }
        },
        {
            "date": "01.06.2026",
            "time": "13:30",
            "priceadjust_percent": 10,
            "railwayscheduleid": 3,
            "routeid": 1,
            "startstation": "WienHBF",
            "endstation": "Salzburg HBF",
            "stationplan": [
                {
                    "start": "WienHBF",
                    "end": "Wels HBF",
                    "nutzungsentgeld": 22.5,
                    "duration": 65
                },
                {
                    "start": "Wels HBF",
                    "end": "Salzburg HBF",
                    "nutzungsentgeld": 19,
                    "duration": 55
                }
            ],
            "crew": [
                {
                    "personalid": 5,
                    "name": "Lara Müller"
                },
                {
                    "personalid": 6,
                    "name": "Jan Hofer"
                }
            ],
            "train": {
                "trainid": 3,
                "train_name": "IC300"
            }
        }
    ]
    return jsonify(data)
