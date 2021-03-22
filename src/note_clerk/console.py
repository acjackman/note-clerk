"""Note clerk application."""
from dataclasses import dataclass
import datetime as dt
from enum import Enum
from functools import reduce, wraps
import json
import logging
import re
import sys
from typing import Any, Callable, Iterable, Optional, TextIO, TypeVar

import click
from dateutil.parser import parse as parse_date
import frontmatter
import yaml


from . import __version__, fixing, utils
from .app import App
from .linting import lint_file


log = logging.getLogger(__name__)
unicode_log = logging.getLogger(f"{__name__}.unicode_file")


STD_IN_INDEPENDENT = "Standard in (`-`) should be used independent of any other file"


def either(x: bool, y: bool) -> bool:
    return x | y


def log_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Callable:
        try:
            return func(*args, **kwargs)
        except click.exceptions.Exit:
            raise
        except Exception as exc:
            log.error(f"Unhandled Exception: {exc}", exc_info=True)
            raise

    return wrapper


@click.group()
@click.option("--config-dir", type=click.Path(), envvar="NOTECLERK_CONFIG")
@click.version_option(version=__version__, prog_name="note-clerk")
@click.option(
    "--log-level",
    default="WARNING",
    type=click.Choice(["WARNING", "INFO", "DEBUG"], case_sensitive=False),
)
@click.pass_context
@log_errors
def cli(ctx: click.Context, config_dir: Optional[str], log_level: str) -> None:
    """Note clerk application."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s| %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=log_level.upper(),
    )
    unicode_log.setLevel(logging.ERROR)

    ctx.obj = App(config_dir=config_dir)


@cli.command()
@click.pass_obj
@log_errors
def info(app: App) -> None:
    """Show app configuration."""
    click.echo(f'Configuration Directory: "{app.config_dir}"')


T = TypeVar("T")
TextAction = Callable[[TextIO, Optional[str]], T]


def _apply_to_paths(paths: Iterable[str], action: TextAction) -> Iterable[T]:
    _paths = list(paths)

    if _paths.count("-") > 0 and _paths != ["-"]:
        raise click.BadArgumentUsage(STD_IN_INDEPENDENT)
    if _paths == ["-"]:
        log.debug("Text coming from stdin")
        yield from action(sys.stdin, None)
    else:
        try:
            for path in utils.all_files(paths):
                try:
                    log.debug(f"attempting to open '{path}'")
                    with open(path, "r") as f:
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
@log_errors
def lint(ctx: click.Context, app: App, paths: Iterable[str]) -> None:
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

    found_lint = reduce(either, _apply_to_paths(paths, _lint_text), False)
    if found_lint:
        ctx.exit(10)


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path())
@click.pass_obj
@click.pass_context
@log_errors
def fix(ctx: click.Context, app: App, paths: Iterable[str]) -> None:
    error = reduce(either, _apply_to_paths(paths, fixing.update_text), False)
    if error:
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
def list_tags(app: App, paths: Iterable[str]) -> None:
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


@dataclass
class FileValue:
    """Value along with file location it was found in."""

    value: str
    filepath: Optional[str]
    line: Optional[int] = None
    column: Optional[int] = None

    def file_location(self) -> str:
        """Return specified file location."""
        location = self.filepath or ""
        if self.line:
            location += f":{self.line}"
            if self.column:
                location += f":{self.column}"
        return location


@analyze.command()
@click.argument("paths", nargs=-1, type=click.Path())
@click.pass_obj
def list_types(app: App, paths: Iterable[str]) -> None:
    """List all types in given notes."""

    def _list_types(text: TextIO, filename: Optional[str]) -> Iterable[FileValue]:
        # log.debug(f"{text=} {filename=}")
        try:
            metadata, content = frontmatter.parse(text.read())
            yield FileValue(metadata["type"], filename)
        except (KeyError, yaml.parser.ParserError, json.decoder.JSONDecodeError):
            pass

    fv: FileValue
    for fv in _apply_to_paths(paths, _list_types):
        click.echo(
            "\t".join(
                [
                    fv.value,  # type: ignore
                    f"'{fv.file_location()}'",  # type: ignore
                ]
            )
        )


@cli.group()
@click.pass_obj
def plan(app: App) -> None:
    pass


@plan.command()
@click.pass_obj
@click.option("--next", "next_date", is_flag=True)
@click.option("--prev", "prev_date", is_flag=True)
@click.option("--date", "date_text", default=lambda: f"{dt.datetime.now():%Y-%m-%d}")
def week(app: App, next_date: bool, prev_date: bool, date_text: str) -> None:
    from . import planning

    date = parse_date(date_text)
    date = planning.determine_date(date, next_date, prev_date)

    plan = planning.create_week_plan_file(planning.last_monday(), app.notes_dir)
    click.echo(plan)


@plan.command()
@click.pass_obj
@click.option("--next", "next_date", is_flag=True)
@click.option("--prev", "prev_date", is_flag=True)
@click.option("--date", "date_text", default=lambda: f"{dt.datetime.now():%Y-%m-%d}")
def day(app: App, next_date: bool, prev_date: bool, date_text: str) -> None:
    from . import planning

    date = parse_date(date_text)
    try:
        date = planning.determine_date(date, next_date, prev_date)
    except Exception:
        raise ScriptFailed("--next and --prev must not be passed together")

    day_plan = planning.create_day_plan_file(date, app.notes_dir)
    click.echo(day_plan)


class ScriptFailed(click.ClickException):
    exit_code = 1

    def show(self, file: Any = None) -> None:
        """Stub out the show to exit silently."""
