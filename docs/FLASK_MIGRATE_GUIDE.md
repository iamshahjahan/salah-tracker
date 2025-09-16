# Flask-Migrate Guide

This guide explains how to use Flask-Migrate for database schema management in the Salah Tracker application.

## Overview

Flask-Migrate is now properly set up and configured for managing database migrations. It provides a structured way to handle database schema changes, making it easy to:

- Track database changes over time
- Apply migrations to different environments
- Rollback changes if needed
- Collaborate on database schema changes

## Setup

Flask-Migrate is already configured in `main.py`:

```python
from flask_migrate import Migrate
migrate = Migrate(app, db)
```

## Directory Structure

```
migrations/
├── alembic.ini          # Alembic configuration
├── env.py               # Migration environment
├── script.py.mako       # Migration template
├── README               # Flask-Migrate documentation
└── versions/            # Migration files
    └── 001_add_prayer_index.py
```

## Available Commands

### Using Flask CLI

```bash
# Set environment variable
export FLASK_APP=main.py

# Initialize migrations (already done)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback one migration
flask db downgrade

# Show current revision
flask db current

# Show migration history
flask db history

# Show migration heads
flask db heads
```

### Using the Management Script

We've created a convenient management script at `scripts/manage_migrations.py`:

```bash
# Show help
python3 scripts/manage_migrations.py help

# Check current status
python3 scripts/manage_migrations.py status

# Create a new migration
python3 scripts/manage_migrations.py create "Add user preferences table"

# Apply migrations
python3 scripts/manage_migrations.py upgrade

# Show history
python3 scripts/manage_migrations.py history
```

## Current Migrations

### 001_add_prayer_index
- **Purpose**: Adds a composite index on the `prayers` table
- **Columns**: `user_id`, `prayer_type`, `prayer_date`
- **Benefits**: Improves query performance for prayer lookups by user and date

## Best Practices

### 1. Always Create Migrations for Schema Changes
```bash
# Before making model changes, create a migration
flask db migrate -m "Add new column to users table"
```

### 2. Review Migration Files
Always review the generated migration files before applying them:

```python
# Check the generated migration in migrations/versions/
def upgrade():
    # Review the changes here
    pass

def downgrade():
    # Review the rollback changes here
    pass
```

### 3. Test Migrations
```bash
# Test on a development database first
flask db upgrade

# If something goes wrong, rollback
flask db downgrade
```

### 4. Commit Migration Files
Always commit migration files to version control:

```bash
git add migrations/versions/
git commit -m "Add migration for user preferences"
```

## Remote Server Deployment

### Apply Migrations on Remote Server

```bash
# SSH into the server
ssh -i /path/to/key.pem ec2-user@your-server

# Navigate to the project directory
cd /var/www/salah-tracker

# Activate virtual environment
source venv/bin/activate

# Set Flask app
export FLASK_APP=main.py

# Apply migrations
flask db upgrade
```

### Check Migration Status on Remote Server

```bash
# Check current revision
flask db current

# Check migration history
flask db history
```

## Troubleshooting

### Common Issues

1. **"No changes in schema detected"**
   - This happens when Flask-Migrate can't detect changes
   - Make sure your models are properly imported in `main.py`
   - Try creating a manual migration file

2. **"Target database is not up to date"**
   - Run `flask db upgrade` to apply pending migrations
   - Check `flask db current` to see the current state

3. **"Can't locate revision identified by 'xyz'"**
   - This usually means the migration history is corrupted
   - Check `flask db history` to see the migration chain
   - You may need to manually fix the migration files

### Manual Migration Creation

If automatic migration generation doesn't work, create manual migration files:

```python
"""Add new feature

Revision ID: 002_add_feature
Revises: 001_add_prayer_index
Create Date: 2025-09-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '002_add_feature'
down_revision = '001_add_prayer_index'
branch_labels = None
depends_on = None

def upgrade():
    # Add your changes here
    op.add_column('users', sa.Column('new_field', sa.String(100)))

def downgrade():
    # Add rollback changes here
    op.drop_column('users', 'new_field')
```

## Integration with Existing Custom Migrations

The existing custom migration files in `migrations_backup/` can be converted to Flask-Migrate format:

1. Review the custom migration logic
2. Create a new Flask-Migrate migration
3. Copy the relevant SQL operations
4. Test the migration

## Environment Variables

Make sure these environment variables are set:

```bash
export FLASK_APP=main.py
export DATABASE_URL=mysql://user:password@localhost/database
```

## Monitoring

### Check Migration Status
```bash
# Local development
python3 scripts/manage_migrations.py status

# Remote server
ssh user@server 'cd /path/to/app && source venv/bin/activate && flask db current'
```

### Log Migration Activities
All migration activities are logged in the application logs. Check `logs/salah_tracker_*.log` for migration-related messages.

## Next Steps

1. **Convert Existing Migrations**: Review and convert the custom migrations in `migrations_backup/`
2. **Add Model Changes**: Use Flask-Migrate for all future database changes
3. **Set Up CI/CD**: Integrate migration checks into your deployment pipeline
4. **Documentation**: Keep this guide updated as you add new migrations

## Resources

- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Migration Tutorial](https://docs.sqlalchemy.org/en/14/core/metadata.html)
