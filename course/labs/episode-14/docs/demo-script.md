# 5-minute Demo Script

## 0:00 Problem
Modern coding agents are powerful, but reliability does not come from prompts
alone. I built a mini harness to show the runtime pieces behind a coding agent.

## 0:30 Architecture
The model proposes structured actions. The harness validates, executes, observes,
traces, and evaluates those actions.

## 1:30 Demo
Run a bugfix task and show the live steps.

## 2:30 Trace
Show every step: action, policy, result.

## 3:15 Policy block
Show one dangerous action blocked and recorded.

## 3:45 Eval
Compare context strategies (baseline vs repo_map).

## 4:15 Self-repair
Show a fail-then-pass repair trace.

## 4:30 Lessons
Most failures came from missing context and weak verification, not just model
capability.
