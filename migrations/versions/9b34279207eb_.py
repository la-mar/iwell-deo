"""empty message

Revision ID: 9b34279207eb
Revises: e211f751fb27
Create Date: 2019-10-21 12:04:11.866801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b34279207eb"
down_revision = "e211f751fb27"
branch_labels = None
depends_on = None


def upgrade():
    pass
    # op.execute("""ALTER ROLE grafana SET search_path = public;""")


def downgrade():
    pass
    # op.execute("""ALTER ROLE grafana SET search_path = '';""")
