from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from config import db

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    trades = db.relationship('Trade', backref='user', lazy=True)  # Use backref here
    portfolio = db.relationship('Portfolio', backref='user', lazy=True)  # Backref for portfolio

class Stock(db.Model, SerializerMixin):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(100))
    current_price = db.Column(db.Float)

    portfolio_entries = db.relationship('Portfolio', backref='stock', lazy=True)  # Backref for holdings
    trades = db.relationship('Trade', backref='stock', lazy=True)  # Backref for trades

class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Correct FK reference
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)  # Correct FK reference
    quantity = db.Column(db.Integer, nullable=False)
    avg_buy_price = db.Column(db.Float, nullable=False)  # Track average buy price

class Trade(db.Model):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Correct FK reference
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)  # Correct FK reference
    trade_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price_at_trade = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
