import datetime as dt
import io
import logging
from pathlib import Path
import re
from typing import Any, Callable, Dict, Iterable, Optional, TextIO, Tuple, Union

from boltons.fileutils import atomic_save
from dateutil.parser import parse as parse_date
from orderedset import OrderedSet
from ruamel.yaml import YAML
from ruamel.yaml.timestamp import TimeStamp

from . import utils
from .utils import ensure_newline


log = logging.getLogger(__name__)


class UnableFix(Exception):
    """Unable to fix this particular file."""


DateLike = Union[TimeStamp, dt.datetime, str]


def as_date(value: DateLike) -> dt.datetime:
    if isinstance(value, str):
        return parse_date(value)
    return value


def min_date(existing: DateLike, new: DateLike) -> DateLike:
    existing_date = as_date(existing)
    new_date = as_date(new)
    if existing_date <= new_date:
        return existing
    else:
        return new


def merge_values(key: str, existing: Any, new: Any) -> Any:
    if isinstance(existing, list) and isinstance(new, list):
        return list(OrderedSet(existing + new))
    if existing == new:
        return existing
    if key == "created":
        try:
            log.debug(f"{type(existing)=} {type(new)=}")
            return min_date(existing, new)
        except (TypeError, ValueError):
            pass
    if isinstance(existing, int) or isinstance(new, int):
        raise UnableFix("Unable to join integers")
    raise UnableFix("Unable to join constants")


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
                combined[key] = merge_values(key, combined[key], value)
            except KeyError:
                combined[key] = value

    yaml.dump(combined, output)

    return f"---\n{output.getvalue().strip()}\n***\n"


ID_REGEX = re.compile(r"^([0-9]+)")


def fix_filename(filename: Optional[str]) -> Optional[str]:
    if filename is None:
        return None
    path = Path(filename)
    stem = path.stem
    match = ID_REGEX.match(stem)
    log.debug(f"{match=}")
    if match is None:
        return filename
    orig_note_id = match.groups()[0]
    if len(orig_note_id) == 14:
        return filename
    elif len(orig_note_id) < 14:
        note_id = orig_note_id.ljust(14, "0")
        new_filename = stem.replace(orig_note_id, note_id) + path.suffix
        log.debug(f"{new_filename=}")
        new_path = path.parent / new_filename
        while new_path.exists():
            rename_match = ID_REGEX.match(new_filename)
            assert rename_match is not None  # noqa: S101
            note_id = rename_match.groups()[0]
            updated_id = str(int(note_id) + 1).rjust(14, "0")
            new_filename = new_filename.replace(note_id, updated_id)
            log.debug(f"{new_filename=}")
            new_path = path.parent / new_filename
        return str(new_path)
    return filename


def fix_text(text: TextIO, filename: Optional[str]) -> Tuple[str, Optional[str]]:
    header, body = utils.split_header([line.strip() for line in text.readlines()])
    try:
        new_header = fix_header(header)
    except Exception:
        log.error("error creating header", exc_info=True)
        raise
    log.debug(f"new_header:\n{new_header}")
    new_note: str = ensure_newline(new_header) + ensure_newline(body.strip())
    new_filename = fix_filename(filename)
    return new_note, new_filename


def raised_error(func: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> Iterable[bool]:
        try:
            func(*args, **kwargs)
            yield False
        except UnableFix:
            yield True

    return wrapper


@raised_error
def update_text(
    text: TextIO,
    filename: str,
) -> None:
    log.debug(f"{filename=}")
    n_text, n_filename = fix_text(text, filename)
    with atomic_save(n_filename, overwrite=True) as f:
        f.write(n_text.encode("utf-8"))
    log.debug(f"\n  {filename=}\n{n_filename=}")
    if filename is not None and filename != n_filename:
        log.debug("Deleting file")
        Path(filename).unlink()
