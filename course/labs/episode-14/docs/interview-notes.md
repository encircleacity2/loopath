# Interview Notes

## Q: What is the core engineering judgment in this project?
Don't hide intelligence in a black-box prompt; split agent behavior into
verifiable runtime components (action schema, tool registry, policy, context
builder, trace logger, evaluator). When the agent fails, the trace localizes
whether it was a context, tool, policy, or decision problem.

## Q: Loop engineering vs prompt engineering?
Prompt engineering tweaks input and hopes. Loop engineering builds a feedback
loop: define evals, run, collect traces, analyze failures, change
prompt/context/tool/policy, rerun evals. The point is a system that improves
provably from data.

## Q: If real users used this, what would you add first?
Stricter sandbox + approval, real diff/patch instead of full overwrite, and a
richer eval set — because users care most about not breaking things,
reviewability, and explainable failures.

## Q: Why does edit_file use full overwrite?
A first-stage teaching tradeoff to focus on loop/policy/trace/eval; the real
version would switch to diff/patch for review, conflict handling, and minimal
edits.

## Q: Why is FakeModel meaningful?
It makes the runtime deterministic so model randomness can't mask loop/tool/policy
bugs.
