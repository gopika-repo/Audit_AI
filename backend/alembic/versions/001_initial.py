"""Initial migration - create users, projects, and onboarding_progress tables.

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
from sqlalchemy import text

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("DO $$ BEGIN CREATE TYPE userrole AS ENUM ('admin', 'engineer', 'fresher'); EXCEPTION WHEN duplicate_object THEN null; END $$;"))

    op.execute(text("DO $$ BEGIN CREATE TYPE onboardingstatus AS ENUM ('not_started', 'in_progress', 'completed'); EXCEPTION WHEN duplicate_object THEN null; END $$;"))

    op.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            role userrole NOT NULL DEFAULT 'fresher',
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))

    op.execute(text("CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)"))

    op.execute(text("""
        CREATE TABLE IF NOT EXISTS projects (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            domain VARCHAR(100) NOT NULL,
            ai_category VARCHAR(100),
            tech_stack JSON NOT NULL DEFAULT '{}',
            repo_url VARCHAR(500),
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))

    op.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_name ON projects(name)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_domain ON projects(domain)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_is_active ON projects(is_active)"))

    op.execute(text("""
        CREATE TABLE IF NOT EXISTS onboarding_progress (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            status onboardingstatus NOT NULL DEFAULT 'not_started',
            progress_percentage INTEGER NOT NULL DEFAULT 0,
            started_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))

    op.execute(text("CREATE INDEX IF NOT EXISTS ix_onboarding_progress_user_id ON onboarding_progress(user_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_onboarding_progress_project_id ON onboarding_progress(project_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_onboarding_progress_status ON onboarding_progress(status)"))


def downgrade() -> None:
    op.execute(text("DROP TABLE IF EXISTS onboarding_progress CASCADE"))
    op.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
    op.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    op.execute(text("DROP TYPE IF EXISTS onboardingstatus"))
    op.execute(text("DROP TYPE IF EXISTS userrole"))