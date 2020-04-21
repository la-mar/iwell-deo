"""empty message

Revision ID: 6ce83ad65bc1
Revises: cfec89b6878b
Create Date: 2020-04-21 13:28:53.274086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6ce83ad65bc1"
down_revision = "cfec89b6878b"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """

        create function table_metrics(schemaname character varying
                                    ) returns SETOF record
            language plpgsql
        as
        $fun$
        declare
            r record;
            t varchar;
        begin
            for t in execute $$
                select n.nspname || '.' || c.relname
                    from pg_namespace as n, pg_class as c
                    where n.oid = c.relnamespace
                        and c.relkind = 'r'
                        and n.nspname = '$$ || schemaname || $$'
                        and 'updated_at' in (SELECT column_name
                                                FROM information_schema.columns
                                                WHERE table_schema = '$$ || schemaname || $$'
                                                and table_name = c.relname
                                                and column_name = 'updated_at'
                                            )
                            $$

            loop
                execute 'select ''' || t || '''::varchar, count(*), min(updated_at)::timestamptz, max(updated_at)::timestamptz from ' || t
                    into r;
                return next r;
            end loop;
            return;
        end;
        $fun$;


    create or replace view vw_data_table_metrics as
    select
        'public' as schema_name,
        split_part(table_name, '.', 2) as table_name,
        table_name as qualified_table_name,
        rowcount as table_rowcount,
        (EXTRACT(epoch FROM now() - updated_at_max)/60)::int as min_since_last_update,
        updated_at_min as table_oldest,
        updated_at_max as table_newest
    from public.table_metrics('public') t(table_name varchar, rowcount bigint, updated_at_min timestamptz, updated_at_max timestamptz)order by updated_at_max desc;


    """
    )


def downgrade():
    op.execute(
        """
    drop view vw_data_table_metrics;
    drop function table_metrics;
    """
    )
