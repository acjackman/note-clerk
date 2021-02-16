"""Defines the application container for the console app."""

import logging
from pathlib import Path

from . import checks
from .linting import LintChecks

log = logging.getLogger(__name__)


class App:
    """Application container for note-clerk."""

    def __init__(self, config_dir: str = None) -> None:  # noqa: ANN101
        """Initialize with config directory."""
        self.config_dir = Path(config_dir or ".").expanduser()
        log.info(f'Note Clerk using config dir: "{self.config_dir}"')
        self.notes_dir = self.config_dir

    @property
    def lint_checks(self) -> LintChecks:
        """List of checks the app is configured for."""
        log.debug("getting configured checks")
        return [
            checks.CheckHeaderTagsArray,
            checks.CheckHeaderTagsQuoted,
        ]
