from __future__ import annotations

from pydantic import BaseModel

from loopath.actions import FinalAnswerAction
from loopath.tracing import Trace


class AgentRunResult(BaseModel):
    success: bool
    final_message: str | None = None
    trace: Trace
    error: str | None = None


class AgentLoop:
    def __init__(self, model, tools, max_steps: int = 10):
        self.model = model
        self.tools = tools
        self.max_steps = max_steps

    def run(self, task: str) -> AgentRunResult:
        trace = Trace(task=task)
        history: list[str] = []

        for step in range(1, self.max_steps + 1):
            context = self._build_simple_context(task, history)
            try:
                action = self.model.next_action(context)
            except Exception as exc:
                return AgentRunResult(success=False, trace=trace, error=str(exc))

            if isinstance(action, FinalAnswerAction):
                fake_result = self.tools.final_result(action.message)
                trace.add_step(step, action, fake_result)
                return AgentRunResult(success=True, final_message=action.message, trace=trace)

            result = self.tools.execute(action)
            trace.add_step(step, action, result)
            history.append(f"Action: {action.model_dump()} Result: {result.model_dump()}")

        return AgentRunResult(success=False, trace=trace, error="Max steps exceeded")

    def _build_simple_context(self, task: str, history: list[str]) -> str:
        return "Task:\n" + task + "\n\nHistory:\n" + "\n".join(history)
