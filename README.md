# Collector-iWell

### Environment Variables

Example development configuration. Environment variables can either be defined at the system level or in a filed named '.env' in the project's root directory.

```python

PYTHONPATH=~/repo/iwell-deo/iwell
IWELL_CLIENT_ID=KTDMpqhGyBMhnRDB
IWELL_CLIENT_SECRET=gYFRiXRtMN0fDYTDPUDYOk1RAbPz44Bu
IWELL_URL=https://api.iwell.info/v1
IWELL_USERNAME=observer@driftwoodenergy.com
IWELL_PASSWORD="%3U8NYX2eOP^@11q"
IWELL_TOKEN_PATH=/oauth2/access-token

DATABASE_DRIVER="postgres"
DATABASE_USERNAME="iwell"
DATABASE_PASSWORD=""
DATABASE_HOST="localhost"
DATABASE_NAME="iwell"
DATABASE_SCHEMA="public"

SENTRY_DSN=""
SENTRY_ENABLED=false
LOG_LEVEL=10

FLASK_APP=iwell.manage.py
FLASK_ENV=development
APP_SETTINGS=iwell.config.DevelopmentConfig
SECRET_KEY=my_precious
```

### Migrations

When setting up a new migration environment with alembic, edit version_table_schema
in env.py before running the first migration. This tells alembic to store the
table it uses to track migrations in the designated schema. If unspecified,
alembic will create the table in the public schema by default. Example below.

Similarly, adding "include_schemas=True" to the configuration call will instruct
alembic to generate migrations using fully qualified table names. This prevents
alembic from attempting to recreate existing tables that it created in previous
migrations. By default, alembic will create a table in the schema defined in
that table's flask model, but it will not see that table when reflecting the
database during future migrations.

```python
def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            version_table_schema="SCHEMA_NAME_HERE",
            include_schemas=True,
            **current_app.extensions["migrate"].configure_args,
        )

        with context.begin_transaction():
            context.run_migrations()

```
