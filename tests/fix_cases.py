from dataclasses import dataclass

from ._utils import inline_note


@dataclass()
class FixCase:
    name: str
    original: str
    fixed: str = ""
    filename: str = "-"
    newname: str = ""

    def __post_init__(self) -> None:
        self.original = inline_note(self.original, trailing_newline=True)
        if self.fixed == "":
            self.fixed = self.original
        self.fixed = inline_note(self.fixed, trailing_newline=True)
        if self.newname == "":
            self.newname = self.filename

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
]


UNFIXABLE = [
    FixCase(
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
    FixCase(
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
    FixCase(
        name="Unquoted tag in Array",
        original="""
        ---
        tags: ["#tag-a", #tag-b]
        ---
        # Note
        """,
    ),
    FixCase(
        name="Duplicate key in header",
        original="""
        ---
        key1: foo
        key1: bar
        ---
        """,
    ),
    FixCase(
        name="Uncloased header",
        original="""
        ---
        """,
    ),
]
