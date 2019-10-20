import logging
import os
import shutil
import sys
from collections import defaultdict

import click
from flask.cli import FlaskGroup

from api.models import *
import collector.tasks
from iwell import create_app, db
import loggers

loggers.standard_config()
logger = logging.getLogger(__name__)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
STATUS_COLOR_MAP = defaultdict(
    lambda: "white",
    {"success": "green", "error": "red", "timeout": "yellow", "failed": "red"},
)

app = create_app()
cli = FlaskGroup(create_app=create_app)


def update_logger(level: int, formatter: str = None):
    if level is not None:
        loggers.standard_config(verbosity=level, formatter=formatter)


def get_terminal_columns():
    return shutil.get_terminal_size().columns


def hr():
    return "-" * get_terminal_columns()


# @click.group(context_settings=CONTEXT_SETTINGS)
# def cli():
#     pass


# @cli.command("urlmap")
# def urlmap():
#     """Prints out all routes"""
#     click.echo("{:50s} {:40s} {}".format("Endpoint", "Methods", "Route"))
#     for route in app.url_map.iter_rules():
#         methods = ",".join(route.methods)
#         click.echo("{:50s} {:40s} {}".format(route.endpoint, methods, route))


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


@cli.command()
def run():
    # app.run()
    pass


@cli.command()
@click.argument("endpoint")
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
def sync_endpoint(endpoint, since, from_, to, verbose):
    "Run a one-off task to synchronize an endpoint"
    update_logger(verbose, formatter="layman")
    # app.app_context().push()
    collector.tasks._sync_endpoint(endpoint, since=since, start=from_, end=to)


@cli.command()
def endpoints():
    print("iwell cli")


def main(argv=sys.argv):
    """
    Args:
        argv (list): List of arguments
    Returns:
        int: A return code
    Does stuff.
    """
    # print(argv)

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


if __name__ == "__main__":
    cli()
