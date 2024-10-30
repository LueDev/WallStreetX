"""Create tables with relationships for trades and portfolio

Revision ID: 662811ba24fe
Revises: 
Create Date: 2024-10-30 14:27:29.906745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '662811ba24fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('portfolios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('avg_buy_price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], name=op.f('fk_portfolios_stock_id_stocks')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_portfolios_user_id_users')),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('portfolio')
    with op.batch_alter_table('trades', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('stock_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('trade_type',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('quantity',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('price_at_trade',
               existing_type=sa.FLOAT(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trades', schema=None) as batch_op:
        batch_op.alter_column('price_at_trade',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('quantity',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('trade_type',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('stock_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    op.create_table('portfolio',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('stock_id', sa.INTEGER(), nullable=True),
    sa.Column('quantity', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], name='fk_portfolio_stock_id_stocks'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_portfolio_user_id_users'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('portfolios')
    # ### end Alembic commands ###