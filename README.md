Project Overview: Stock Picker and Trader Dashboard
The idea is to create a Stock Picker and Trader Dashboard app, where users can:

View and track stock prices with interactive TradingView charts.
Manage a portfolio of tracked stocks and store their trades (buy/sell history).
Calculate and visualize financial metrics (e.g., Greeks for options trading).
Authenticate users with sessions and password protection using Flask.
Planning
MVP User Stories:
As a user, I can create an account and log in.
As a user, I can view a list of stocks and track their prices.
As a user, I can add stocks to my portfolio and store my trades.
As a user, I can view financial metrics for a stock (e.g., Greeks, volatility).
As a user, I can update or remove a stock from my portfolio.
As a user, I can log out securely.
Models and Relationships
1. User Model (One-to-Many Relationship)
A user has many trades and a portfolio.
Attributes:

id: Integer (Primary Key)
username: String (Unique)
password_hash: String (Hashed password)
2. Stock Model (Many-to-Many Relationship via Portfolio)
Stocks are tracked by multiple users via a Portfolio table (association model).
Users can submit desired quantity for each stock in the portfolio.
Attributes:

id: Integer (Primary Key)
symbol: String (e.g., 'AAPL')
company_name: String
current_price: Float
3. Portfolio Model (Association Table for User-Stock)
This is a many-to-many relationship between users and stocks.
The portfolio stores user-specific data like the quantity of stocks.
Attributes:

id: Integer (Primary Key)
user_id: Foreign Key (User)
stock_id: Foreign Key (Stock)
quantity: Integer
4. Trade Model (One-to-Many Relationship)
Users can store their buy/sell trades in this model.
Attributes:

id: Integer (Primary Key)
user_id: Foreign Key (User)
stock_id: Foreign Key (Stock)
trade_type: String ('buy' or 'sell')
quantity: Integer
price_at_trade: Float
timestamp: DateTime
Entity Relationship Diagram (ERD)
Here’s a quick view of the relationships:

User –< Trade
User –< Portfolio >– Stock