"""Episode 9: the full trace. This supersedes the minimal tracing.py from
Episode 4 — it adds run_id, per-step context/policy/phase fields, JSON + Markdown
persistence, so a failed run becomes diagnosable instead of "the model failed"."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    step: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context_preview: str = ""
    context_chars: int = 0
    action: dict
    policy: dict | None = None
    result: dict
    phase: str = "normal"  # normal | repair | review


class Trace(BaseModel):
    run_id: str = Field(default_factory=lambda: uuid4().hex[:12])
    task: str
    context_strategy: str = "unknown"
    steps: list[TraceStep] = Field(default_factory=list)
    final: dict = Field(default_factory=dict)

    def add_step(self, step: int, action, result, **kwargs) -> None:
        self.steps.append(
            TraceStep(
                step=step,
                action=action.model_dump(),
                result=result.model_dump(),
                **kwargs,
            )
        )


def render_trace_markdown(trace: Trace) -> str:
    lines = [
        f"# Trace {trace.run_id}",
        "",
        f"- Task: {trace.task}",
        f"- Context strategy: {trace.context_strategy}",
        f"- Steps: {len(trace.steps)}",
        "",
    ]
    for step in trace.steps:
        lines.extend([
            f"## Step {step.step}",
            "",
            f"- Phase: {step.phase}",
            f"- Context chars: {step.context_chars}",
            f"- Action: `{step.action.get('type')}`",
            "",
            "### Action",
            "```json",
            json.dumps(step.action, indent=2, ensure_ascii=False),
            "```",
            "",
            "### Result",
            "```json",
            json.dumps(step.result, indent=2, ensure_ascii=False)[:2000],
            "```",
            "",
        ])
    return "\n".join(lines)


class TraceLogger:
    def __init__(self, trace_dir: Path):
        self.trace_dir = trace_dir
        self.trace_dir.mkdir(parents=True, exist_ok=True)

    def save_json(self, trace: Trace) -> Path:
        path = self.trace_dir / f"{trace.run_id}.json"
        path.write_text(json.dumps(trace.model_dump(), indent=2, ensure_ascii=False))
        return path

    def save_markdown(self, trace: Trace) -> Path:
        path = self.trace_dir / f"{trace.run_id}.md"
        path.write_text(render_trace_markdown(trace))
        return path
