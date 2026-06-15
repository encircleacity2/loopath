#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


REQUIRED_PATHS = [
    "README.md",
    "AGENTS.md",
    "pyproject.toml",
    "docs/architecture.md",
    "src/loopath/__init__.py",
    "tests",
    "demo_repos",
    "prompts",
    "evals",
    "traces",
]

CONTENT_CHECKS = [
    ("README.md", "structured model actions"),
    ("README.md", "loop engineering"),
    ("docs/architecture.md", "The model does not directly mutate the world"),
    ("AGENTS.md", "Never bypass policy checks"),
    ("AGENTS.md", "Trace every agent step"),
]


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text()


def verify(repo: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    repo = repo.resolve()

    for relative in REQUIRED_PATHS:
        path = repo / relative
        results.append(
            CheckResult(
                name=f"path:{relative}",
                passed=path.exists(),
                detail="exists" if path.exists() else f"missing {relative}",
            )
        )

    for relative, needle in CONTENT_CHECKS:
        path = repo / relative
        if not path.exists():
            results.append(
                CheckResult(
                    name=f"content:{relative}:{needle}",
                    passed=False,
                    detail=f"cannot check content because {relative} is missing",
                )
            )
            continue

        content = read_text(path)
        results.append(
            CheckResult(
                name=f"content:{relative}:{needle}",
                passed=needle in content,
                detail=f"found {needle!r}" if needle in content else f"missing {needle!r}",
            )
        )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Loopath Lab 1.")
    parser.add_argument("--repo", default=".", help="Path to the student's Loopath repo.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    repo = Path(args.repo)
    results = verify(repo)
    passed = all(result.passed for result in results)

    if args.json:
        print(
            json.dumps(
                {
                    "passed": passed,
                    "score": sum(1 for result in results if result.passed),
                    "total": len(results),
                    "checks": [result.__dict__ for result in results],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if passed else 1

    for result in results:
        marker = "ok" if result.passed else "missing"
        print(f"[{marker}] {result.name} - {result.detail}")

    if passed:
        print("Lab 1 verification passed")
        return 0

    print("Lab 1 verification failed")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

