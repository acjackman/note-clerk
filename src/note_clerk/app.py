"""Defines the application container for the console app."""

import logging
from pathlib import Path


log = logging.getLogger(__name__)


class App:
    """Application container for note-clerk."""

    def __init__(self, config_dir: str = None) -> None:  # noqa: ANN101
        """Initialize with config directory."""
        self.config_dir = Path(config_dir or ".").expanduser()
        log.info(f'Note Clerk using config dir: "{self.config_dir}"')
