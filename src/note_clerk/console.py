"""Note clerk application."""
from typing import Tuple

import click

from . import __version__, _utils
from .app import App


@click.group()
@click.option("--config-dir", type=click.Path(), envvar="NOTECLERK_CONFIG")
@click.version_option(version=__version__, prog_name="note-clerk")
@click.pass_context
def cli(ctx: click.Context, config_dir: str) -> None:
    """Note clerk application."""
    ctx.obj = App(config_dir=config_dir)


@cli.command()
@click.pass_obj
def info(app: App) -> None:
    """Show app configuration."""
    click.echo(f'Configuration Directory: "{app.config_dir}"')


@cli.command()
@click.argument("paths", type=click.Path(), nargs=-1)
@click.pass_obj
def list_files(app: App, paths: Tuple[str]) -> None:
    """List all files selected by the given paths."""
    if len(paths) == 0:  # pragma: no cover
        paths = (".",)

    for file in _utils.all_files(paths):
        click.echo(file)
