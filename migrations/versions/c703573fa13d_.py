"""empty message

Revision ID: c703573fa13d
Revises: d78f6bcc7f5a
Create Date: 2019-11-26 15:01:28.870000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c703573fa13d"
down_revision = "d78f6bcc7f5a"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        create view vw_field_values as
        select
            reading_at,
            well_name,
            field_name,
            value
        from field_values fv
                inner join wells w on fv.well_id = w.id
                inner join fields f on fv.field_id = f.id
    """
    )


def downgrade():
    op.execute("""drop view vw_field_values""")
