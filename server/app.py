#!/usr/bin/env python3

from flask import Flask, request, jsonify, session, make_response
from flask_restful import Resource, Api
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from functools import wraps
import jwt, requests, os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask_bcrypt import generate_password_hash, check_password_hash
from cachetools import TTLCache
import ipdb

from config import app, db
from models import User, Stock, Portfolio, Trade, StockTicker

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
RAPID_API_KEY = os.getenv("RAPIDAPI_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")
DATABASE_URL = os.getenv("DATABASE_URL")

app.config['JWT_SECRET_KEY'] = SECRET_KEY or 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

api = Api(app)
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

        # Adjust to include 'current_user' explicitly as a keyword argument
        return f(*args, current_user=current_user, **kwargs)
    return decorated

# Helper functions for user authentication and token creation
def create_token(user):
    payload = {'user_id': user.id, 'username': user.username, 'exp': datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm="HS256")
    return token

@app.route('/api/successfulStock', methods=["GET"])
def get_successfulStock():
    threshold = request.args.get('threshold', type=float)
    if threshold is None:
        return make_response({"error": "threshold not present"}), 404
    
    results = (Portfolio.query.options(joinedload(Portfolio.stock))).filter(Portfolio.quantity >= threshold).all()

    stocks_above_threshold = [{
        "stock_id": portfolio.stock_id,
        "symbol": portfolio.stock.symbol,
        "company_name": portfolio.stock.company_name,
        "quantity": portfolio.quantity
     } for portfolio in results]
    
    return jsonify(stocks_above_threshold), 200
               
    

# Signup, login, logout, and register routes
class UserResource(Resource):
    def post(self):
        """Create a new user (signup)"""
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return {"error": "Email already registered"}, 400
        hashed_password = generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            first_name=data['firstName'],
            last_name=data['lastName'],
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return {"token": create_token(new_user)}, 201

    @token_required
    def get(self, current_user):
        """Retrieve current user details"""
        user_data = {
            'id': current_user.id,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'username': current_user.username,
            'email': current_user.email,
        }
        return user_data, 200

    @token_required
    def put(self, current_user):
        """Update current user details"""
        data = request.get_json()
        if 'first_name' in data:
            current_user.first_name = data['first_name']
        if 'last_name' in data:
            current_user.last_name = data['last_name']
        if 'username' in data:
            # Check if the new username is unique
            if User.query.filter_by(username=data['username']).first() and current_user.username != data['username']:
                return {"error": "Username already taken"}, 400
            current_user.username = data['username']
        if 'email' in data:
            # Check if the new email is unique
            if User.query.filter_by(email=data['email']).first() and current_user.email != data['email']:
                return {"error": "Email already in use"}, 400
            current_user.email = data['email']
        if 'password' in data:
            current_user.password_hash = generate_password_hash(data['password']).decode('utf-8')
        
        try:
            db.session.commit()
            return {"message": "User updated successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @token_required
    def delete(self, current_user):
        """Delete current user account"""
        try:
            db.session.delete(current_user)
            db.session.commit()
            return {"message": "User account deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password_hash, data['password']):
            return {"token": create_token(user)}, 200
        return {'message': 'Invalid credentials'}, 401

class LogoutResource(Resource):
    def post(self):
        session.clear()
        return {'message': 'Logged out successfully'}, 200

# Stock-related routes
class StockResource(Resource):
    @token_required
    def get(self, current_user):
        stocks = Stock.query.all()
        result = [{'id': stock.id, 'symbol': stock.symbol, 'company_name': stock.company_name,
                   'current_price': stock.current_price} for stock in stocks]
        return result, 200

class HistoricalDataResource(Resource):
    @token_required
    def get(self, current_user, symbol):
        try:
            response = requests.get(
                f'https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v3/get-historical-data',
                headers={'x-rapidapi-key': RAPID_API_KEY, 'x-rapidapi-host': RAPID_API_HOST},
                params={'symbol': symbol, 'region': 'US'}
            )
            data = response.json().get('prices', [])
            filtered_data = [item for item in data if item.get('close') is not None]
            return filtered_data, 200
        except Exception as e:
            return {'error': str(e)}, 500

class UpdateStockPriceResource(Resource):
    @token_required
    def post(self, current_user):
        data = request.json
        symbol, latest_price = data.get("symbol"), data.get("latest_price")
        if not symbol or latest_price is None:
            return {"error": "Symbol and latest price are required"}, 400
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            return {"error": "Stock not found"}, 404
        stock.current_price = latest_price
        for portfolio in Portfolio.query.filter_by(stock_id=stock.id).all():
            portfolio.current_value = portfolio.quantity * latest_price
            portfolio.net_profit_loss = (latest_price - portfolio.avg_buy_price) * portfolio.quantity
        db.session.commit()
        return {"message": f"{symbol} price updated successfully"}, 200

# Portfolio-related routes
class PortfolioResource(Resource):
    @token_required
    def get(self, current_user):
        portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
        result = [{'stock_symbol': entry.stock.symbol, 'quantity': entry.quantity,
                   'avg_buy_price': entry.avg_buy_price, 'current_price': entry.stock.current_price,
                   'current_value': entry.current_value, 'net_profit_loss': entry.net_profit_loss} for entry in portfolios]
        return result, 200

# Trade-related routes
class TradeResource(Resource):
    @token_required
    def post(self, current_user):
        data = request.get_json()
        stock = Stock.query.get(data['stock_id'])
        
        if not stock:
            return {"error": "Stock not found."}, 404

        trade_type = data['trade_type']
        quantity = data['quantity']
        price_at_trade = stock.current_price
        net_profit = 0.0

        # Get or create the portfolio entry
        portfolio_entry = Portfolio.query.filter_by(user_id=current_user.id, stock_id=stock.id).first()
        
        if trade_type == 'buy':
            # Calculate trade value
            trade_value = quantity * price_at_trade
            if portfolio_entry:
                # Update existing entry
                total_cost = (portfolio_entry.avg_buy_price * portfolio_entry.quantity) + trade_value
                new_quantity = portfolio_entry.quantity + quantity
                portfolio_entry.avg_buy_price = total_cost / new_quantity
                portfolio_entry.quantity = new_quantity
                portfolio_entry.current_value = new_quantity * price_at_trade
            else:
                # Create new portfolio entry
                portfolio_entry = Portfolio(
                    user_id=current_user.id,
                    stock_id=stock.id,
                    quantity=quantity,
                    avg_buy_price=price_at_trade,
                    initial_capital=trade_value,
                    current_value=trade_value,
                    net_profit_loss=0.0
                )
                db.session.add(portfolio_entry)

        elif trade_type == 'sell':
            if not portfolio_entry or portfolio_entry.quantity < quantity:
                return {"error": "Insufficient stock quantity."}, 400
            
            # Calculate net profit
            sale_value = quantity * price_at_trade
            buy_cost = quantity * portfolio_entry.avg_buy_price
            net_profit = sale_value - buy_cost
            
            # Update portfolio entry
            portfolio_entry.quantity -= quantity
            portfolio_entry.net_profit_loss += net_profit
            if portfolio_entry.quantity == 0:
                db.session.delete(portfolio_entry)
            else:
                portfolio_entry.current_value = portfolio_entry.quantity * price_at_trade

        # Log the trade
        trade = Trade(
            user_id=current_user.id,
            stock_id=stock.id,
            trade_type=trade_type,
            quantity=quantity,
            price_at_trade=price_at_trade,
            net_profit=net_profit if trade_type == 'sell' else 0.0,
            timestamp=datetime.utcnow()
        )

        db.session.add(trade)
        
        try:
            db.session.commit()
            return {"message": "Trade executed successfully"}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": str(e)}, 500


    @token_required
    def get(self, current_user):
        trades = Trade.query.filter_by(user_id=current_user.id).all()
        result = [
            {
                'stock_symbol': trade.stock.symbol if trade.stock else 'N/A',
                'trade_type': trade.trade_type,
                'quantity': trade.quantity,
                'price_at_trade': trade.price_at_trade,
                'net_profit': trade.net_profit,
                'timestamp': trade.timestamp.isoformat()
            }
            for trade in trades
        ]
        return jsonify(result)

# Register resources
api.add_resource(UserResource, '/user')
api.add_resource(LoginResource, '/login')
api.add_resource(LogoutResource, '/logout')
api.add_resource(StockResource, '/api/stocks')
api.add_resource(HistoricalDataResource, '/api/historical/<string:symbol>')
api.add_resource(UpdateStockPriceResource, '/api/update_stock_price')
api.add_resource(PortfolioResource, '/api/portfolio')
api.add_resource(TradeResource, '/api/trades')

if __name__ == '__main__':
    app.run(port=int(os.getenv("PORT", 10000)), debug=True)
