"""Delivery date changed to date format only

Revision ID: 2a926c1f4a57
Revises: 36465e9a971a
Create Date: 2024-04-25 15:45:46.097676

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a926c1f4a57'
down_revision = '36465e9a971a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fuel_quote', schema=None) as batch_op:
        batch_op.alter_column('delivery_date',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.Date(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fuel_quote', schema=None) as batch_op:
        batch_op.alter_column('delivery_date',
               existing_type=sa.Date(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    # ### end Alembic commands ###
