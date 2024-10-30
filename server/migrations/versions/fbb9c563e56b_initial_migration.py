"""Initial Migration

Revision ID: fbb9c563e56b
Revises: 
Create Date: 2024-10-30 19:29:32.879403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbb9c563e56b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock_tickers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(length=10), nullable=False),
    sa.Column('company_name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('symbol')
    )
    op.create_table('stocks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(length=10), nullable=False),
    sa.Column('company_name', sa.String(length=100), nullable=True),
    sa.Column('current_price', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('symbol')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('portfolios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('avg_buy_price', sa.Float(), nullable=False),
    sa.Column('current_value', sa.Float(), nullable=True),
    sa.Column('initial_capital', sa.Float(), nullable=False),
    sa.Column('net_profit_loss', sa.Float(), nullable=True),
    sa.Column('volatility', sa.Float(), nullable=True),
    sa.Column('sharpe_ratio', sa.Float(), nullable=True),
    sa.Column('dividend_yield', sa.Float(), nullable=True),
    sa.Column('sector', sa.String(length=50), nullable=True),
    sa.Column('asset_class', sa.String(length=50), nullable=True),
    sa.Column('trade_turnover', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], name=op.f('fk_portfolios_stock_id_stocks')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_portfolios_user_id_users')),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('trade_type', sa.String(length=10), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price_at_trade', sa.Float(), nullable=False),
    sa.Column('net_profit', sa.Float(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], name=op.f('fk_trades_stock_id_stocks')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_trades_user_id_users')),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trades')
    op.drop_table('portfolios')
    op.drop_table('users')
    op.drop_table('stocks')
    op.drop_table('stock_tickers')
    # ### end Alembic commands ###
