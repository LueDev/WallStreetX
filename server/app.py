#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response, session
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
import jwt, requests, os 
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask_bcrypt import generate_password_hash, check_password_hash

from config import app, db, api
from models import User, Stock, Portfolio, Trade

SECRET_KEY = os.getenv("SECRET_KEY")
RAPID_API_KEY = os.getenv("RAPIDAPI_KEY")
RAPID_API_HOST = os.getenv("RAPIDAPI_HOST")

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
        }, app.config['SECRET_KEY'], algorithm="HS256")
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
                quantity=data['quantity']
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
    app.run(port=5555, debug=True)
