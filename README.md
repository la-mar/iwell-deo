# Collector-iWell

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
