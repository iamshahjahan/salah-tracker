"""Add unique constraint on prayers table (fixed for foreign keys)

Revision ID: 002
Revises: 001
Create Date: 2025-09-16 11:35:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique constraint and clean up duplicates with foreign key handling"""

    # First, handle prayer_completions that reference duplicate prayers
    # We'll keep the completion records for the prayer with the highest ID (most recent)
    op.execute("""
        UPDATE prayer_completions pc
        INNER JOIN prayers p1 ON pc.prayer_id = p1.id
        INNER JOIN prayers p2 ON p1.user_id = p2.user_id
            AND p1.prayer_type = p2.prayer_type
            AND p1.prayer_date = p2.prayer_date
            AND p1.id < p2.id
        SET pc.prayer_id = p2.id
    """)

    # Now we can safely delete duplicate prayers, keeping the one with the highest ID
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
