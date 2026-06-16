"""The CLI is a product surface over the core loop — not the loop itself.

It is the window through which a user understands and drives the agent. Keep its
output readable; it is not random printing.
"""
import argparse
from pathlib import Path


def run_task(task: str, workspace: Path, context: str) -> None:
    print("Loopath")
    print(f"Task: {task}")
    print(f"Workspace: {workspace}")
    print(f"Context: {context}")
    # Wire to AgentLoop here, then print the result and the trace path.


def run_eval(tasks: Path) -> None:
    print(f"Running eval set: {tasks}")
    # Wire to EvalRunner here, then print the summary table.


def main() -> None:
    parser = argparse.ArgumentParser(prog="loopath")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("task")
    run_parser.add_argument("--workspace", default=".")
    run_parser.add_argument("--context", default="repo_map")

    eval_parser = subparsers.add_parser("eval")
    eval_parser.add_argument("--tasks", default="evals/tasks.jsonl")

    args = parser.parse_args()

    if args.command == "run":
        run_task(args.task, Path(args.workspace), args.context)
    elif args.command == "eval":
        run_eval(Path(args.tasks))


if __name__ == "__main__":
    main()
