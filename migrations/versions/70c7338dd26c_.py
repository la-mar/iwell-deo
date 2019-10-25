"""empty message

Revision ID: 70c7338dd26c
Revises: 20d38cfe7b17
Create Date: 2019-10-22 13:47:30.519261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70c7338dd26c'
down_revision = '20d38cfe7b17'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('run_tickets', 'run_ticket_number',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('run_tickets', 'run_ticket_number',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
