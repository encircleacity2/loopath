from __future__ import annotations

from pydantic import BaseModel

from loopath.tracing import Trace


class ReviewResult(BaseModel):
    approved: bool
    severity: str = "info"
    reason: str
    requested_action: str | None = None


def summarize_trace_for_review(trace: Trace) -> str:
    edited_files = []
    ran_tests = False
    policy_blocks = 0

    for step in trace.steps:
        action_type = step.action.get("type")
        if action_type == "edit_file":
            edited_files.append(step.action.get("path", "unknown"))
        if action_type == "run_command" and "pytest" in step.action.get("command", ""):
            ran_tests = True
        if step.result.get("metadata", {}).get("policy_blocked"):
            policy_blocks += 1

    return (
        f"Edited files: {edited_files}\n"
        f"Ran tests: {ran_tests}\n"
        f"Policy blocks: {policy_blocks}\n"
        f"Steps: {len(trace.steps)}"
    )


class RuleBasedReviewer:
    """A testable, explainable baseline. It enforces invariants from an
    independent angle and never edits code itself."""

    def review(self, trace: Trace) -> ReviewResult:
        summary = summarize_trace_for_review(trace)
        edited = "Edited files: []" not in summary
        ran_tests = "Ran tests: True" in summary

        if edited and not ran_tests:
            return ReviewResult(
                approved=False,
                severity="medium",
                reason="The agent edited files but did not run tests.",
                requested_action="run_tests",
            )

        return ReviewResult(approved=True, reason="Basic reviewer checks passed.")
