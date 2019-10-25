"""empty message

Revision ID: e211f751fb27
Revises: a1bbfc2ee006
Create Date: 2019-10-21 11:39:44.578256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e211f751fb27"
down_revision = "a1bbfc2ee006"
branch_labels = None
depends_on = None


def upgrade():
    pass
    # op.execute(
    #     """
    #     GRANT CONNECT ON DATABASE iwell TO grafana;
    #     GRANT USAGE ON SCHEMA public TO grafana;
    #     GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana;
    #     ALTER DEFAULT PRIVILEGES
    #     IN SCHEMA public
    #     GRANT SELECT ON TABLES TO grafana;
    # """
    # )


def downgrade():
    pass
    # op.execute(
    #     """
    #     REVOKE CONNECT ON DATABASE iwell from grafana;
    #     REVOKE USAGE ON SCHEMA public from grafana;
    #     REVOKE SELECT ON ALL TABLES IN SCHEMA public from grafana;
    #     ALTER DEFAULT PRIVILEGES
    #     IN SCHEMA public
    #     REVOKE SELECT ON TABLES from grafana;
    # """
    # )
