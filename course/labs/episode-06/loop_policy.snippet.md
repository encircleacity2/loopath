# Episode 6 integration — wire Policy into AgentLoop

This is an **edit to `src/loopath/loop.py`**, not a new file. Give `AgentLoop` a
`policy` (e.g. `def __init__(self, model, tools, policy=None, max_steps=10)`),
import `ToolResult` from `loopath.tools`, and check the policy **before**
executing a tool. Replace:

```python
result = self.tools.execute(action)
```

with:

```python
decision = self.policy.check(action) if self.policy else None
if decision and not decision.allowed:
    result = ToolResult(ok=False, error=decision.reason, metadata={"policy_blocked": True})
else:
    result = self.tools.execute(action)
```

**Key idea:** a policy block is *not* a crash. It becomes a normal `ToolResult`
observation (tagged `policy_blocked`) that goes into the trace and back into
context, so the agent can choose a safe alternative instead of stopping.

**Verify (prompt injection demo):** with the workspace at
`demo_repos/prompt_injection`, a task of "Summarize the README" should let the
agent read the README but block any `env` command — and the block should show up
in the trace.
