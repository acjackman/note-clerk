"""Note clerk application."""
from dataclasses import dataclass
from enum import Enum
from functools import reduce, wraps
import io
import json
import logging
from pathlib import Path
import re
import sys
from typing import Any, Callable, Dict, Iterable, List, Optional, TextIO, Tuple, TypeVar

from boltons.fileutils import atomic_save
import click
import frontmatter
from orderedset import OrderedSet
from ruamel.yaml import YAML
import yaml


from . import __version__, utils
from .app import App
from .linting import lint_file
from .utils import ensure_newline


log = logging.getLogger(__name__)
unicode_log = logging.getLogger(f"{__name__}.unicode_file")


STD_IN_INDEPENDENT = "Standard in (`-`) should be used independent of any other file"


either: Callable[[bool, bool], bool] = lambda x, y: x | y


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

    found_lint = reduce(either, _apply_to_paths(paths, _lint_text), False)
    if found_lint:
        ctx.exit(10)


class UnableFix(Exception):
    """Unable to fix this particular file."""


def fix_header(header: str) -> str:
    output = io.StringIO()
    yaml = YAML(output=output)
    header_docs = [h for h in yaml.load_all(header) if h is not None]  # noqa: S506
    log.debug(f"header_docs:\n{header_docs}")

    if len(header_docs) < 2:
        return header

    combined: Dict[str, Any] = {}
    for doc in header_docs:
        log.debug(f"doc:\n{doc}")
        for key, value in sorted(doc.items(), key=lambda t: t[0]):
            try:
                existing = combined[key]
                if isinstance(existing, list) and isinstance(value, list):
                    combined[key] = list(OrderedSet(existing + value))
                elif existing == value:
                    pass
                else:
                    raise UnableFix("Unable to join constants")
            except KeyError:
                combined[key] = value

    yaml.dump(combined, output)

    return f"---\n{output.getvalue().strip()}\n***\n"


def fix_text(text: TextIO, filename: Optional[str]) -> Tuple[str, Optional[str]]:
    header, body = utils.split_header([line.strip() for line in text.readlines()])
    try:
        new_header = fix_header(header)
    except Exception:
        log.error("error creationg header", exc_info=True)
    log.debug(f"new_header:\n{new_header}")
    new_note: str = ensure_newline(new_header) + ensure_newline(body.strip())
    return new_note, filename


def raised_error(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Iterable[bool]:
        try:
            func(*args, **kwargs)
            yield False
        except UnableFix:
            yield True

    return wrapper


@raised_error
def update_text(
    text: TextIO,
    filename: Optional[str],
) -> None:
    log.debug(f"{filename=}")
    n_text, n_filename = fix_text(text, filename)

    if n_filename is None:
        click.echo(n_text.strip())
    # elif base_path is None:
    #     raise Exception("base_path must not be none if null filename")
    else:
        with atomic_save(n_filename, overwrite=True) as f:
            f.write(n_text)
        if filename is not None and filename != n_filename:
            Path(filename).unlink()


@cli.command()
@click.argument("paths", nargs=-1, type=click.Path())
@click.pass_obj
@click.pass_context
def fix(ctx: click.Context, app: App, paths: Tuple[str]) -> None:
    log.debug("running fix")

    try:
        acj: List[bool] = list(
            _apply_to_paths(
                paths,
                update_text,
            )
        )
        log.debug(f"{acj=}")
    except Exception:
        log.error("unable to apply to paths", exc_info=True)
        raise
    error = reduce(either, acj, False)
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
def list_types(app: App, paths: Tuple[str]) -> None:
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
