from __future__ import annotations

from pydantic import BaseModel

from loopath.evals import EvalResult


class ExperimentVariant(BaseModel):
    name: str
    prompt_file: str
    context_strategy: str
    max_steps: int = 10


class ExperimentResult(BaseModel):
    variant: str
    results: list[EvalResult]

    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.success) / len(self.results)

    @property
    def avg_steps(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.steps for r in self.results) / len(self.results)


VARIANTS = [
    ExperimentVariant(name="baseline", prompt_file="prompts/baseline.md", context_strategy="minimal"),
    ExperimentVariant(name="strict_tools", prompt_file="prompts/strict_tool_use.md", context_strategy="repo_map"),
    ExperimentVariant(name="planner", prompt_file="prompts/planner.md", context_strategy="repo_map"),
]


def render_experiment_report(results: list[ExperimentResult]) -> str:
    lines = [
        "# Loop Engineering Experiment Report",
        "",
        "| Variant | Success Rate | Avg Steps | Failed Tasks |",
        "|---|---:|---:|---|",
    ]
    for result in results:
        failed = [r.task_id for r in result.results if not r.success]
        lines.append(
            f"| {result.variant} | {result.success_rate:.0%} | {result.avg_steps:.1f} | {', '.join(failed)} |"
        )
    return "\n".join(lines)
