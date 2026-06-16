# Episode 12 integration — self-repair in the loop

Repair is **loop-level orchestration**, not a tool concern. Add these helpers
(e.g. in `loop.py`) and wire a *bounded* repair into `AgentLoop`.

```python
def is_test_failure(action, result) -> bool:
    return (
        action.type == "run_command"
        and "pytest" in action.command
        and not result.ok
    )


def summarize_test_failure(result, max_chars: int = 2000) -> str:
    text = (result.output or "") + "\n" + (result.error or "")
    # pytest's key failure (summary + assertion diff) is at the tail.
    return text[-max_chars:] if len(text) > max_chars else text


def build_repair_context(task: str, failure_summary: str, history: list[str]) -> str:
    return (
        f"Original task:\n{task}\n\n"
        "The latest test run failed. Only fix the specific failure. "
        "Do not rewrite unrelated files.\n\n"
        f"Failure summary:\n{failure_summary}\n\n"
        "Recent history:\n" + "\n".join(history[-5:]) + "\n\n"
        "Return exactly one structured action."
    )
```

Keep a budget so repair is never an infinite retry:

```python
repairs_used = 0
# ... inside the step loop, after recording a tool result ...
if is_test_failure(action, result) and repairs_used < self.max_repairs:
    repairs_used += 1
    failure_summary = summarize_test_failure(result)
    history.append(build_repair_context(task, failure_summary, history))
    # the next iteration's context now targets this specific failure
```

Mark repair steps with `phase="repair"` (TraceStep supports it as of Episode 9),
so a run reads: `pytest failed -> repair edit_file -> pytest passed`. Past
`max_repairs`, fail honestly and hand off to a human or reviewer.
