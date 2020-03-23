import pytest

from note_clerk.app import App
from note_clerk.linting import LintCheck


@pytest.fixture
def app() -> App:
    """App instance."""
    return App()


def test_lint_checks(app: App) -> None:
    """Test that lint_checks returns LintCheck instances."""
    checks = list(app.lint_checks)

    for check in checks:
        assert issubclass(check, LintCheck)
