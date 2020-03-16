"""Note clerk application."""
import click

from . import __version__


@click.command()
@click.version_option(version=__version__)
def cli() -> None:
    """Note clerk application."""
    click.echo("Hello, world!")
