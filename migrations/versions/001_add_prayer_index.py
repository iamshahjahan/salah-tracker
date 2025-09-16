"""Add composite index on prayers table

Revision ID: 001_add_prayer_index
Revises:
Create Date: 2025-09-16 11:24:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add composite index on prayers table for better query performance"""
    # Create composite index on user_id, prayer_type, prayer_date
    op.create_index(
        'idx_prayers_user_type_date',
        'prayers',
        ['user_id', 'prayer_type', 'prayer_date'],
        unique=False
    )


def downgrade():
    """Remove the composite index from prayers table"""
    # Drop the composite index
    op.drop_index('idx_prayers_user_type_date', table_name='prayers')
