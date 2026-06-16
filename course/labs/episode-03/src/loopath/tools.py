from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from loopath.actions import (
    EditFileAction,
    ReadFileAction,
    RunCommandAction,
    SearchAction,
)


class ToolResult(BaseModel):
    ok: bool
    output: str = ""
    error: str | None = None
    metadata: dict = Field(default_factory=dict)


def resolve_workspace_path(workspace: Path, path: str) -> Path:
    """Resolve `path` inside `workspace`, refusing anything that escapes it.

    The model's path is untrusted input (e.g. ``../../.ssh/id_rsa``), so every
    file tool must route through this single resolver.
    """
    root = workspace.resolve()
    target = (root / path).resolve()
    if root != target and root not in target.parents:
        raise ValueError(f"Path escapes workspace: {path}")
    return target


def read_file(workspace: Path, path: str) -> ToolResult:
    try:
        target = resolve_workspace_path(workspace, path)
        if not target.exists():
            return ToolResult(ok=False, error=f"File not found: {path}")
        if not target.is_file():
            return ToolResult(ok=False, error=f"Not a file: {path}")
        return ToolResult(ok=True, output=target.read_text())
    except Exception as exc:
        return ToolResult(ok=False, error=str(exc))


def search(workspace: Path, query: str, path: str | None = None) -> ToolResult:
    try:
        base = resolve_workspace_path(workspace, path or ".")
        matches: list[str] = []
        files = [base] if base.is_file() else base.rglob("*")
        for file in files:
            if not file.is_file():
                continue
            if ".git" in file.parts:
                continue
            try:
                text = file.read_text()
            except UnicodeDecodeError:
                continue
            for i, line in enumerate(text.splitlines(), start=1):
                if query in line:
                    rel = file.relative_to(workspace.resolve())
                    matches.append(f"{rel}:{i}: {line}")
        return ToolResult(ok=True, output="\n".join(matches), metadata={"matches": len(matches)})
    except Exception as exc:
        return ToolResult(ok=False, error=str(exc))


def run_command(workspace: Path, command: str, timeout: int = 20) -> ToolResult:
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return ToolResult(
            ok=completed.returncode == 0,
            output=completed.stdout,
            error=completed.stderr if completed.returncode != 0 else None,
            metadata={"exit_code": completed.returncode},
        )
    except subprocess.TimeoutExpired:
        return ToolResult(ok=False, error=f"Command timed out after {timeout}s")


def edit_file(workspace: Path, path: str, content: str) -> ToolResult:
    try:
        target = resolve_workspace_path(workspace, path)
        before = target.read_text() if target.exists() else ""
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return ToolResult(
            ok=True,
            output=f"Wrote {path}",
            metadata={"before_chars": len(before), "after_chars": len(content)},
        )
    except Exception as exc:
        return ToolResult(ok=False, error=str(exc))


class ToolRegistry:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def execute(self, action) -> ToolResult:
        if isinstance(action, ReadFileAction):
            return read_file(self.workspace, action.path)
        if isinstance(action, SearchAction):
            return search(self.workspace, action.query, action.path)
        if isinstance(action, RunCommandAction):
            return run_command(self.workspace, action.command)
        if isinstance(action, EditFileAction):
            return edit_file(self.workspace, action.path, action.content)
        return ToolResult(ok=False, error=f"No tool for action type: {action.type}")

    def final_result(self, message: str) -> ToolResult:
        # final_answer carries no real tool side effect, but it is still recorded
        # as a result so the last step is auditable in the trace.
        return ToolResult(ok=True, output=message)
