class FakeModel:
    """A deterministic stand-in for a real model.

    It returns preset actions in order, so the loop's behavior is fully
    reproducible. This lets us prove the runtime works before model randomness
    can mask loop, tool, or policy bugs.
    """

    def __init__(self, actions):
        self.actions = list(actions)

    def next_action(self, context: str):
        if not self.actions:
            raise RuntimeError("FakeModel has no more actions")
        return self.actions.pop(0)
