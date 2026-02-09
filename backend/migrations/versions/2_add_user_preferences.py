"""add user preferences

Revision ID: 2add_user_preferences
Revises: 1cafdaca745b
Create Date: 2026-01-02 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2add_user_preferences'
down_revision = '1cafdaca745b'
branch_labels = None
depends_on = None


def upgrade():
    # ### Add preferred_currency column ###
    op.add_column('users', sa.Column('preferred_currency', sa.String(length=3), nullable=True, server_default='USD'))
    
    # ### Add chat_initialized column ###
    op.add_column('users', sa.Column('chat_initialized', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade():
    # ### Drop columns ###
    op.drop_column('users', 'chat_initialized')
    op.drop_column('users', 'preferred_currency')
