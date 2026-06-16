from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from loopath.tools import run_command


class EvalTask(BaseModel):
    id: str
    repo: str
    prompt: str
    verify: str
    expected_files_changed: list[str] = Field(default_factory=list)


def load_eval_tasks(path: Path) -> list[EvalTask]:
    tasks = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        tasks.append(EvalTask.model_validate(json.loads(line)))
    return tasks


class EvalResult(BaseModel):
    task_id: str
    success: bool
    steps: int
    verifier_passed: bool
    trace_path: str | None = None
    error: str | None = None
    metrics: dict = Field(default_factory=dict)


def verify_task(workspace: Path, verify: str) -> tuple[bool, str]:
    if verify == "pytest":
        result = run_command(workspace, "pytest")
        return result.ok, result.output + "\n" + (result.error or "")

    if verify.startswith("contains:"):
        _, file_path, expected = verify.split(":", 2)
        target = workspace / file_path
        if not target.exists():
            return False, f"{file_path} does not exist"
        text = target.read_text()
        return expected in text, f"Expected substring: {expected}"

    if verify.startswith("policy:"):
        # Teaching version: actual policy metrics are read from the trace later.
        return True, "Policy verifier is trace-based"

    return False, f"Unknown verifier: {verify}"


class EvalRunner:
    def __init__(self, make_agent_loop):
        # make_agent_loop(workspace) -> AgentLoop, so the runner stays decoupled
        # from any particular model/context/policy configuration.
        self.make_agent_loop = make_agent_loop

    def run_task(self, task: EvalTask) -> EvalResult:
        workspace = Path(task.repo).resolve()
        loop = self.make_agent_loop(workspace)
        run = loop.run(task.prompt)
        verifier_passed, verifier_output = verify_task(workspace, task.verify)

        return EvalResult(
            task_id=task.id,
            success=run.success and verifier_passed,
            steps=len(run.trace.steps),
            verifier_passed=verifier_passed,
            trace_path=None,
            error=None if verifier_passed else verifier_output,
        )

    def run_all(self, tasks: list[EvalTask]) -> list[EvalResult]:
        return [self.run_task(task) for task in tasks]


def summarize_results(results: list[EvalResult]) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.success)
    avg_steps = sum(r.steps for r in results) / total if total else 0
    lines = [
        "# Eval Summary",
        "",
        f"- Total: {total}",
        f"- Passed: {passed}",
        f"- Success rate: {passed / total:.0%}" if total else "- Success rate: n/a",
        f"- Avg steps: {avg_steps:.1f}",
        "",
        "| Task | Success | Steps | Error |",
        "|---|---:|---:|---|",
    ]
    for r in results:
        lines.append(f"| {r.task_id} | {r.success} | {r.steps} | {r.error or ''} |")
    return "\n".join(lines)
