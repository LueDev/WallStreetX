from sqlalchemy_serializer import SerializerMixin
from config import db

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    trades = db.relationship('Trade', backref='user')
    portfolio = db.relationship('Portfolio', backref='user')

class Stock(db.Model, SerializerMixin):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(100))
    current_price = db.Column(db.Float)

    portfolio_entries = db.relationship('Portfolio', backref='stock')
    trades = db.relationship('Trade', backref='stock')

class Portfolio(db.Model, SerializerMixin):
    __tablename__ = 'portfolio'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'))
    quantity = db.Column(db.Integer, nullable=False)

class Trade(db.Model, SerializerMixin):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'))
    trade_type = db.Column(db.String(10))
    quantity = db.Column(db.Integer)
    price_at_trade = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)
