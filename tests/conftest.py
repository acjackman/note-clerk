"""Pytest configuration."""
from _pytest.config import Config
from click.testing import CliRunner
import pytest

from ._utils import file_factory


def pytest_configure(config: Config) -> None:
    """Configure pytest dynamically."""
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
    config.addinivalue_line("markers", "regression: mark as regression test.")


@pytest.fixture
def cli_runner() -> CliRunner:
    """Creates CliRunner instance."""
    return CliRunner()
