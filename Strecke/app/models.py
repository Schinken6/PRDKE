from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    street = db.Column(db.String(140))
    no = db.Column(db.Integer)
    zipcode = db.Column(db.Integer)
    city = db.Column(db.String(140))
    country = db.Column(db.String(140))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    isAdmin = db.Column(db.Boolean, default=False)

    address_id = db.Column(db.Integer, db.ForeignKey('address.id', name='fk_user_address_id'))
    address = db.relationship("Address")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(140))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id', name='fk_station_address_id'))
    address = db.relationship("Address")
    xcoord = db.Column(db.String(140))
    ycoord = db.Column(db.String(140))


class Segment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    startStation = db.Column(db.Integer, db.ForeignKey('station.id', name='fk_segment_start'))
    endStation = db.Column(db.Integer, db.ForeignKey('station.id', name='fk_segment_end'))
    trackWidth = db.Column(db.Integer)
    length = db.Column(db.Double)
    maxSpeed = db.Column(db.Integer)
    price = db.Column(db.Double)
    warnings = db.relationship("Warning", back_populates="segment")


class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(140))
    description = db.Column(db.String(1500))
    validFrom = db.Column(db.DateTime)
    validTo = db.Column(db.DateTime)
    segment = db.Column(db.Integer, db.ForeignKey('segment.id', name='fk_warning_segment_id'))


routesegments = db.Table('routesegments', db.metadata,
                         db.Column('id', db.Integer, primary_key=True, autoincrement=True),
                         db.Column('route_id', db.Integer, db.ForeignKey('route.id', name='fk_route_id')),
                         db.Column('segment_id', db.Integer, db.ForeignKey('segment.id', name='fk_route_segment_id')),
                         db.Column('segment_order', db.Integer, nullable=False, default=0)
                         )


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(140))
    startStation = db.Column(db.Integer, db.ForeignKey('station.id', name='fk_route_station_start'))
    endStation = db.Column(db.Integer, db.ForeignKey('station.id', name='fk_route_station_start'))
    sections = db.relationship('Section', secondary=routesegments, backref="route")
    trackWidth = db.Column(db.Integer)
