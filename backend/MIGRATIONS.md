# Database Migrations with Alembic

This document explains how to use Alembic for database migrations and versioning in the Ripple FundRaiser platform.

## Overview

Alembic is a lightweight database migration tool for SQLAlchemy. It allows you to:
- Track database schema changes over time
- Apply or rollback migrations safely
- Generate migrations automatically from model changes
- Maintain version control for your database schema

## Quick Start

```bash
# Create a new migration after changing models
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback the last migration
alembic downgrade -1

# View migration history
alembic history
```

## Installation

Alembic is already included in the project dependencies. If you need to install it:

```bash
cd backend
source .venv/bin/activate
uv pip install alembic
```

## Configuration

### Project Structure

```
backend/
├── alembic/
│   ├── versions/           # Migration files
│   │   └── 667bc022c053_initial_database_schema.py
│   ├── env.py             # Alembic environment configuration
│   └── script.py.mako     # Migration template
├── alembic.ini            # Alembic configuration file
├── database.py            # SQLAlchemy Base and engine
└── models.py              # Database models
```

### Alembic Configuration ([alembic.ini](alembic.ini))

The [alembic.ini](alembic.ini) file contains the main configuration:

```ini
[alembic]
script_location = %(here)s/alembic
prepend_sys_path = .
```

Key settings:
- `script_location`: Location of migration scripts (alembic/ directory)
- `prepend_sys_path`: Adds current directory to Python path for imports

### Environment Configuration ([alembic/env.py](alembic/env.py))

The [alembic/env.py](alembic/env.py:1-68) file connects Alembic to your database and models:

```python
from database import Base, DATABASE_URL
from models import User, Campaign, GiverProfile, Donation

# Set database URL from environment
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Add your model's MetaData for autogenerate support
target_metadata = Base.metadata
```

**Important:** All models must be imported in [alembic/env.py](alembic/env.py:17) for autogeneration to detect changes.

## Common Workflows

### 1. Creating Your First Migration

After setting up Alembic, create an initial migration:

```bash
cd backend
source .venv/bin/activate

# Generate initial migration from current models
alembic revision --autogenerate -m "initial database schema"

# Review the generated migration in alembic/versions/
# Apply the migration
alembic upgrade head
```

### 2. Adding a New Model

When you add a new model to [models.py](models.py):

1. **Define the model** in [models.py](models.py):
   ```python
   class NewModel(Base):
       __tablename__ = "new_table"
       id = Column(Integer, primary_key=True)
       name = Column(String(100))
   ```

2. **Import the model** in [alembic/env.py](alembic/env.py:17):
   ```python
   from models import User, Campaign, GiverProfile, Donation, NewModel
   ```

3. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "add new_table"
   ```

4. **Review the migration** in `alembic/versions/xxxx_add_new_table.py`:
   ```python
   def upgrade() -> None:
       op.create_table('new_table',
           sa.Column('id', sa.Integer(), nullable=False),
           sa.Column('name', sa.String(length=100), nullable=True),
           sa.PrimaryKeyConstraint('id')
       )
   ```

5. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

### 3. Modifying an Existing Model

When you modify a model field:

1. **Update the model** in [models.py](models.py):
   ```python
   class User(Base):
       # Changed from String(100) to String(200)
       email = Column(String(200), unique=True, nullable=False)
   ```

2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "increase email field length"
   ```

3. **Review and apply**:
   ```bash
   # Review the generated migration file
   cat alembic/versions/xxxx_increase_email_field_length.py

   # Apply if correct
   alembic upgrade head
   ```

### 4. Creating Manual Migrations

For data migrations or complex changes, create an empty migration:

```bash
alembic revision -m "migrate user data"
```

Then edit the generated file:

```python
def upgrade() -> None:
    # Custom migration logic
    op.execute("""
        UPDATE users
        SET status = 'active'
        WHERE created_at < '2025-01-01'
    """)

def downgrade() -> None:
    # Reverse the changes
    op.execute("""
        UPDATE users
        SET status = NULL
        WHERE created_at < '2025-01-01'
    """)
```

## Migration Commands

### Creating Migrations

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "description"

# Create empty migration for manual edits
alembic revision -m "description"

# Create migration with specific version ID
alembic revision --autogenerate --rev-id "custom_id" -m "description"
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +2

# Upgrade to specific revision
alembic upgrade abc123

# Apply migrations with SQL output (dry-run)
alembic upgrade head --sql
```

### Rolling Back Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base

# Show SQL for rollback (dry-run)
alembic downgrade -1 --sql
```

### Viewing Migration Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show verbose history with details
alembic history --verbose

# Show pending migrations
alembic current
alembic heads
```

## Best Practices

### 1. Always Review Generated Migrations

Alembic's autogenerate is smart but not perfect. Always review:

```bash
# Generate migration
alembic revision --autogenerate -m "changes"

# Review the file before applying
cat alembic/versions/xxxx_changes.py

# Apply only after review
alembic upgrade head
```

### 2. Test Migrations Before Deploying

```bash
# Create test database
docker exec -it fundraiser_db mysql -u fundraiser_user -p -e "CREATE DATABASE fundraiser_test"

# Update .env with test database
DATABASE_URL=mysql+pymysql://fundraiser_user:fundraiser_pass@localhost:3306/fundraiser_test

# Test migration
alembic upgrade head

# Test rollback
alembic downgrade -1

# Verify data integrity
```

### 3. Keep Migrations Small and Focused

Instead of one large migration:
```bash
alembic revision --autogenerate -m "add users, campaigns, and donations"
```

Create separate migrations:
```bash
alembic revision --autogenerate -m "add user model"
alembic upgrade head
alembic revision --autogenerate -m "add campaign model"
alembic upgrade head
alembic revision --autogenerate -m "add donation model"
```

### 4. Write Reversible Migrations

Always implement both `upgrade()` and `downgrade()`:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('verified', sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET verified = FALSE")
    op.alter_column('users', 'verified', nullable=False)

def downgrade() -> None:
    op.drop_column('users', 'verified')
```

### 5. Import All Models in env.py

For autogenerate to work, all models must be imported in [alembic/env.py](alembic/env.py:17):

```python
# Import ALL models here
from models import (
    User,
    Campaign,
    GiverProfile,
    Donation,
    # Add any new models here
)
```

### 6. Never Modify Applied Migrations

Once a migration is applied (especially in production), never modify it. Instead:

```bash
# Create a new migration to fix issues
alembic revision -m "fix previous migration"
```

### 7. Use Meaningful Migration Messages

Good messages:
```bash
alembic revision --autogenerate -m "add email verification to user model"
alembic revision -m "migrate existing users to new status field"
alembic revision --autogenerate -m "add indexes for campaign search"
```

Bad messages:
```bash
alembic revision --autogenerate -m "changes"
alembic revision -m "fix"
alembic revision --autogenerate -m "update models"
```

## Handling Common Scenarios

### Adding a Non-Nullable Column

When adding a required field to existing table:

```python
def upgrade() -> None:
    # Step 1: Add column as nullable
    op.add_column('users', sa.Column('status', sa.String(20), nullable=True))

    # Step 2: Set default value for existing rows
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")

    # Step 3: Make it non-nullable
    op.alter_column('users', 'status', nullable=False)

def downgrade() -> None:
    op.drop_column('users', 'status')
```

### Renaming a Column

```python
def upgrade() -> None:
    op.alter_column('campaigns', 'target_amount', new_column_name='goal_amount')

def downgrade() -> None:
    op.alter_column('campaigns', 'goal_amount', new_column_name='target_amount')
```

### Adding an Index

```python
def upgrade() -> None:
    op.create_index(
        'ix_campaigns_status_created',
        'campaigns',
        ['status', 'created_at']
    )

def downgrade() -> None:
    op.drop_index('ix_campaigns_status_created', 'campaigns')
```

### Data Migration with New Column

```python
def upgrade() -> None:
    # Add new column
    op.add_column('users', sa.Column('full_name', sa.String(200), nullable=True))

    # Migrate data from old columns
    op.execute("""
        UPDATE users
        SET full_name = CONCAT(first_name, ' ', last_name)
        WHERE first_name IS NOT NULL AND last_name IS NOT NULL
    """)

def downgrade() -> None:
    op.drop_column('users', 'full_name')
```

## Deployment Workflow

### Development Environment

```bash
# 1. Make model changes in models.py
# 2. Generate migration
alembic revision --autogenerate -m "description"

# 3. Review the migration
cat alembic/versions/xxxx_description.py

# 4. Test locally
alembic upgrade head

# 5. Commit migration file
git add alembic/versions/xxxx_description.py
git commit -m "feat(db): description"
```

### Production Deployment

```bash
# 1. Pull latest code with migrations
git pull origin main

# 2. Backup database (CRITICAL!)
docker exec fundraiser_db mysqldump -u fundraiser_user -p fundraiser_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Check current database version
alembic current

# 4. Preview migrations to be applied
alembic upgrade head --sql > preview_migrations.sql
cat preview_migrations.sql

# 5. Apply migrations
alembic upgrade head

# 6. Verify application still works
curl http://localhost:8000/health

# 7. If issues occur, rollback
alembic downgrade -1
# or restore from backup
```

## Troubleshooting

### "Target database is not up to date"

This occurs when database state doesn't match Alembic history:

```bash
# Check current state
alembic current

# Check what Alembic expects
alembic heads

# Option 1: Stamp database to current revision
alembic stamp head

# Option 2: Drop all tables and recreate
alembic downgrade base
alembic upgrade head
```

### "Can't locate revision identified by 'xyz'"

Migration file is missing or corrupted:

```bash
# List all migrations in database
alembic history

# If migration file is missing, restore from git
git log --all --full-history -- "alembic/versions/xyz*.py"
git checkout <commit> -- alembic/versions/xyz_*.py
```

### Autogenerate Not Detecting Changes

Ensure models are imported in [alembic/env.py](alembic/env.py:17):

```python
# Make sure this line includes ALL models
from models import User, Campaign, GiverProfile, Donation, YourNewModel
```

### Migration Fails Partway Through

```bash
# Check current state
alembic current

# If stuck in partial state, manually fix database then stamp
alembic stamp abc123

# Or rollback and try again
alembic downgrade -1
# Fix the migration file
alembic upgrade head
```

## Advanced Topics

### Branching and Merging

When multiple developers create migrations:

```bash
# Developer A creates migration abc123
# Developer B creates migration def456

# After merging, create a merge migration
alembic merge -m "merge migrations" abc123 def456

# This creates a new migration that depends on both
alembic upgrade head
```

### Offline SQL Generation

Generate SQL files for DBA review:

```bash
# Generate SQL for all pending migrations
alembic upgrade head --sql > migrations.sql

# Generate SQL for rollback
alembic downgrade -1 --sql > rollback.sql
```

### Custom Migration Template

Edit [alembic/script.py.mako](alembic/script.py.mako) to customize migration template:

```mako
"""${message}

Revision ID: ${up_revision}
Created: ${create_date}
"""

# Add custom imports or functions here
```

## Related Documentation

- [README.md](README.md) - Main backend setup and configuration
- [models.py](models.py) - Database model definitions
- [database.py](database.py) - SQLAlchemy configuration
- [Alembic Documentation](https://alembic.sqlalchemy.org/) - Official docs

## Quick Reference

```bash
# Common Commands Cheat Sheet
alembic revision --autogenerate -m "msg"  # Create migration
alembic upgrade head                       # Apply all migrations
alembic downgrade -1                       # Rollback one
alembic current                            # Show current version
alembic history                            # Show history
alembic upgrade head --sql                 # Show SQL (dry-run)
alembic stamp head                         # Mark as current without running
```
