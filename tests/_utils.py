"""Testing utility fuctions."""
from dataclasses import dataclass
from inspect import cleandoc as multiline_trim
import logging
from typing import Any, List, Mapping, Optional, Tuple, TypedDict

from boltons.setutils import IndexedSet  # type: ignore


log = logging.getLogger(__name__)


def inline_note(contents: str, trailing_newline: bool = True) -> str:
    """Create a file for testing."""
    contents = multiline_trim(contents).strip()
    if trailing_newline:
        return contents + "\n"
    else:
        return contents


def inline_header(header: str, trailing_newline: bool = True) -> str:
    """Create a file that is header only."""
    contents = f"---\n{multiline_trim(header).strip()}\n---"
    if trailing_newline:
        return contents + "\n"
    else:
        return contents


ParamaterizationVars = Mapping[str, Any]


class ParamaterizationArgs(TypedDict):
    """Arguments for the pytest.mark.paramaterize function."""

    argnames: str
    argvalues: List[Tuple]
    ids: List[str]


@dataclass(frozen=True)
class ParamCase:
    """Paramatarized test case."""

    id: str
    variables: ParamaterizationVars
    description: Optional[str] = None


def _get_from_lists(
    key: str,
    lists: List[ParamaterizationVars],
    default: Any = None,
    raise_error: bool = False,
) -> Any:
    """Return the first instance of key in list of dictionaries."""
    for params in lists:
        try:
            return params[key]
        except KeyError:
            log.debug(f"Could not find key {key} in {params}")
            pass

    if raise_error:
        raise KeyError(f'"{key}" is not found in any list')

    return default


def paramaterize_cases(
    cases: List[ParamCase],
    default_values: Optional[ParamaterizationVars] = None,
    fill_none: bool = True,
    fill_default: bool = False,
) -> ParamaterizationArgs:
    """Create paramaterization from a set of named cases."""
    _default = default_values or {}

    # Build the list of paramaterized values
    argnames = IndexedSet()
    if fill_default:
        argnames |= IndexedSet(_default.keys())

    # Build list case ids, values, and add any argnames that weren't in default
    ids = []
    case_values = []
    for case in cases:
        ids.append(case.id)
        argnames |= IndexedSet(case.variables.keys())
        case_values.append(case.variables)

    # Convert argnames to a list once we have identified all posibilities
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

    return ParamaterizationArgs(
        argnames=argnames,
        argvalues=argvalues,
        ids=ids,
    )
