"""Test the utils."""
from pathlib import Path
from typing import Callable

import pytest

from note_clerk import _utils


@pytest.fixture
def file_factory(tmpdir) -> Callable:  # noqa: ANN001
    """Quickly make filies in the temp dir."""

    def factory(filename: str, content: str = "content") -> Path:
        path = Path(str(tmpdir)) / filename
        with open(path, "w") as f:
            f.write(content)

        return path

    return factory


class TestAllFiles:
    """Tests for all_files."""

    def test_empty_directory(self, tmpdir) -> None:  # noqa: ANN001, ANN101
        """Test empty directory."""
        tmp = Path(str(tmpdir))
        full_list = list(_utils._all_files((tmp,)))

        assert full_list == []

    # Testing the private function for coverage
    def test_directory_with_no_file(self, tmpdir) -> None:  # noqa: ANN001, ANN101
        """Test empty directory."""
        tmp = Path(str(tmpdir))
        full_list = list(_utils._all_files((tmp,)))

        assert full_list == []

    def test_with_single_file(
        self, tmpdir, file_factory  # noqa: ANN001, ANN101
    ) -> None:
        """Test empty directory."""
        f = file_factory("hello.txt")

        full_list = list(_utils._all_files((f,)))

        assert full_list == [f]

    # Testing the private function for coverage
    def test_directory_with_single_file(
        self, tmpdir, file_factory  # noqa: ANN001, ANN101
    ) -> None:
        """Test empty directory."""
        tmp = Path(str(tmpdir))
        f = file_factory("hello.txt")
        f2 = file_factory("test2.txt")

        full_list = list(_utils._all_files((tmp,)))

        assert set(full_list) == set([f, f2])
