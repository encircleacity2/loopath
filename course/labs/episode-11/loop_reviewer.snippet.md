# Episode 11 integration — review before final_answer

This is an **edit to `src/loopath/loop.py`**. Give `AgentLoop` an optional
`reviewer`. In the `final_answer` branch, review the trace **before** returning
success:

```python
if isinstance(action, FinalAnswerAction):
    review = self.reviewer.review(trace) if self.reviewer else None
    if review and not review.approved:
        # Teaching version: fail honestly instead of auto-repairing.
        trace.final = {"success": False, "review": review.model_dump()}
        return AgentRunResult(success=False, trace=trace, error=review.reason)
    fake_result = self.tools.final_result(action.message)
    trace.add_step(step, action, fake_result)
    return AgentRunResult(success=True, final_message=action.message, trace=trace)
```

**Why before, not after:** once the final answer reaches the user, reviewing is
too late. The reviewer enforces an invariant from an independent angle — it never
edits code; it returns `approved / reason / requested_action`.
