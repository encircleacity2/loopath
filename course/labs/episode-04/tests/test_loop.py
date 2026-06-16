from pathlib import Path

from loopath.actions import FinalAnswerAction, ReadFileAction
from loopath.loop import AgentLoop
from loopath.model import FakeModel
from loopath.tools import ToolRegistry


def test_agent_loop_reads_file_and_finishes(tmp_path: Path):
    (tmp_path / "app.py").write_text("print('hello')")
    model = FakeModel([
        ReadFileAction(type="read_file", path="app.py"),
        FinalAnswerAction(type="final_answer", message="Done"),
    ])
    tools = ToolRegistry(tmp_path)

    result = AgentLoop(model, tools).run("Read app.py")

    assert result.success
    assert result.final_message == "Done"
    assert len(result.trace.steps) == 2


def test_max_steps_terminates(tmp_path: Path):
    (tmp_path / "app.py").write_text("x")
    model = FakeModel([
        ReadFileAction(type="read_file", path="app.py") for _ in range(20)
    ])
    tools = ToolRegistry(tmp_path)

    result = AgentLoop(model, tools, max_steps=5).run("loop forever")

    assert not result.success
    assert result.error == "Max steps exceeded"
    assert len(result.trace.steps) == 5
