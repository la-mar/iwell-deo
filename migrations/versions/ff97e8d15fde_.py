"""empty message

Revision ID: ff97e8d15fde
Revises:
Create Date: 2019-10-12 15:21:18.147409

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ff97e8d15fde"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("create schema if not exists iwell;")


def downgrade():
    pass
