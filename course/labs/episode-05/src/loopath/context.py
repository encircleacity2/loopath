from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ContextConfig:
    strategy: str = "minimal"
    max_chars: int = 8000


class ContextBuilder:
    """The harness's viewfinder: it decides what the model actually sees."""

    def __init__(self, workspace: Path, config: ContextConfig):
        self.workspace = workspace
        self.config = config

    def build(self, task: str, history: list[str]) -> str:
        if self.config.strategy == "minimal":
            return self._minimal(task, history)
        if self.config.strategy == "repo_map":
            return self._repo_map(task, history)
        raise ValueError(f"Unknown context strategy: {self.config.strategy}")

    def _minimal(self, task: str, history: list[str]) -> str:
        return f"Task:\n{task}\n\nHistory:\n" + "\n".join(history)

    def _repo_map(self, task: str, history: list[str]) -> str:
        files = []
        for path in self.workspace.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                files.append(str(path.relative_to(self.workspace)))
        body = [
            f"Task:\n{task}",
            "Repository files:",
            "\n".join(f"- {file}" for file in sorted(files)),
            "History:",
            "\n".join(history),
        ]
        return self._truncate("\n\n".join(body))

    def _truncate(self, text: str) -> str:
        if len(text) <= self.config.max_chars:
            return text
        # Truncation must be explicit so the model knows content was cut.
        return text[: self.config.max_chars] + "\n\n[TRUNCATED]"
