"""Initial migration for QoraTrader

Revision ID: 001_initial
Revises: 
Create Date: 2025-10-22 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create strategies table
    op.create_table('strategies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('INACTIVE', 'ACTIVE', 'PAUSED', 'STOPPED', 'ERROR', name='strategystatus'), nullable=True),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('code', sa.Text(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create accounts table
    op.create_table('accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('account_type', sa.Enum('SIMULATED', 'LIVE', name='accounttype'), nullable=True),
        sa.Column('status', sa.Enum('NORMAL', 'RESTRICTED', 'RISK_CONTROL', 'FROZEN', name='accountstatus'), nullable=True),
        sa.Column('balance', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('available_balance', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('market_value', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('total_pnl', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('daily_pnl', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'EXTREME', name='risklevel'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create positions table
    op.create_table('positions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=True),
        sa.Column('strategy_id', sa.String(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('direction', sa.Enum('LONG', 'SHORT', name='positiondirection'), nullable=False),
        sa.Column('volume', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('available_volume', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('avg_price', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('unrealized_pnl', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('realized_pnl', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create orders table
    op.create_table('orders',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('strategy_id', sa.String(), nullable=True),
        sa.Column('account_id', sa.String(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('order_type', sa.Enum('MARKET', 'LIMIT', 'STOP', name='ordertype'), nullable=False),
        sa.Column('side', sa.Enum('BUY', 'SELL', name='orderside'), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('status', sa.Enum('PENDING_SUBMISSION', 'SUBMITTED', 'PARTIALLY_FILLED', 'FILLED', 'CANCELLED', 'REJECTED', name='orderstatus'), nullable=True),
        sa.Column('exchange_order_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create trades table
    op.create_table('trades',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('order_id', sa.String(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('side', sa.Enum('BUY', 'SELL', name='directiontype'), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('commission', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_params table
    op.create_table('risk_params',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('strategy_id', sa.String(), nullable=True),
        sa.Column('max_position_size', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('max_order_size', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('max_daily_loss', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('max_drawdown', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('position_limit_per_symbol', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('daily_order_limit', sa.Integer(), nullable=True),
        sa.Column('order_frequency_limit', sa.Integer(), nullable=True),
        sa.Column('risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'EXTREME', name='risklevel'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create backtest_reports table
    op.create_table('backtest_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('strategy_id', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('initial_capital', sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column('final_capital', sa.Numeric(precision=20, scale=6), nullable=False),
        sa.Column('total_return', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('annual_return', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('sharpe_ratio', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('sortino_ratio', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('calmar_ratio', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('max_drawdown', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('win_rate', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('profit_factor', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('alpha', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('beta', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('total_trades', sa.Integer(), nullable=True),
        sa.Column('winning_trades', sa.Integer(), nullable=True),
        sa.Column('losing_trades', sa.Integer(), nullable=True),
        sa.Column('data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create market_data table
    op.create_table('market_data',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('data_type', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('open', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('high', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('low', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('close', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('volume', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('turnover', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('bid_price', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('ask_price', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('bid_volume', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('ask_volume', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indicator_libraries table
    op.create_table('indicator_libraries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('path', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order to respect foreign key constraints
    op.drop_table('indicator_libraries')
    op.drop_table('market_data')
    op.drop_table('backtest_reports')
    op.drop_table('risk_params')
    op.drop_table('trades')
    op.drop_table('orders')
    op.drop_table('positions')
    op.drop_table('accounts')
    op.drop_table('strategies')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS strategystatus')
    op.execute('DROP TYPE IF EXISTS accounttype')
    op.execute('DROP TYPE IF EXISTS accountstatus')
    op.execute('DROP TYPE IF EXISTS risklevel')
    op.execute('DROP TYPE IF EXISTS positiondirection')
    op.execute('DROP TYPE IF EXISTS ordertype')
    op.execute('DROP TYPE IF EXISTS orderside')
    op.execute('DROP TYPE IF EXISTS orderstatus')
    op.execute('DROP TYPE IF EXISTS directiontype')