"""Note clerk application."""
import logging
import sys
from typing import Optional, TextIO, Tuple

import click

from . import __version__, utils
from .app import App
from .linting import lint_file, LintChecks


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


def _lint_text(text: TextIO, filename: Optional[str], lint_checks: LintChecks) -> bool:
    _filename = filename or "stdin"
    found_lint = False
    for lint in lint_file(text, filename, lint_checks):
        found_lint = True
        click.echo(f"{_filename}:{lint.line}:{lint.column} | {lint.error}")
    return found_lint


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path())
@click.pass_obj
@click.pass_context
def lint(ctx: click.Context, app: App, paths: Tuple[str]) -> None:
    """Lint all files selected by the given paths."""
    _paths = list(paths)
    log.debug(f"_paths={_paths}")

    # TODO: checks should come from plugins
    lint_checks = app.lint_checks
    found_lint = False

    if _paths.count("-") > 0 and _paths != ["-"]:
        raise click.BadArgumentUsage(STD_IN_INDEPENDENT)

    if _paths == ["-"]:
        log.debug("linting stdin")
        found_lint |= _lint_text(sys.stdin, None, lint_checks)
    else:
        try:
            for file in utils.all_files(paths):
                log.debug(f"attempting to open '{file}'")
                with open(file, "r") as f:
                    log.debug(f"linting '{file}'")
                    found_lint |= _lint_text(f, str(file), lint_checks)
        except utils.FilesNotFound as e:
            raise click.BadArgumentUsage(
                f"All paths should exist, these do not: {utils.quoted_paths(e.missing)}"
            ) from e

    if found_lint:
        ctx.exit(10)
