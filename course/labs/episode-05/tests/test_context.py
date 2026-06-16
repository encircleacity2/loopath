from pathlib import Path

from loopath.context import ContextBuilder, ContextConfig


def test_strategies_differ(tmp_path: Path):
    (tmp_path / "app.py").write_text("x")
    minimal = ContextBuilder(tmp_path, ContextConfig(strategy="minimal")).build("t", [])
    repo_map = ContextBuilder(tmp_path, ContextConfig(strategy="repo_map")).build("t", [])
    assert minimal != repo_map


def test_repo_map_lists_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("x")
    ctx = ContextBuilder(tmp_path, ContextConfig(strategy="repo_map")).build("t", [])
    assert "app.py" in ctx


def test_over_budget_is_truncated(tmp_path: Path):
    for i in range(50):
        (tmp_path / f"file_{i}.py").write_text("x" * 200)
    ctx = ContextBuilder(
        tmp_path, ContextConfig(strategy="repo_map", max_chars=200)
    ).build("t", [])
    assert "[TRUNCATED]" in ctx
