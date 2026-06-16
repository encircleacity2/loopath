from pathlib import Path

from loopath.evals import load_eval_tasks, verify_task


def test_load_eval_tasks(tmp_path: Path):
    p = tmp_path / "tasks.jsonl"
    p.write_text('{"id":"a","repo":".","prompt":"x","verify":"pytest"}\n\n')
    tasks = load_eval_tasks(p)
    assert len(tasks) == 1
    assert tasks[0].id == "a"


def test_verify_contains(tmp_path: Path):
    (tmp_path / "README.md").write_text("run pip install foo")
    ok, _ = verify_task(tmp_path, "contains:README.md:pip install")
    assert ok


def test_verify_contains_missing_file(tmp_path: Path):
    ok, _ = verify_task(tmp_path, "contains:README.md:pip install")
    assert not ok


def test_unknown_verifier(tmp_path: Path):
    ok, _ = verify_task(tmp_path, "wat")
    assert not ok
