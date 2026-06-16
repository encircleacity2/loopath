# Loopath MCP Design

MCP tools expose **user-intent capabilities**, not internal functions.
Do NOT expose internals like `parse_action`, `resolve_workspace_path`, or
`_truncate` — they leak implementation, freeze refactoring, and widen the attack
surface.

## Tools

### Loopath.run_task
- Input: `task` (string), `repo_path` (string), `context_strategy` (string), `max_steps` (number)
- Output: `success` (boolean), `final_message` (string), `trace_id` (string)

### Loopath.run_eval
- Input: `eval_file` (string), `variant` (string)
- Output: `success_rate` (number), `report_path` (string)

### Loopath.get_trace
- Input: `trace_id` (string)
- Output: `trace_markdown` (string)

## AGENTS.md vs skill vs MCP

- **AGENTS.md** — durable rules *inside this repo* an agent should follow.
- **Skill** — a reusable, packaged workflow/instruction set.
- **MCP** — a standard protocol to expose tools and context to *external* systems.
