"""Entry point: run the eval set and print a summary table.

Wire `make_agent_loop` to your AgentLoop with whatever model / context / policy
configuration you want to evaluate, then:

    python evals/run_eval.py
"""
from pathlib import Path

from loopath.evals import EvalRunner, load_eval_tasks, summarize_results


def make_agent_loop(workspace: Path):
    # Example wiring (replace with the configuration you want to evaluate):
    #   from loopath.loop import AgentLoop
    #   from loopath.model import FakeModel
    #   from loopath.tools import ToolRegistry
    #   return AgentLoop(FakeModel([...]), ToolRegistry(workspace))
    raise NotImplementedError("Wire make_agent_loop to your AgentLoop configuration.")


def main() -> None:
    tasks = load_eval_tasks(Path("evals/tasks.jsonl"))
    results = EvalRunner(make_agent_loop).run_all(tasks)
    print(summarize_results(results))


if __name__ == "__main__":
    main()
