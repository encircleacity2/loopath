from pydantic import BaseModel

from loopath.actions import RunCommandAction


class PolicyDecision(BaseModel):
    allowed: bool
    reason: str
    requires_approval: bool = False


# Teaching-grade denylist. A real system would combine this with a sandbox and
# an allowlist; substring matching is intentionally simple here.
DANGEROUS_PATTERNS = [
    "rm -rf",
    "curl | sh",
    "cat ~/.ssh",
    "printenv",
    "env",
]


def check_command(command: str) -> PolicyDecision:
    lowered = command.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in lowered:
            return PolicyDecision(allowed=False, reason=f"Blocked dangerous command: {pattern}")
    return PolicyDecision(allowed=True, reason="Command allowed")


class Policy:
    def check(self, action) -> PolicyDecision:
        if isinstance(action, RunCommandAction):
            return check_command(action.command)
        return PolicyDecision(allowed=True, reason="No policy rule blocked this action")
