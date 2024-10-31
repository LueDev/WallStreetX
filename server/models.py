from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from config import db

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    trades = db.relationship('Trade', back_populates='user', lazy='dynamic')
    portfolios = db.relationship('Portfolio', back_populates='user', lazy='dynamic')

class StockTicker(db.Model, SerializerMixin):
    __tablename__ = 'stock_tickers'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    company_name = db.Column(db.String(100))

class Stock(db.Model, SerializerMixin):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    company_name = db.Column(db.String(100))
    current_price = db.Column(db.Float)

    portfolios = db.relationship(
        'Portfolio', back_populates='stock', lazy='dynamic', overlaps="portfolio_stock"
    )
    trades = db.relationship(
        'Trade', back_populates='stock', lazy='dynamic', overlaps="traded_stock"
    )

class Portfolio(db.Model, SerializerMixin):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    avg_buy_price = db.Column(db.Float, nullable=False, default=0.0)
    current_value = db.Column(db.Float, default=0.0)
    initial_capital = db.Column(db.Float, nullable=True)
    net_profit_loss = db.Column(db.Float, default=0.0)
    volatility = db.Column(db.Float, default=0.0)
    sharpe_ratio = db.Column(db.Float, default=0.0)
    dividend_yield = db.Column(db.Float, default=0.0)
    sector = db.Column(db.String(50))
    asset_class = db.Column(db.String(50))
    trade_turnover = db.Column(db.Integer, default=0)

    stock = db.relationship('Stock', back_populates='portfolios', overlaps="portfolio_entries,stock_entry")
    user = db.relationship('User', back_populates='portfolios', overlaps="user_portfolios")

    def update_after_trade(self, trade):
        """Update the portfolio based on a trade."""
        if trade.trade_type == 'buy':
            total_cost = (self.avg_buy_price * self.quantity) + (trade.price_at_trade * trade.quantity)
            self.quantity += trade.quantity
            self.avg_buy_price = total_cost / self.quantity

        elif trade.trade_type == 'sell':
            profit = (trade.price_at_trade - self.avg_buy_price) * trade.quantity
            self.net_profit_loss += profit
            self.quantity -= trade.quantity

            if self.quantity == 0:
                db.session.delete(self)

        self.current_value = self.quantity * self.stock.current_price
        db.session.commit()

    @property
    def calculate_sharpe_ratio(self, risk_free_rate=0.01):
        """Calculate the Sharpe ratio for the portfolio."""
        if self.volatility > 0:
            return (self.net_profit_loss - self.initial_capital) / self.volatility
        return 0.0

class Trade(db.Model, SerializerMixin):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    trade_type = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price_at_trade = db.Column(db.Float, nullable=False)
    net_profit = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    stock = db.relationship('Stock', back_populates='trades', overlaps="stock_trade,trades")
    user = db.relationship('User', back_populates='trades', overlaps="user_trader,user_trades")

    def calculate_net_profit(self, portfolio):
        """Calculate profit or loss for a sell trade."""
        if self.trade_type == 'sell':
            self.net_profit = (self.price_at_trade - portfolio.avg_buy_price) * self.quantity
            db.session.commit()
