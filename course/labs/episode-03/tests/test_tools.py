from pathlib import Path

import pytest

from loopath.tools import (
    edit_file,
    read_file,
    resolve_workspace_path,
    run_command,
    search,
)


def test_read_file_in_workspace(tmp_path: Path):
    (tmp_path / "app.py").write_text("print('hi')")
    result = read_file(tmp_path, "app.py")
    assert result.ok
    assert "hi" in result.output


def test_path_escape_is_blocked(tmp_path: Path):
    with pytest.raises(ValueError):
        resolve_workspace_path(tmp_path, "../../etc/passwd")


def test_search_returns_line_numbers(tmp_path: Path):
    (tmp_path / "app.py").write_text("a\nfind me\nb")
    result = search(tmp_path, "find me")
    assert result.ok
    assert ":2:" in result.output


def test_run_command_failure_has_exit_code(tmp_path: Path):
    result = run_command(tmp_path, "exit 3")
    assert not result.ok
    assert result.metadata["exit_code"] == 3


def test_edit_file_writes(tmp_path: Path):
    result = edit_file(tmp_path, "new.txt", "hello")
    assert result.ok
    assert (tmp_path / "new.txt").read_text() == "hello"
