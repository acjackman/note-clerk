"""Testing utility fuctions."""
from dataclasses import dataclass
from inspect import cleandoc as multiline_trim
import logging
from typing import Any, Dict, List, Optional, Tuple, TypedDict

from boltons.setutils import IndexedSet


log = logging.getLogger(__name__)


def inline_note(contents: str) -> str:
    """Create a file for testing."""
    return multiline_trim(contents)


def inline_header(header: str) -> str:
    """Create a file that is header only."""
    return inline_note(
        f"""
        ---
        {multiline_trim(header)}
        ---
        """
    )


def _get_from_lists(
    key: str, lists: List[Dict], default: Any = None, raise_error: bool = False
) -> Any:
    """Return the first instance of key in list of dictionaries."""
    for l in lists:
        try:
            return l[key]
        except KeyError:
            log.debug(f"Could not find key {key} in {l}")
            pass

    if raise_error:
        raise KeyError(f'"{key}" is not found in any list')

    return default


class ParamaterizationArgs(TypedDict):
    argnames: str
    argvalues: List[Tuple]
    ids: List[str]


class TestCase:
    id: str
    name: str


def paramaterize_cases(
    cases: List[Tuple[str, Dict[str, Any]]],
    default_values: Optional[Dict[str, Any]] = None,
    fill_none: bool = True,
    fill_default: bool = False,
) -> ParamaterizationArgs:
    """Create paramaterization from a set of named cases."""
    _default = default_values or {}
    ids = []
    argnames = IndexedSet()
    if fill_default:
        argnames |= IndexedSet(_default.keys())
    case_values = []

    for case_id, case_vars in cases:
        ids.append(case_id)
        argnames |= IndexedSet(case_vars.keys())
        case_values.append(case_vars)

    argnames = list(argnames)

    # Build list of tuples of values
    argvalues = [
        tuple(
            [
                _get_from_lists(var, [values, _default], raise_error=not fill_none)
                for var in argnames
            ]
        )
        for values in case_values
    ]
    return {
        "argnames": argnames,
        "argvalues": argvalues,
        "ids": ids,
    }
