from functools import wraps
import io
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional, TextIO, Tuple

from boltons.fileutils import atomic_save
import click
from orderedset import OrderedSet
from ruamel.yaml import YAML


from . import utils
from .utils import ensure_newline


log = logging.getLogger(__name__)


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
        log.error("error creating header", exc_info=True)
        raise
    log.debug(f"new_header:\n{new_header}")
    new_note: str = ensure_newline(new_header) + ensure_newline(body.strip())
    return new_note, filename


def raised_error(func: Callable) -> Callable:
    @wraps(func)
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
