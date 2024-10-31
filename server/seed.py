#!/usr/bin/env python3

# Standard library imports
from random import choice

# Remote library imports
from faker import Faker
from flask_bcrypt import generate_password_hash

# Local imports
from app import app
from models import db, User, Stock, Portfolio, Trade

fake = Faker()

if __name__ == '__main__':
    with app.app_context():
        print("Starting seed...")

        # Drop and recreate all tables
        db.drop_all()
        db.create_all()

        # Create a static admin user with all required fields
        admin_user = User(
            first_name="Admin",
            last_name="User",
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin").decode("utf-8")
        )
        db.session.add(admin_user)

        # Create additional users with Faker-generated data
        users = [
            User(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=fake.user_name(),
                email=fake.email(),
                password_hash=generate_password_hash(fake.password()).decode("utf-8")
            )
            for _ in range(4)
        ]
        db.session.add_all(users)

        # Create sample stocks
        stocks = [
            Stock(symbol="AAPL", company_name="Apple Inc.", current_price=175.30),
            Stock(symbol="GOOGL", company_name="Alphabet Inc.", current_price=175.46)
        ]
        db.session.add_all(stocks)

        # Create sample portfolio entries
        portfolios = [
            Portfolio(user_id=1, stock_id=1, quantity=10, avg_buy_price=175.30, initial_capital=1753.00),
            Portfolio(user_id=2, stock_id=2, quantity=5, avg_buy_price=175.46, initial_capital=877.30)
        ]
        db.session.add_all(portfolios)

        # Create sample trades
        trades = [
            Trade(
                user_id=1, stock_id=1, trade_type="buy", quantity=10,
                price_at_trade=175.30, timestamp=fake.date_time()
            ),
            Trade(
                user_id=2, stock_id=2, trade_type="sell", quantity=5,
                price_at_trade=175.46, timestamp=fake.date_time()
            )
        ]
        db.session.add_all(trades)

        # Commit all changes to the database
        db.session.commit()
        print("Database seeded successfully!")
