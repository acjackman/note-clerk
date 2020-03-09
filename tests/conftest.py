"""Pytest configuration."""
from _pytest.config import Config


def pytest_configure(config: Config) -> None:
    """Configure pytest dynamically."""
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
    config.addinivalue_line("markers", "regression: mark as regression test.")
