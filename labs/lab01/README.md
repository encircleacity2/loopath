# Lab 1 Verifier

Use this verifier to check a student's Lab 1 project skeleton.

From the course repo:

```bash
python3 labs/lab01/verify.py --repo /path/to/student/loopath
```

If the student's project is the current working directory:

```bash
python3 /path/to/course/labs/lab01/verify.py --repo .
```

Expected success output:

```text
Lab 1 verification passed
```

The verifier checks:

- required directories and files exist
- `README.md` explains the project purpose
- `docs/architecture.md` states that the model does not directly mutate the world
- `AGENTS.md` includes test, policy, and trace rules
