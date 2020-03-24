"""Note clerk application."""
from functools import reduce
import logging
import sys
from typing import Callable, Iterable, Optional, TextIO, Tuple, TypeVar

import click

from . import __version__, utils
from .app import App
from .linting import lint_file


log = logging.getLogger(__name__)


STD_IN_INDEPENDENT = "Standard in (`-`) should be used independent of any other file"


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


T = TypeVar("T")
TextAction = Callable[[TextIO, Optional[str]], T]


def _apply_to_paths(
    ctx: click.Context, app: App, paths: Tuple[str], action: TextAction
) -> Iterable[T]:
    _paths = list(paths)

    if _paths.count("-") > 0 and _paths != ["-"]:
        raise click.BadArgumentUsage(STD_IN_INDEPENDENT)
    if _paths == ["-"]:
        yield action(sys.stdin, None)
    else:
        try:
            for file in utils.all_files(paths):
                with open(file, "r") as f:
                    yield action(f, str(file))
        except utils.FilesNotFound as e:
            raise click.BadArgumentUsage(
                f"All paths should exist, these do not: {utils.quoted_paths(e.missing)}"
            ) from e


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path())
@click.pass_obj
@click.pass_context
def lint(ctx: click.Context, app: App, paths: Tuple[str]) -> None:
    """Lint all files selected by the given paths."""
    # TODO: checks should come from plugins
    lint_checks = app.lint_checks

    def _lint_text(text: TextIO, filename: Optional[str]) -> bool:
        _filename = filename or "stdin"
        found_lint = False
        for lint in lint_file(text, filename, lint_checks):
            found_lint = True
            click.echo(f"{_filename}:{lint.line}:{lint.column} | {lint.error}")
        return found_lint

    either: Callable[[bool, bool], bool] = lambda x, y: x | y

    found_lint = reduce(either, _apply_to_paths(ctx, app, paths, _lint_text),)
    if found_lint:
        ctx.exit(10)
