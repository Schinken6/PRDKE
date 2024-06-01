from datetime import datetime, timedelta
from flask import request, render_template, flash, redirect, url_for, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm, BuyTicketForm, NewPromotionForm
from flask_login import current_user, login_user
import sqlalchemy as sa
from app.models import User, Ticket, Promotion
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
        flash(
            'Die Aktion kann nicht gelöscht werden, da sie bereits auf %d gekaufte Tickets angewandt wurde!' % ticket_count,
            'error')
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

@app.route('/search_tickets', methods=['POST'])
def search_tickets():
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
        return render_template('show_tickets.html', tickets=filtered_schedules)
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
                                            'arrival_time': after['arrival_time'],
                                            'price': f"{float(before['price'].strip('€')) + float(after['price'].strip('€'))}€"
                                        }
                                        valid_tickets.append(combined_ticket) # zu Liste hinzufügen
                                        print(f"Gefundene gültige Verbindung: {combined_ticket}")

                            if valid_tickets: # wenn Tickets vorhanden sind, auf nächster Seite anzeigen
                                return render_template('show_tickets.html', tickets=valid_tickets)
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
                departure_time = current_time.strftime("%H:%M")

            current_time += timedelta(minutes=segment['duration']) # aktualisierung der Zeit für aktuelle Station

            if processing_route: # Wenn Startbahnhof gefunden wurde
                if segment['end'] == form_end_station: # Wenn Endbahnhof gefunden wurde
                    arrival_time = current_time.strftime("%H:%M")
                    total_price += segment['nutzungsentgeld']
                    break
                total_price += segment['nutzungsentgeld']

        if processing_route:
            valid_route_found = True # für Return
            filtered_schedules.append({
                'train_name': schedule['train']['train_name'],
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'price': str(total_price) + "€"
            })

    if valid_route_found: # wenn mindestens eine Kombination von Start- und Endbahnhof gefunden wurde
        return filtered_schedules
    else: # Rückgabe von Fehlermeldung (keine Liste )
        return jsonify({'error': 'Die Fahrt ist in dieser Konstellation nicht möglich.'}), 400


@app.route('/purchase_ticket', methods=['POST']) # funktioniert noch nicht
def purchase_ticket():
    ticket_id = request.form['ticket_id']
    return render_template('ticket_purchase.html', ticket_id=ticket_id)


@app.route('/api/railwayschedules', methods=['GET']) # temporäre eigene API, bis die API von Marko fertig ist
def api_railwayschedules():
    data = [
        {
            "date": "01.01.2024",
            "time": "08:00",
            "priceadjust_percent": 10,
            "railwayscheduleid": 1,
            "routeid": 1,
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
            "routeid": 1,
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
            "routeid": 1,
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
            "routeid": 1,
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
            "startstation": "Linz",
            "endstation": "Graz",
            "stationplan": [
                {
                    "start": "Linz",
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
                    "end": "Graz",
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
        }
    ]
    return jsonify(data)
