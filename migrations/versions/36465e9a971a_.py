"""empty message

Revision ID: 36465e9a971a
Revises: 
Create Date: 2024-04-11 16:07:48.489694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36465e9a971a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=120), nullable=False),
    sa.Column('profile_complete', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('fuel_quote',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('gallons_requested', sa.Float(), nullable=False),
    sa.Column('delivery_date', sa.DateTime(), nullable=False),
    sa.Column('total_amount_due', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('price_per_gallon', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('delivery_fee', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('profile_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('full_name', sa.String(length=100), nullable=True),
    sa.Column('address1', sa.String(length=200), nullable=True),
    sa.Column('address2', sa.String(length=200), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.Column('zip_code', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('profile_info')
    op.drop_table('fuel_quote')
    op.drop_table('user')
    # ### end Alembic commands ###
