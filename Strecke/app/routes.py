from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app
from app.forms import LoginForm, TrainstationForm, UserForm, SegmentForm, WarningForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Segment, Warning, Route
from urllib.parse import urlsplit
from app.models import Station, Address, routesegments
from sqlalchemy.orm import aliased
from datetime import datetime



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
    return render_template('index.html', title='Home', posts=posts)


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
    stations = db.session.query(Station, Address).join(Address, Station.address_id == Address.id).all()
    return render_template('trainstation.html', title='Trainstation', stations=stations)


@app.route('/trainsstationNew', methods=['GET', 'POST'])
@login_required
def trainstationNew():
    form = TrainstationForm()
    if form.validate_on_submit():
        address = Address(street=form.street.data, no=form.no.data, zipcode=form.zipcode.data, city=form.city.data,
                          country=form.country.data)
        db.session.add(address)
        db.session.commit()
        trainstation = Station(name=form.name.data, address_id=address.id)
        db.session.add(trainstation)
        db.session.commit()
        flash('Bahnhof angelegt!')
        return redirect(url_for('trainstation'))

    return render_template('trainstationNew.html', title='New Trainstation', form=form)


@app.route('/trainsstationEdit/<station_id>', methods=['GET', 'POST'])
@login_required
def trainstationEdit(station_id):
    station = Station.query.get(station_id)
    address = Address.query.get(station.address_id)
    form = TrainstationForm()
    if form.validate_on_submit():
        address.street = form.street.data
        address.no = form.no.data
        address.zipcode = form.zipcode.data
        address.city = form.city.data
        address.country = form.country.data
        station.name = form.name.data
        db.session.merge(station)
        print(address.city)
        print(form.city.data)
        db.session.commit()  # Commit the changes
        flash('Änderungen gespeichert!')
        return redirect(url_for('trainstation'))
    form = TrainstationForm(obj=station)
    form.street.data = address.street
    form.no.data = address.no
    form.zipcode.data = address.zipcode
    form.city.data = address.city
    form.country.data = address.country
    return render_template('trainstationNew.html', title='Edit Trainstation', form=form)


@app.route('/trainsstationDelete/<station_id>', methods=['GET', 'POST'])
@login_required
def trainstationDelete(station_id):
    deletestation = Station.query.get_or_404(station_id)
    deleteaddress = Address.query.get(deletestation.address_id)
    # if request.method == 'POST':
    db.session.delete(deletestation)
    db.session.delete(deleteaddress)
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


@app.route('/user')
@login_required
def user():
    users = User.query.all()
    return render_template('user.html', title='User', users=users)


@app.route('/userNew', methods=['GET', 'POST'])
@login_required
def userNew():
    form = UserForm()
    if form.validate_on_submit():
        address = Address(street=form.street.data, no=form.no.data, zipcode=form.zipcode.data, city=form.city.data,
                          country=form.country.data)
        db.session.add(address)
        db.session.commit()
        user = User(username=form.username.data, email=form.email.data, isAdmin=form.is_admin.data,
                    address_id=address.id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created!')
        return redirect(url_for('user'))
    return render_template('userNew.html', title='New User', form=form)


@app.route('/userEdit/<user_id>', methods=['GET', 'POST'])
@login_required
def userEdit(user_id):
    user = User.query.get(user_id)
    address = Address.query.get(user.address_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.isAdmin = form.is_admin.data
        address.street = form.street.data
        address.no = form.no.data
        address.zipcode = form.zipcode.data
        address.city = form.city.data
        address.country = form.country.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Changes saved!')
        return redirect(url_for('user'))
    form.street.data = address.street
    form.no.data = address.no
    form.zipcode.data = address.zipcode
    form.city.data = address.city
    form.country.data = address.country
    return render_template('userEdit.html', title='Edit User', form=form)


@app.route('/userDelete/<user_id>', methods=['GET', 'POST'])
@login_required
def userDelete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user'))


@app.route('/segment/new', methods=['GET', 'POST'])
@login_required
def segmentNew():
    form = SegmentForm()
    stations = Station.query.all()
    if form.validate_on_submit():
        segment = Segment(startStation=form.startStation.data, endStation=form.endStation.data,
                          trackWidth=form.trackWidth.data, length=form.length.data, maxSpeed=form.maxSpeed.data,
                          price=form.price.data)
        db.session.add(segment)
        db.session.commit()
        flash('New segment has been created!', 'success')
        return redirect(url_for('segments'))
    else:
        print(form.errors)  # Print form errors
    return render_template('segmentNew.html', title='New Segment', form=form, stations=stations)


@app.route('/segmentEdit/<int:segment_id>', methods=['GET', 'POST'])
@login_required
def segmentEdit(segment_id):
    segment = Segment.query.get(segment_id)
    stations = Station.query.all()
    if segment is None:
        flash('Segment not found.')
        return redirect(url_for('segments'))
    form = SegmentForm(obj=segment)
    form.startStation.choices = [(s.id, s.name) for s in stations]
    form.endStation.choices = [(s.id, s.name) for s in stations]
    if form.validate_on_submit():
        form.populate_obj(segment)
        db.session.commit()
        flash('Segment has been updated!', 'success')
        return redirect(url_for('segments'))
    form.startStation.data = segment.startStation
    form.endStation.data = segment.endStation
    return render_template('segmentNew.html', title='Edit Segment', form=form, stations=stations)


@app.route('/segment/<int:segment_id>/delete', methods=['POST'])
@login_required
def segmentDelete(segment_id):
    segment = Segment.query.get_or_404(segment_id)
    db.session.delete(segment)
    db.session.commit()
    flash('Segment has been deleted!', 'success')
    return redirect(url_for('segments'))


@app.route('/segments')
@login_required
def segments():
    StartStation = aliased(Station)
    EndStation = aliased(Station)

    segments = db.session.query(
        Segment,
        StartStation.name.label('start_station_name'),
        EndStation.name.label('end_station_name')
    ).join(
        StartStation, Segment.startStation == StartStation.id
    ).join(
        EndStation, Segment.endStation == EndStation.id
    ).all()

    return render_template('segment.html', title='Segments', segments=segments)




@app.route('/warnings', methods=['GET'])
@login_required
def warnings():
    warnings = Warning.query.all()
    return render_template('warnings.html', title='Warnings Overview', warnings=warnings)







@app.route('/warningNew', methods=['GET', 'POST'])
@login_required
def warningNew():
    form = WarningForm()
    segments = Segment.query.order_by('startStation').all()
    form.segment.choices = [(s.id, f'{Station.query.get(s.startStation).name} - {Station.query.get(s.endStation).name}') for s in segments]
    if form.validate_on_submit():
        validFrom = datetime.strptime(request.form['validFrom'], '%Y-%m-%d').date()
        validTo = datetime.strptime(request.form['validTo'], '%Y-%m-%d').date()
        warning = Warning(name=form.name.data, description=form.description.data, validFrom=validFrom,
                          validTo=validTo, segment=form.segment.data)
        db.session.add(warning)
        db.session.commit()
        flash('New warning has been created!', 'success')
        return redirect(url_for('warnings'))
    else:
        print(form.errors)  # Print form errors
    return render_template('warningNew.html', form=form)


@app.route('/warningDelete/<int:warning_id>', methods=['POST'])
@login_required
def warningDelete(warning_id):
    warning = Warning.query.get_or_404(warning_id)
    db.session.delete(warning)
    db.session.commit()
    flash('Warning has been deleted!', 'success')
    return redirect(url_for('warnings'))


#############################API#############################

@app.route('/Strecke/<int:route_id>', methods=['GET'])
def get_route(route_id):
    route = Route.query.get(route_id)
    if route is None:
        return jsonify({'error': 'Route not found'}), 404

    # Aliased for multiple join on the same table (Station)
    StartStation = aliased(Station)
    EndStation = aliased(Station)

    # Get the start and end stations
    start_station = StartStation.query.get(route.startStation)
    end_station = EndStation.query.get(route.endStation)

    # Get the segments of the route
    segments = Segment.query.filter(Segment.route.any(id=route.id)).all()

    segments_list = []
    for segment in segments:
        start_station_segment = StartStation.query.get(segment.startStation)
        end_station_segment = EndStation.query.get(segment.endStation)
        segment_data = {
            'id': segment.id,
            'start': start_station_segment.name if start_station_segment else None,
            'end': end_station_segment.name if end_station_segment else None,
            'laenge': segment.length,
            'maxGeschwindigkeit': segment.maxSpeed,
            'nutzungsentgeld': segment.price
        }
        segments_list.append(segment_data)

    route_data = {
        'id': route.id,
        'name': route.name,
        'startbahnhof': start_station.name if start_station else None,
        'endbahnhof': end_station.name if end_station else None,
        'spurbreite': route.trackWidth,
        'abschnitte': segments_list
    }

    return jsonify(route_data)


@app.route('/Strecken', methods=['GET'])
def get_routes():
    # Aliased for multiple join on the same table (Station)
    StartStation = aliased(Station)
    EndStation = aliased(Station)

    routes = Route.query.all()
    routes_list = []

    for route in routes:
        # Get the start and end stations
        start_station = StartStation.query.get(route.startStation)
        end_station = EndStation.query.get(route.endStation)

        # Get the segments of the route
        segments = Segment.query.filter(Segment.route.any(id=route.id)).all()

        segments_list = []
        for segment in segments:
            start_station_segment = StartStation.query.get(segment.startStation)
            end_station_segment = EndStation.query.get(segment.endStation)
            segment_data = {
                'id': segment.id,
                'start': start_station_segment.name if start_station_segment else None,
                'end': end_station_segment.name if end_station_segment else None,
                'laenge': segment.length,
                'maxGeschwindigkeit': segment.maxSpeed,
                'nutzungsentgeld': segment.price
            }
            segments_list.append(segment_data)

        route_data = {
            'id': route.id,
            'name': route.name,
            'startbahnhof': start_station.name if start_station else None,
            'endbahnhof': end_station.name if end_station else None,
            'spurbreite': route.trackWidth,
            'abschnitte': segments_list
        }

        routes_list.append(route_data)

    return jsonify(routes_list)


@app.route('/Strecke/<start_station>/<end_station>', methods=['GET'])
def get_route_by_station(start_station, end_station):
    # Aliased for multiple join on the same table (Station)
    StartStation = aliased(Station)
    EndStation = aliased(Station)

    # Get the start and end stations
    start_station = StartStation.query.filter_by(name=start_station).first()
    end_station = EndStation.query.filter_by(name=end_station).first()

    if start_station is None or end_station is None:
        return jsonify({'error': 'Start or end station not found'}), 404

    # Get the route
    route = Route.query.filter_by(startStation=start_station.id, endStation=end_station.id).first()

    if route is None:
        return jsonify({'error': 'Route not found'}), 404

    # Get the segments of the route
    segments = Segment.query.filter(Segment.route.any(id=route.id)).all()

    segments_list = []
    for segment in segments:
        start_station_segment = StartStation.query.get(segment.startStation)
        end_station_segment = EndStation.query.get(segment.endStation)
        segment_data = {
            'id': segment.id,
            'start': start_station_segment.name if start_station_segment else None,
            'end': end_station_segment.name if end_station_segment else None,
            'laenge': segment.length,
            'maxGeschwindigkeit': segment.maxSpeed,
            'nutzungsentgeld': segment.price
        }
        segments_list.append(segment_data)

    route_data = {
        'id': route.id,
        'name': route.name,
        'startbahnhof': start_station.name if start_station else None,
        'endbahnhof': end_station.name if end_station else None,
        'spurbreite': route.trackWidth,
        'abschnitte': segments_list
    }

    return jsonify(route_data)

@app.route('/Strecke/lite', methods=['GET'])
def get_lite_routes():
    # Aliased for multiple join on the same table (Station)
    StartStation = aliased(Station)
    EndStation = aliased(Station)

    routes = Route.query.all()
    routes_list = []

    for route in routes:
        # Get the start and end stations
        start_station = StartStation.query.get(route.startStation)
        end_station = EndStation.query.get(route.endStation)

        route_data = {
            'id': route.id,
            'name': route.name,
            'startbahnhof': start_station.name if start_station else None,
            'endbahnhof': end_station.name if end_station else None,
            'spurbreite': route.trackWidth,
        }

        routes_list.append(route_data)

    return jsonify(routes_list)


@app.route('/Abschnitt/<start_station>/<end_station>', methods=['GET'])
def get_segment(start_station, end_station):
    # Aliased for multiple join on the same table (Station)
    StartStation = aliased(Station)
    EndStation = aliased(Station)

    # Get the start and end stations
    start_station = StartStation.query.filter_by(name=start_station).first()
    end_station = EndStation.query.filter_by(name=end_station).first()

    if start_station is None or end_station is None:
        return jsonify({'error': 'Start or end station not found'}), 404

    # Get the segment
    segment = Segment.query.filter_by(startStation=start_station.id, endStation=end_station.id).first()

    if segment is None:
        return jsonify({'error': 'Segment not found'}), 404

    segment_data = {
        'id': segment.id,
        'start': start_station.name if start_station else None,
        'end': end_station.name if end_station else None,
        'laenge': segment.length,
        'maxGeschwindigkeit': segment.maxSpeed,
        'nutzungsentgeld': segment.price
    }

    return jsonify(segment_data)


@app.route('/Warnung/all', methods=['GET'])
def get_warnings():
    try:
        warnings = Warning.query.all()
    except TypeError:
        warnings = []

    warnings_list = []

    for warning in warnings:
        warning_data = {
            'name': warning.name,
            'beschreibung': warning.description,
            'abschnitssId': warning.segmentId,
            'startzeitpunkt': warning.validFrom,
            'endzeitpunkt': warning.validTo
        }
        warnings_list.append(warning_data)

    return jsonify(warnings_list)


@app.route('/Strecke/<int:route_id>/Warnungen', methods=['GET'])
def get_route_warnings(route_id):
    # Get the route
    route = Route.query.get(route_id)
    if route is None:
        return jsonify({'error': 'Route not found'}), 404

    # Get the segments of the route
    segments = Segment.query.filter(Segment.route.any(id=route.id)).all()

    warnings_list = []
    for segment in segments:
        # Get the warnings of the segment
        warnings = Warning.query.filter_by(segment=segment.id).all()
        for warning in warnings:
            warning_data = {
                'id': warning.id,
                'name': warning.name,
                'beschreibung': warning.description,
                'startzeitpunkt': warning.validFrom.isoformat() if warning.validFrom else None,
                'endzeitpunkt': warning.validTo.isoformat() if warning.validTo else None,
                'Abschnitt': warning.segment
            }
            warnings_list.append(warning_data)

    return jsonify(warnings_list)


@app.route('/Abschnitt/<int:segment_id>/Warnungen', methods=['GET'])
def get_segment_warnings(segment_id):
    # Get the segment
    segment = Segment.query.get(segment_id)
    if segment is None:
        return jsonify({'error': 'Segment not found'}), 404

    # Get the warnings of the segment
    warnings = Warning.query.filter_by(segment=segment.id).all()

    warnings_list = []
    for warning in warnings:
        warning_data = {
            'id': warning.id,
            'name': warning.name,
            'beschreibung': warning.description,
            'startzeitpunkt': warning.validFrom.isoformat() if warning.validFrom else None,
            'endzeitpunkt': warning.validTo.isoformat() if warning.validTo else None,
            'abschnittId': warning.segment
        }
        warnings_list.append(warning_data)

    return jsonify(warnings_list)

@app.route('/StreckeVonBis/<int:route_id>/<start_station_name>/<end_station_name>/Warnungen', methods=['GET'])
def get_route_warnings_between_stations(route_id, start_station_name, end_station_name):
    # Get the route
    route = Route.query.get(route_id)
    if route is None:
        return jsonify({'error': 'Route not found'}), 404

    # Get the start and end stations
    start_station = Station.query.filter_by(name=start_station_name).first()
    end_station = Station.query.filter_by(name=end_station_name).first()

    if start_station is None or end_station is None:
        return jsonify({'error': 'Start or end station not found'}), 404

    # Get the segments of the route between the start station and the end station
    segments = db.session.query(routesegments).filter_by(route_id=route.id).all()
    start_index = next((index for index, segment in enumerate(segments) if Segment.query.get(segment.segment_id).startStation == start_station.id), None)
    end_index = next((index for index, segment in enumerate(segments) if Segment.query.get(segment.segment_id).endStation == end_station.id), None)

    if start_index is None or end_index is None or start_index > end_index:
        return jsonify({'error': 'Invalid start station or end station'}), 404

    segments_between_stations = segments[start_index:end_index+1]

    warnings_list = []
    for segment in segments_between_stations:
        # Get the warnings of the segment
        warnings = Warning.query.filter_by(segment=segment.segment_id).all()
        for warning in warnings:
            warning_data = {
                'id': warning.id,
                'name': warning.name,
                'beschreibung': warning.description,
                'startzeitpunkt': warning.validFrom.isoformat() if warning.validFrom else None,
                'endzeitpunkt': warning.validTo.isoformat() if warning.validTo else None,
                'abschnittId': warning.segment
            }
            warnings_list.append(warning_data)

    return jsonify(warnings_list)
