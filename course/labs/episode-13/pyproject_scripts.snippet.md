# Episode 13 integration — register the CLI entry point

Add to `pyproject.toml`:

```toml
[project.scripts]
loopath = "loopath.cli:main"
```

Then `loopath run "..."` and `loopath eval` become product surfaces over the
core loop. Smoke-test with:

```bash
loopath run "demo" --workspace demo_repos/todo_bug
loopath eval --tasks evals/tasks.jsonl
```
