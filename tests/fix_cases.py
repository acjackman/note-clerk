from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, TypeVar

from _pytest.mark.structures import ParameterSet
import pytest

from ._utils import inline_note


class Case:
    name: str
    skip: bool = False
    xfail: Optional[str] = None

    @property
    def code(self) -> str:
        slug_replacements = {
            " ": "-",
            "'": "",
            '"': "",
        }
        slug = self.name.lower()
        for char, to in slug_replacements.items():
            slug = slug.replace(char, to)
        return slug

    @property
    def as_param(self) -> ParameterSet:
        kwargs: Dict[str, Any] = {"id": self.code}
        if self.xfail is not None:
            kwargs["marks"] = pytest.mark.xfail(reason=self.xfail)
        if self.skip:
            kwargs["marks"] = pytest.mark.skip()
        return pytest.param(self, **kwargs)


@dataclass()
class FixCase(Case):
    name: str
    original: str
    fixed: str = ""
    filename: str = "-"
    newname: str = ""
    skip: bool = False
    xfail: Optional[str] = None

    def __post_init__(self) -> None:
        self.original = inline_note(self.original, trailing_newline=True)
        if self.fixed == "":
            self.fixed = self.original
        self.fixed = inline_note(self.fixed, trailing_newline=True)
        if self.newname == "":
            self.newname = self.filename


FIXES = [
    FixCase(
        name="Empty YAML Header doesn't change",
        original="""
        ---
        ---
        # Test Note
        """,
        fixed="""
        ---
        ---
        # Test Note
        """,
    ),
    FixCase(
        name="Collapses Headers",
        original="""
        ---
        tags: ["#tag2"]
        created: 2020-11-15T05:42:49.301Z
        ---
        ---
        created: 2020-11-15T05:42:49.301Z
        tags: ["#inbox"]
        ---
        # Test Note
        """,
        fixed="""
        ---
        created: 2020-11-15T05:42:49.301000Z
        tags:
        - '#tag2'
        - '#inbox'
        ---
        # Test Note
        """,
    ),
    FixCase(
        name="Collapses date headers by minimizing",
        original="""
        ---
        created: 2020-11-15T06:00:00Z
        ---
        ---
        created: 2020-11-15T05:42:49.301Z
        ---
        # Test Note
        """,
        fixed="""
        ---
        created: 2020-11-15T05:42:49.301000Z
        ---
        # Test Note
        """,
    ),
    FixCase(
        name="ID name doesn't change",
        original="""
        ---
        type: note
        ---
        # Title
        """,
        filename="00000000000000.md",
    ),
    FixCase(
        name="names don't change for non .md files",
        original="""
        ---
        type: note
        ---
        # Title
        """,
        filename="testing.txt",
    ),
    FixCase(
        name="maxes out id length",
        original="""
        ---
        type: note
        ---
        # Title
        """,
        filename="1234.md",
        newname="12340000000000.md",
    ),
    FixCase(
        name="overlong ids are not changed",
        original="""
        ---
        type: note
        ---
        # Title
        """,
        filename="123456789012345.md",
    ),
    FixCase(
        name="Multi-indent list unchanged",
        original="""
        - L1 item 1
            - L2 item 1.1
                - L3 item 1.1.1
            - 1.2
        - 2
        """,
    ),
    FixCase(
        name="Multi-indent list unchanged",
        original="""
        ---
        created: 2021-01-23T03:19:02.002Z
        ---
        ---
        created: 2021-01-22T20:22:59-0700
        ---
        """,
        fixed="""
        ---
        created: 2021-01-22T20:22:59-0700
        ---
        """,
        xfail="ruamel.yaml doesn't identify Z as a timezone marker",
    ),
]


@dataclass()
class UnfixableCase(Case):
    name: str
    original: str
    filename: str = "-"
    newname: str = ""
    skip: bool = False
    xfail: Optional[str] = None

    def __post_init__(self) -> None:
        self.original = inline_note(self.original, trailing_newline=True)
        if self.newname == "":
            self.newname = self.filename


UNFIXABLE = [
    UnfixableCase(
        name="unclosed header",
        original="""
        ---
        tags: ["#tag2"]
        created: 2020-11-15T05:42:49.301Z
        created: 2020-11-15T05:42:49.301Z
        tags: ["#inbox"]
        # Test Note
        """,
    ),
    UnfixableCase(
        name="unclosed header in file",
        original="""
        ---
        tags: ["#tag2"]
        created: 2020-11-15T05:42:49.301Z
        created: 2020-11-15T05:42:49.301Z
        tags: ["#inbox"]
        # Test Note
        """,
        filename="foo.md",
    ),
    UnfixableCase(
        name="duplicate keys integer values ",
        original="""
        ---
        k1: 1
        ---
        ---
        k1: 2
        ---
        # Test Note
        """,
    ),
    UnfixableCase(
        name="Unquoted tag in Array",
        original="""
        ---
        tags: ["#tag-a", #tag-b]
        ---
        # Note
        """,
    ),
    UnfixableCase(
        name="Mismatched Quotes",
        original="""
        ---
        tags: ['#bad-quotes"]
        ---
        """,
    ),
    UnfixableCase(
        name="Duplicate key in header",
        original="""
        ---
        key1: foo
        key1: bar
        ---
        """,
    ),
]


C = TypeVar("C", FixCase, UnfixableCase)


def is_stdin(case: C) -> bool:
    return case.filename is None or case.filename == "-"


def stdin_cases(cases: Iterable[C]) -> List[ParameterSet]:
    return [c.as_param for c in cases if is_stdin(c)]


def file_cases(cases: Iterable[C]) -> List[ParameterSet]:
    return [c.as_param for c in cases if not is_stdin(c)]
