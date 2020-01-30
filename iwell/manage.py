import logging
import os
import shutil
import sys
from collections import defaultdict
import subprocess

import click
from flask.cli import FlaskGroup, AppGroup

from api.models import *
import collector.tasks
from iwell import create_app, db
import loggers
from config import get_active_config
from collector.endpoint import load_from_config

logger = logging.getLogger()

import metrics


CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"], ignore_unknown_options=False
)
STATUS_COLOR_MAP = defaultdict(
    lambda: "white",
    {"success": "green", "error": "red", "timeout": "yellow", "failed": "red"},
)

conf = get_active_config()
app = create_app()
cli = FlaskGroup(create_app=create_app, context_settings=CONTEXT_SETTINGS)
run_cli = AppGroup("run")
test_cli = AppGroup("test")


def get_terminal_columns():
    return shutil.get_terminal_size().columns


def hr():
    return "-" * get_terminal_columns()


@cli.command()
def ipython_embed():
    """Runs a ipython shell in the app context."""
    try:
        import IPython
    except ImportError:
        click.echo("IPython not found. Install with: 'pip install ipython'")
        return
    from flask.globals import _app_ctx_stack

    app = _app_ctx_stack.top.app
    banner = "Python %s on %s\nIPython: %s\nApp: %s%s\nInstance: %s\n" % (
        sys.version,
        sys.platform,
        IPython.__version__,
        app.import_name,
        app.debug and " [debug]" or "",
        app.instance_path,
    )

    ctx = {}

    # Support the regular Python interpreter startup script if someone
    # is using it.
    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup, "r") as f:
            eval(compile(f.read(), startup, "exec"), ctx)

    ctx.update(app.make_shell_context())

    IPython.embed(banner1=banner, user_ns=ctx)


@run_cli.command()
@click.argument("endpoint")
@click.option(
    "--mode", "-m", help="Set to download records updated after the specified time",
)
@click.option(
    "--since",
    "-s",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Set to download records updated after the specified time",
)
@click.option(
    "from_",
    "--from",
    "-f",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Set to download records between the specified time and now",
)
@click.option(
    "--to",
    "-t",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Set to download records occuring before the specified time",
)
@click.option(
    "--verbose",
    "-v",
    help="Set the verbosity level. A higher verbosity level will generate more output during the process' execution. Repeat the flag to increase the verbosity level. (ex. -vvv)",
    show_default=True,
    count=True,
    default=2,
)
def endpoint(endpoint, mode, since, from_, to, verbose):
    "Run a one-off task to synchronize an endpoint"
    print(conf)
    kwargs = dict(since=since, start=from_, end=to,)

    if mode:
        kwargs.update(dict(mode=mode))

    if endpoint != "all":
        collector.tasks._sync_endpoint(endpoint, **kwargs)

    for name in load_from_config(conf).keys():
        collector.tasks._sync_endpoint(name, **kwargs)


@cli.command()
def endpoints():
    tpl = "{name:>20} {value:<50}"
    for name, ep in load_from_config(conf).items():
        click.secho(tpl.format(name=f"{name}:", value=str(ep)))


@run_cli.command()
@click.argument("celery_args", nargs=-1, type=click.UNPROCESSED)
def worker(celery_args):
    cmd = ["celery", "-E", "-A", "celery_queue.worker:celery", "worker",] + list(
        celery_args
    )
    subprocess.call(cmd)


@run_cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("celery_args", nargs=-1, type=click.UNPROCESSED)
def cron(celery_args):
    cmd = ["celery", "-A", "celery_queue.worker:celery", "beat",] + list(celery_args)
    subprocess.call(cmd)


@run_cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("celery_args", nargs=-1, type=click.UNPROCESSED)
def monitor(celery_args):
    cmd = ["celery", "-A", "celery_queue.worker:celery", "flower",] + list(celery_args)
    subprocess.call(cmd)


@test_cli.command()
def sentry():
    from loggers import load_sentry

    conf.SENTRY_ENABLED = True
    conf.SENTRY_EVENT_LEVEL = 10
    load_sentry()
    logger.error("Sentry Integration Test")


def main(argv=sys.argv):
    """
    Args:
        argv (list): List of arguments
    Returns:
        int: A return code
    Does stuff.
    """

    cli()
    return 0


@cli.command()
def recreate_db():
    # with app.app_context().push():
    db.drop_all()
    db.create_all()
    db.session.commit()


# @cli.command()
# def test():
#     """Runs the tests without code coverage"""
#     tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         return 0
#     sys.exit(result)


# @cli.command()
# def cov():
#     """Runs the unit tests with coverage."""
#     tests = unittest.TestLoader().discover('project/tests')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         COV.stop()
#         COV.save()
#         print('Coverage Summary:')
#         COV.report()
#         COV.html_report()
#         COV.erase()
#         return 0
#     sys.exit(result)

cli.add_command(run_cli)
cli.add_command(test_cli)

if __name__ == "__main__":
    cli()
