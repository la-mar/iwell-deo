"""empty message

Revision ID: 8d5aa15ebdce
Revises: e4ad63130045
Create Date: 2019-12-07 10:32:18.763853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8d5aa15ebdce"
down_revision = "e4ad63130045"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        create or replace view vw_field_values(reading_at, well_name, field_name, value) as
        select
            fv.reading_at,
            w.well_name,
            f.field_name,
            fv.value::float as value
        from field_values fv
                join wells w on fv.well_id = w.id
                join fields f on fv.field_id = f.id
        where field_name <> 'Time of Gauge';
    """
    )


def downgrade():
    op.execute(
        """
        create or replace view vw_field_values(reading_at, well_name, field_name, value) as
        select
            fv.reading_at,
            w.well_name,
            f.field_name,
            fv.value
        from field_values fv
                join wells w on fv.well_id = w.id
                join fields f on fv.field_id = f.id
        where field_name <> 'Time of Gauge';
    """
    )
