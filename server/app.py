#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response, session
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
import jwt, requests, os 
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask_bcrypt import generate_password_hash, check_password_hash
from cachetools import TTLCache

from config import app, db, api
from models import User, Stock, Portfolio, Trade, StockTicker

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
RAPID_API_KEY = os.getenv("RAPIDAPI_KEY")
RAPID_API_HOST = os.getenv("RAPIDAPI_HOST")
DATABASE_URL=os.getenv("DATABASE_URL")

app.config['JWT_SECRET_KEY'] = SECRET_KEY or 'your_default_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# Cache for stock prices with TTL of 300 seconds (5 minutes)
price_cache = TTLCache(maxsize=10000, ttl=300)

# Token-required decorator for protected routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

def create_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm="HS256")
    return token

def fetch_stock_price(symbol):
    """Fetch stock price with caching."""
    if symbol in price_cache:
        print(f"Returning cached price for {symbol}")
        return price_cache[symbol]  # Return cached price

    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v3/get-quote"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST
    }
    params = {"symbol": symbol, "region": "US"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        price = data['quoteResponse']['result'][0].get('regularMarketPrice')
        if price:
            price_cache[symbol] = price  # Cache the price
            return price
        else:
            raise ValueError(f"No price found for {symbol}")
    except Exception as e:
        print(f"Error fetching price for {symbol}: {str(e)}")
        return None

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json

    # Check if email already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Hash the password
    hashed_password = generate_password_hash(data['password']).decode('utf-8')

    # Create new user
    new_user = User(
        first_name=data['firstName'],
        last_name=data['lastName'],
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password
    )

    # Add and commit the new user
    db.session.add(new_user)
    db.session.commit()

    # Generate token
    token = create_token(new_user)
    return jsonify(token=token)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password']).decode('utf-8')
    try:
        user = User(username=data['username'], password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {'error': str(e)}, 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return {'message': 'Invalid credentials'}, 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear session on logout
    return {'message': 'Logged out successfully'}, 200

@app.route('/api/historical/<string:symbol>', methods=['GET'])
@token_required
def get_historical_data(current_user, symbol):
    try:
        response = requests.get(
            f'https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v3/get-historical-data',
            headers={
                'x-rapidapi-key': RAPID_API_KEY,
                'x-rapidapi-host': RAPID_API_HOST,
            },
            params={'symbol': symbol, 'region': 'US'}
        )
        data = response.json()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/portfolio', methods=['GET'])
@token_required
def get_portfolio(current_user):
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    result = [
        {
            'stock_symbol': entry.stock.symbol,
            'quantity': entry.quantity,
            'avg_buy_price': entry.avg_buy_price,
            'current_price': entry.stock.current_price,
            'current_value': entry.current_value,
            'net_profit_loss': entry.net_profit_loss,
            'sharpe_ratio': entry.sharpe_ratio,
            'dividend_yield': entry.dividend_yield
        }
        for entry in portfolios
    ]
    return jsonify(result), 200



@app.route('/api/trade-history', methods=['GET'])
@token_required
def get_trade_history(current_user):
    trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.timestamp.desc()).all()
    result = [
        {
            'stock_symbol': trade.stock.symbol,
            'trade_type': trade.trade_type,
            'quantity': trade.quantity,
            'price_at_trade': trade.price_at_trade,
            'net_profit': trade.net_profit,
            'timestamp': trade.timestamp
        }
        for trade in trades
    ]
    return jsonify(result), 200

@app.route('/api/trades', methods=['POST'])
@token_required
def execute_trade(current_user):
    data = request.get_json()
    stock = Stock.query.get(data['stock_id'])
    trade_type = data['trade_type']
    quantity = int(data['quantity'])

    if not stock:
        return jsonify({"error": "Stock not found."}), 404

    portfolio_entry = Portfolio.query.filter_by(
        user_id=current_user.id, stock_id=stock.id
    ).first()

    if trade_type == 'sell':
        if not portfolio_entry or portfolio_entry.quantity < quantity:
            return jsonify({"error": "Insufficient stock quantity."}), 400

        # Calculate net profit from the sale
        sale_value = quantity * stock.current_price
        buy_cost = quantity * portfolio_entry.avg_buy_price
        net_profit = sale_value - buy_cost

        # Update portfolio and remove entry if quantity is zero
        portfolio_entry.quantity -= quantity
        portfolio_entry.net_profit_loss += net_profit

        if portfolio_entry.quantity == 0:
            db.session.delete(portfolio_entry)

    elif trade_type == 'buy':
        trade_value = quantity * stock.current_price

        if portfolio_entry:
            # Update existing entry
            total_cost = (portfolio_entry.avg_buy_price * portfolio_entry.quantity) + trade_value
            new_quantity = portfolio_entry.quantity + quantity
            portfolio_entry.avg_buy_price = total_cost / new_quantity
            portfolio_entry.quantity = new_quantity
        else:
            # Create new portfolio entry
            new_entry = Portfolio(
                user_id=current_user.id,
                stock_id=stock.id,
                quantity=quantity,
                avg_buy_price=stock.current_price,
                initial_capital=trade_value
            )
            db.session.add(new_entry)

    # Create new trade log
    new_trade = Trade(
        user_id=current_user.id,
        stock_id=stock.id,
        trade_type=trade_type,
        quantity=quantity,
        price_at_trade=stock.current_price,
        net_profit=net_profit if trade_type == 'sell' else 0.0
    )
    db.session.add(new_trade)

    try:
        db.session.commit()
        return jsonify({"message": "Trade executed successfully."}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/tickers', methods=['GET'])
@token_required
def get_tickers(current_user):
    tickers = StockTicker.query.all()
    result = [{"symbol": ticker.symbol, "company_name": ticker.company_name} for ticker in tickers]
    return jsonify(result), 200

class StockList(Resource):
    @token_required
    def get(self, current_user):
        try:
            stocks = Stock.query.all()
            result = [{'id': stock.id, 'symbol': stock.symbol, 'company_name': stock.company_name,
                       'current_price': stock.current_price} for stock in stocks]
            return jsonify(result)
        except SQLAlchemyError as e:
            return {'error': str(e)}, 500

class PortfolioResource(Resource):
    @token_required
    def get(self, current_user):
        portfolio = Portfolio.query.filter_by(user_id=current_user.id).all()
        result = [{'stock_id': entry.stock_id, 'quantity': entry.quantity} for entry in portfolio]
        return jsonify(result)

    @token_required
    def post(self, current_user):
        data = request.get_json()
        try:
            portfolio_entry = Portfolio(
                user_id=current_user.id,
                stock_id=data['stock_id'],
                quantity=data['quantity'],
                avg_buy_price=data['avg_buy_price'],
                current_value=data['current_value'],
            )
            db.session.add(portfolio_entry)
            db.session.commit()
            return {'message': 'Added to portfolio'}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 400

class TradeResource(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json()
        stock = Stock.query.get(data['stock_id'])
        if data['trade_type'] == 'buy':
            # Implement logic to handle purchases, checking funds, etc.
            pass

        try:
            trade = Trade(
                user_id=current_user.id,
                stock_id=data['stock_id'],
                trade_type=data['trade_type'],
                quantity=data['quantity'],
                price_at_trade=stock.current_price,
                timestamp=datetime.utcnow()
            )
            db.session.add(trade)
            db.session.commit()
            return {'message': 'Trade executed successfully'}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    @token_required
    def get(self, current_user):
        trades = Trade.query.filter_by(user_id=current_user.id).all()
        result = [
            {
                'stock_id': trade.stock_id,
                'trade_type': trade.trade_type,
                'quantity': trade.quantity,
                'price_at_trade': trade.price_at_trade,
                'timestamp': trade.timestamp
            } for trade in trades
        ]
        return jsonify(result)
    
class HistoricalDataResource(Resource):
    @token_required
    def get(self, current_user, symbol):
        try:
            # Fetch historical data from RapidAPI
            response = requests.get(
                'https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v3/get-historical-data',
                params={'symbol': symbol, 'region': 'US'},
                headers={
                    'x-rapidapi-key': RAPID_API_KEY,
                    'x-rapidapi-host': RAPID_API_HOST
                }
            )

            data = response.json().get('prices', [])
            filtered_data = [item for item in data if item.get('close') is not None]

            return jsonify(filtered_data), 200
        except Exception as e:
            return {'error': str(e)}, 500
        
# Register API Resources
api.add_resource(StockList, '/api/stocks')
api.add_resource(PortfolioResource, '/api/portfolio')
api.add_resource(TradeResource, '/api/trades')
api.add_resource(HistoricalDataResource, '/api/historical/<string:symbol>')

if __name__ == '__main__':
    app.run(port=int(os.getenv("PORT", 10000)), debug=True)
