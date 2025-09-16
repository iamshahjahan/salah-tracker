"""Add unique constraint on prayers table

Revision ID: 002_add_unique_constraint_prayers
Revises: 001_add_prayer_index
Create Date: 2025-09-16 11:30:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique constraint and clean up duplicates"""

    # First, remove duplicate records, keeping the one with the highest ID (most recent)
    op.execute("""
        DELETE p1 FROM prayers p1
        INNER JOIN prayers p2
        WHERE p1.user_id = p2.user_id
        AND p1.prayer_type = p2.prayer_type
        AND p1.prayer_date = p2.prayer_date
        AND p1.id < p2.id
    """)

    # Add unique constraint on user_id, prayer_type, prayer_date
    op.create_unique_constraint(
        'uq_prayers_user_type_date',
        'prayers',
        ['user_id', 'prayer_type', 'prayer_date']
    )


def downgrade():
    """Remove the unique constraint"""
    # Drop the unique constraint
    op.drop_constraint('uq_prayers_user_type_date', 'prayers', type_='unique')
