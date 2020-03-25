"""Note clerk application."""
from dataclasses import dataclass
from enum import Enum
from functools import reduce
import logging
import re
import sys
from typing import Callable, Iterable, Optional, TextIO, Tuple, TypeVar

import click

from . import __version__, utils
from .app import App
from .linting import lint_file


log = logging.getLogger(__name__)
unicode_log = logging.getLogger(f"{__name__}.unicode_file")


STD_IN_INDEPENDENT = "Standard in (`-`) should be used independent of any other file"


@click.group()
@click.option("--config-dir", type=click.Path(), envvar="NOTECLERK_CONFIG")
@click.version_option(version=__version__, prog_name="note-clerk")
@click.option(
    "--log-level",
    default="WARNING",
    type=click.Choice(["WARNING", "INFO", "DEBUG"], case_sensitive=False),
)
@click.pass_context
def cli(ctx: click.Context, config_dir: str, log_level: str) -> None:
    """Note clerk application."""
    ctx.obj = App(config_dir=config_dir)
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s| %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        # level=log_level.upper(),
    )
    logger = logging.getLogger("note_clerk")
    logger.setLevel(log_level.upper())
    unicode_log.setLevel(logging.ERROR)


@cli.command()
@click.pass_obj
def info(app: App) -> None:
    """Show app configuration."""
    click.echo(f'Configuration Directory: "{app.config_dir}"')


T = TypeVar("T")
TextAction = Callable[[TextIO, Optional[str]], T]


def _apply_to_paths(paths: Tuple[str], action: TextAction) -> Iterable[T]:
    log.debug(f"{paths=}")
    _paths = list(paths)

    if _paths.count("-") > 0 and _paths != ["-"]:
        raise click.BadArgumentUsage(STD_IN_INDEPENDENT)
    if _paths == ["-"]:
        yield from action(sys.stdin, None)
    else:
        try:
            for path in utils.all_files(paths):
                try:
                    with open(path, "r") as f:
                        log.debug(path)
                        yield from action(f, str(path))
                except UnicodeDecodeError:
                    unicode_log.warning(f'Unable to open "{path}", not unicode.')
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

    def _lint_text(text: TextIO, filename: Optional[str]) -> Iterable[bool]:
        _filename = filename or "stdin"
        found_lint = False
        for lint in lint_file(text, filename, lint_checks):
            found_lint = True
            click.echo(f"{_filename}:{lint.line}:{lint.column} | {lint.error}")
        yield found_lint

    either: Callable[[bool, bool], bool] = lambda x, y: x | y

    found_lint = reduce(either, _apply_to_paths(paths, _lint_text), False)
    if found_lint:
        ctx.exit(10)


@cli.group()
def analyze() -> None:
    """Analyze note contents."""
    ...


class TagLocation(Enum):
    """Note tag locations."""

    BODY = "body"
    HEADER = "header"
    HEADER_TAGS = "header_tags"
    HEADER_TOP_LEVEL = "header_top_level"


@dataclass
class FileTag:
    """Tag information."""

    tag: str
    filename: str
    line: int
    column: int
    tag_location: TagLocation


@analyze.command()
@click.argument("paths", nargs=-1, type=click.Path())
@click.pass_obj
def list_tags(app: App, paths: Tuple[str]) -> None:
    """List all tags in given notes."""
    TAG = r"#(#+)?[^\s\"'`\.,!#\]|)}/\\]+"
    TAG_FINDER = re.compile(r"(^" + TAG + r"|(?<=[\s\"'])" + TAG + r")")

    def _list_tags(text: TextIO, filename: Optional[str]) -> Iterable[FileTag]:
        log.debug(f"{text=} {filename=}")
        yaml_sep = 0
        for n, line in enumerate(text, start=1):
            log.debug(f"checking line {n:03}|{line[:-1]}")

            yaml_sep += line == "---\n"
            log.debug(f"{yaml_sep=}")
            if yaml_sep == 1:
                tag_location = TagLocation.HEADER
                if line.startswith("tags:"):
                    tag_location = TagLocation.HEADER_TAGS
                elif line.startswith("top_level:"):
                    tag_location = TagLocation.HEADER_TOP_LEVEL
            else:
                tag_location = TagLocation.BODY

            for match in TAG_FINDER.finditer(line):
                yield FileTag(
                    match.group(0),
                    filename or "stdin",
                    n,
                    match.start() + 1,
                    tag_location,
                )

    ft: FileTag
    for ft in _apply_to_paths(paths, _list_tags):
        click.echo(
            "\t".join(
                [
                    ft.tag,  # type: ignore
                    f"'{ft.filename}:{ft.line}:{ft.column}'",  # type: ignore
                    ft.tag_location.name,  # type: ignore
                ]
            )
        )
