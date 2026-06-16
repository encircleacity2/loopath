# Loopath Architecture

## Core idea

The model does not directly mutate the world.
It proposes structured actions.
The harness validates, executes, observes, and records those actions.

## Modules

- ModelClient: produces the next action.
- Action schema: validates model output.
- ToolRegistry: executes allowed tools.
- Policy: blocks unsafe actions.
- ContextBuilder: decides what the model sees.
- AgentLoop: controls execution.
- TraceLogger: records what happened.
- Evaluator: measures performance.
