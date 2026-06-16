"""Week 1 capstone: a controlled bugfix run driven by FakeModel.

This proves the *harness*, not model intelligence: every action is preset, but
each step is validated, executed, and recorded in a trace. Run it from the
project root after Episodes 1-6 are in place:

    python bugfix_demo.py
"""
from pathlib import Path

from loopath.actions import (
    EditFileAction,
    FinalAnswerAction,
    ReadFileAction,
    RunCommandAction,
)
from loopath.loop import AgentLoop
from loopath.model import FakeModel
from loopath.tools import ToolRegistry


def main() -> None:
    workspace = Path(__file__).parent / "demo_repos" / "todo_bug"
    model = FakeModel([
        ReadFileAction(type="read_file", path="tests/test_app.py"),
        ReadFileAction(type="read_file", path="app.py"),
        EditFileAction(
            type="edit_file",
            path="app.py",
            content="def add(a, b):\n    return a + b\n",
        ),
        RunCommandAction(type="run_command", command="pytest"),
        FinalAnswerAction(type="final_answer", message="Fixed add and tests pass."),
    ])
    result = AgentLoop(model, ToolRegistry(workspace)).run(
        "Fix the failing test in demo_repos/todo_bug"
    )
    print("success:", result.success)
    for step in result.trace.steps:
        print(f"step {step.step}: {step.action.get('type')}")


if __name__ == "__main__":
    main()
