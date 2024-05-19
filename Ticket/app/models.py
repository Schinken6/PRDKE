from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    firstname: so.Mapped[str] = so.mapped_column(sa.String(256))
    lastname: so.Mapped[str] = so.mapped_column(sa.String(256))
    zip: so.Mapped[int] = so.mapped_column()
    city: so.Mapped[str] = so.mapped_column(sa.String(256))
    street : so.Mapped[str] = so.mapped_column(sa.String(256))
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean)

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')

    tickets: so.WriteOnlyMapped['Ticket'] = so.relationship(
        back_populates='owner')

    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    discount = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    route = db.Column(db.String(64))
    global_promotion = db.Column(db.Boolean, default=False)
    tickets: so.WriteOnlyMapped['Ticket'] = so.relationship(
        back_populates='promotion', passive_deletes=True)

class Ticket(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    owner: so.Mapped[User] = so.relationship(back_populates='tickets')
    price: so.Mapped[float] = so.mapped_column(sa.Float(10))
    departure_date: so.Mapped[Optional[datetime]] = so.mapped_column(sa.Date)
    arrival_date: so.Mapped[Optional[datetime]] = so.mapped_column(sa.Date)
    start_station: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))
    end_station: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))
    status: so.Mapped[Optional[str]] = so.mapped_column(sa.String(15))
    promotion_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey(Promotion.id),
                                               index=True)
    promotion: so.Mapped[Optional[Promotion]] = so.relationship(back_populates='tickets')

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
