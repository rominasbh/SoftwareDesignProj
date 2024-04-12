from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_complete = db.Column(db.Boolean, default=False)
    profile_info = db.relationship('ProfileInfo', backref='user', uselist=False, cascade="all, delete-orphan")
    fuel_quotes = db.relationship('FuelQuote', backref='user', cascade="all, delete-orphan")

class ProfileInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    full_name = db.Column(db.String(100))
    address1 = db.Column(db.String(200))
    address2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))

class FuelQuote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    gallons_requested = db.Column(db.Float, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    total_amount_due = db.Column(db.Numeric(10, 2))
    price_per_gallon = db.Column(db.Numeric(10, 2))
    delivery_fee = db.Column(db.Numeric(10, 2))
