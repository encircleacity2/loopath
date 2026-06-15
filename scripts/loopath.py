#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Step:
    title: dict[str, str]
    background: dict[str, str]
    purpose: dict[str, str]
    why: dict[str, str]
    video: str


STEPS: list[Step] = [
    Step(
        {"zh": "Loopath 是什么", "en": "What Loopath Is"},
        {
            "zh": "很多人会使用 Codex、Claude Code 或 Cursor，但并不清楚这些工具背后的 agent loop 是如何被约束和验证的。",
            "en": "Many people use Codex, Claude Code, or Cursor without seeing the agent loop that constrains and verifies the work.",
        },
        {
            "zh": "把 Loopath 定位成一个小而完整的 loop engineering 参考实现。",
            "en": "Frame Loopath as a small reference for loop engineering.",
        },
        {
            "zh": "先定义项目定位，后面的 README、AGENTS.md、architecture、lab 和 verifier 才会服务同一个目标。",
            "en": "A clear frame keeps README, AGENTS.md, architecture, labs, and verification aligned.",
        },
        "media/intro/loopath-intro.mp4",
    ),
    Step(
        {"zh": "最终会构建什么", "en": "What You Will Build"},
        {
            "zh": "API 调用只能得到模型输出，不能自动形成一个可审查、可追踪、可评测的行动系统。",
            "en": "An API call returns model output, but not an auditable, traceable, evaluable action system.",
        },
        {
            "zh": "理解最终系统能力：context -> action -> policy -> tool -> observation -> trace -> eval。",
            "en": "Understand the target system: context -> action -> policy -> tool -> observation -> trace -> eval.",
        },
        {
            "zh": "先看终局，才能知道第一节课为什么先搭边界，而不是直接写 action parser。",
            "en": "Seeing the end state explains why Episode 1 starts with boundaries instead of an action parser.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "Harness 不是 API Wrapper", "en": "A Harness Is Not an API Wrapper"},
        {
            "zh": "Wrapper 只处理文本输入输出；harness 处理真实行动、权限、观察和评测。",
            "en": "A wrapper handles text input and output; a harness handles action, permission, observation, and evaluation.",
        },
        {
            "zh": "区分 model wrapper 和 agent runtime。",
            "en": "Separate a model wrapper from an agent runtime.",
        },
        {
            "zh": "这个区别决定后续模块是否需要 policy、trace 和 eval。",
            "en": "This distinction determines why policy, trace, and eval must exist.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "四层边界", "en": "Four Boundaries"},
        {
            "zh": "Model、Agent、Harness、World 混在一起时，失败很难定位。",
            "en": "When Model, Agent, Harness, and World are mixed together, failures are hard to diagnose.",
        },
        {
            "zh": "建立模型负责想、harness 负责执行边界的心智模型。",
            "en": "Build the mental model: the model proposes; the harness controls execution.",
        },
        {
            "zh": "模型不应该直接修改世界，它应该提出结构化 action。",
            "en": "The model should not directly mutate the world; it should propose structured actions.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "Lab 1 目标", "en": "Lab 1 Target"},
        {
            "zh": "第一节课的产物不是模型能力，而是后续所有 lab 的工程边界。",
            "en": "Episode 1 produces engineering boundaries, not model capability.",
        },
        {
            "zh": "创建项目骨架、README、AGENTS.md、architecture.md、pyproject.toml。",
            "en": "Create the project skeleton, README, AGENTS.md, architecture.md, and pyproject.toml.",
        },
        {
            "zh": "先有稳定结构，agent 才能在后续对话中安全继续创建文件和修改代码。",
            "en": "A stable structure lets the agent safely continue creating files and code in later steps.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "创建目录结构", "en": "Create the Directory Structure"},
        {
            "zh": "传统课程让学生手敲命令；Loopath skill 会让 agent 直接创建 lab 项目。",
            "en": "Traditional courses ask students to type commands; the Loopath skill lets the agent create the lab project.",
        },
        {
            "zh": "理解每个目录为什么存在：src、tests、demo_repos、prompts、evals、traces、docs。",
            "en": "Understand why each directory exists: src, tests, demo_repos, prompts, evals, traces, docs.",
        },
        {
            "zh": "目录本身就是 harness 设计的一部分：代码、评测、trace、文档从第一天就分层。",
            "en": "The directory structure is part of the harness design: code, evals, traces, and docs are separated from day one.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "README 是产品承诺", "en": "README as Product Promise"},
        {
            "zh": "README 不只是说明文件，它决定读者和 agent 如何理解项目目标。",
            "en": "README is not just documentation; it shapes how humans and agents understand the project goal.",
        },
        {
            "zh": "写清楚 Loopath 是 tiny reference implementation，不是完整 agent framework。",
            "en": "State that Loopath is a tiny reference implementation, not a full agent framework.",
        },
        {
            "zh": "边界越清楚，后续 agent 越不容易把项目做歪。",
            "en": "Clear boundaries reduce the chance that future agents take the project in the wrong direction.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "Architecture 写核心约束", "en": "Architecture as Core Constraints"},
        {
            "zh": "直接写 action parser 会只解决局部问题，architecture 先定义完整运行路径。",
            "en": "Jumping into an action parser solves a local problem; architecture defines the whole runtime path first.",
        },
        {
            "zh": "写下最重要约束：model does not directly mutate the world。",
            "en": "Write the key constraint: the model does not directly mutate the world.",
        },
        {
            "zh": "这句话决定后续 action schema、policy、tool、trace、eval 的存在理由。",
            "en": "That sentence explains why action schema, policy, tools, traces, and evals exist.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "画出 Core Loop", "en": "Draw the Core Loop"},
        {
            "zh": "Agent 不是一次性回答，而是在观察结果后决定下一步。",
            "en": "An agent is not a one-shot answer; it decides the next step after observing results.",
        },
        {
            "zh": "把 context、action、policy、tool、observation、trace、eval 画成闭环。",
            "en": "Draw context, action, policy, tool, observation, trace, and eval as a loop.",
        },
        {
            "zh": "图可以让后续每个模块都知道自己处在 loop 的哪个位置。",
            "en": "The diagram tells every later module where it sits in the loop.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "AGENTS.md 是场景工作协议", "en": "AGENTS.md as Scenario Protocol"},
        {
            "zh": "AGENTS.md 不只用于代码开发，它把日常生产力场景里的隐性规则显性化。",
            "en": "AGENTS.md is not only for coding; it makes implicit working rules explicit for productivity scenarios.",
        },
        {
            "zh": "定义 Goal、Can do、Must not do、Done when。",
            "en": "Define Goal, Can do, Must not do, and Done when.",
        },
        {
            "zh": "没有 AGENTS.md，agent 每次都靠当前 prompt 猜你的偏好和边界。",
            "en": "Without AGENTS.md, the agent has to infer your preferences and boundaries from the current prompt.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "pyproject.toml", "en": "pyproject.toml"},
        {
            "zh": "Python 项目需要一个统一配置入口，声明项目名、版本、依赖、测试配置和 CLI。",
            "en": "A Python project needs one configuration entry point for name, version, dependencies, tests, and CLI.",
        },
        {
            "zh": "先写最小 pyproject，不引入复杂依赖。",
            "en": "Start with a minimal pyproject without unnecessary dependencies.",
        },
        {
            "zh": "越早建立项目身份，后续越容易安装、测试和验证。",
            "en": "A clear project identity makes later installation, testing, and verification easier.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "Verifier 自动验收", "en": "Automated Verification"},
        {
            "zh": "正式课程体验不应该让用户复制大段命令，而应该由 agent 自动运行 verifier。",
            "en": "A real course should not ask users to copy long commands; the agent should run the verifier.",
        },
        {
            "zh": "运行 Lab 1 verifier，输出检测卡片。",
            "en": "Run the Lab 1 verifier and render a result card.",
        },
        {
            "zh": "verification 是 loop engineering 的关键：没有自动验收，就无法稳定改进。",
            "en": "Verification is central to loop engineering: without it, improvement cannot be stable.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "Agent Rubric 检查", "en": "Agent Rubric Review"},
        {
            "zh": "脚本检查结构和关键词，agent rubric 检查解释质量和设计取舍。",
            "en": "Scripts check structure and required text; an agent rubric checks explanation quality and design tradeoffs.",
        },
        {
            "zh": "让 agent 返回 score、evidence、missing requirements、next improvement。",
            "en": "Ask the agent to return score, evidence, missing requirements, and one next improvement.",
        },
        {
            "zh": "脚本和 agent 评分结合，可以同时覆盖确定性和开放性学习目标。",
            "en": "Combining scripts and agent grading covers both deterministic and open-ended learning goals.",
        },
        "media/loopath-episode-01.mp4",
    ),
    Step(
        {"zh": "Quiz 一问一答", "en": "One-question-at-a-time Quiz"},
        {
            "zh": "一次展示太多题会打断学习节奏。",
            "en": "Showing too many questions at once breaks the learning rhythm.",
        },
        {
            "zh": "每次只问一题，用户回答后给参考答案和评分。",
            "en": "Ask one question at a time, then provide the reference answer and score.",
        },
        {
            "zh": "这让 quiz 像 tutor，而不是静态练习册。",
            "en": "This makes quiz feel like tutoring, not a static worksheet.",
        },
        "media/loopath-episode-01.mp4",
    ),
]


QUIZ = {
    1: {
        "type": "multiple_choice",
        "question": {
            "zh": "Harness 和 API wrapper 最大区别是什么？",
            "en": "What is the biggest difference between a harness and an API wrapper?",
        },
        "choices": {
            "zh": [
                "A. Harness 会把 prompt 写得更长。",
                "B. Harness 负责 action、tool、policy、trace、eval 等运行时边界。",
                "C. Harness 只能用于本地模型。",
                "D. Harness 不需要测试。",
            ],
            "en": [
                "A. A harness makes prompts longer.",
                "B. A harness owns runtime boundaries such as actions, tools, policy, traces, and evals.",
                "C. A harness only works with local models.",
                "D. A harness does not need tests.",
            ],
        },
        "answer": "B",
        "reference": {
            "zh": "正确答案是 B。Wrapper 处理模型输入输出；harness 处理动作协议、工具执行、权限边界、trace 和 eval。",
            "en": "The correct answer is B. A wrapper handles model input/output; a harness handles action protocols, tool execution, permission boundaries, traces, and evals.",
        },
    },
    2: {
        "type": "short_answer",
        "question": {
            "zh": "为什么第一课先写 README、AGENTS.md 和 architecture.md，而不是直接写 action parser？",
            "en": "Why does Episode 1 start with README, AGENTS.md, and architecture.md instead of an action parser?",
        },
        "reference": {
            "zh": "因为 action parser 只解决模型输出到动作的局部问题。README 定义项目目标，AGENTS.md 定义场景工作协议和 done criteria，architecture.md 定义从用户输入到 context、action、policy、tool、observation、trace、eval 的完整边界。先有边界，parser 才知道服务于什么系统。",
            "en": "Because an action parser only solves the local problem of turning model output into actions. README defines the project goal, AGENTS.md defines the scenario protocol and done criteria, and architecture.md defines the full boundary from user input to context, action, policy, tool, observation, trace, and eval. Boundaries should come before parser implementation.",
        },
        "keywords": ["README", "AGENTS", "architecture", "boundary", "policy", "trace", "eval", "context", "action"],
    },
    3: {
        "type": "short_answer",
        "question": {
            "zh": "为什么 AGENTS.md 是 harness 工程的一部分？",
            "en": "Why is AGENTS.md part of harness engineering?",
        },
        "reference": {
            "zh": "因为它把人的偏好、场景边界、可做/不可做、完成标准写成 agent 可以稳定读取的规则。它不是代码里的 policy，但会影响 context、tool use、done criteria 和 agent 的行为边界。",
            "en": "Because it turns human preferences, scenario boundaries, allowed/disallowed actions, and done criteria into rules an agent can reliably read. It is not code-level policy, but it shapes context, tool use, done criteria, and behavioral boundaries.",
        },
        "keywords": ["AGENTS", "boundary", "done", "policy", "context", "tool", "rules", "scenario"],
    },
}


def normalize_lang(lang: str | None, text: str = "") -> str:
    if lang in {"zh", "en"}:
        return lang
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    ascii_letters = sum(1 for ch in text if ch.isascii() and ch.isalpha())
    return "zh" if cjk >= max(2, ascii_letters // 4) else "en"


def t(value: dict[str, str], lang: str) -> str:
    return value.get(lang) or value["en"]


def card(title: str, body: list[str]) -> str:
    lines = [f"> **{title}**", ">"]
    lines.extend(f"> {line}" if line else ">" for line in body)
    return "\n".join(lines)


def start(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang, args.text or "")
    if lang == "zh":
        print(card("Loopath 互动课程", [
            "默认语言：中文",
            "学习方式：每次一个小课题。你可以随时提问、继续下一节、开始 lab、跑 verification 或进入 quiz。",
            "",
            "建议从 Episode 1 / Step 1 开始：",
            "`python3 scripts/loopath.py step --episode 1 --step 1 --lang zh`",
        ]))
    else:
        print(card("Loopath Interactive Course", [
            "Default language: English",
            "Learning mode: one small topic at a time. You can ask questions, continue, start the lab, run verification, or take the quiz.",
            "",
            "Recommended start: Episode 1 / Step 1:",
            "`python3 scripts/loopath.py step --episode 1 --step 1 --lang en`",
        ]))
    return 0


def render_step(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    if args.episode != 1:
        raise SystemExit("Only Episode 1 is implemented in the interactive skill v1.")
    if args.step < 1 or args.step > len(STEPS):
        raise SystemExit(f"Step must be between 1 and {len(STEPS)}.")
    step = STEPS[args.step - 1]
    clip_path = f"media/episode-01/clips/{lang}/step-{args.step:02d}.mp4"
    video_path = clip_path if (ROOT / clip_path).exists() else step.video
    next_cmd = (
        f"`python3 scripts/loopath.py step --episode 1 --step {args.step + 1} --lang {lang}`"
        if args.step < len(STEPS)
        else "`python3 scripts/loopath.py quiz --episode 1 --question 1 --lang {}`".format(lang)
    )
    labels = {
        "zh": ("背景", "目的", "为什么重要", "视频", "下一步", "继续下一小节、提问、开始 lab、跑 verification，或进入 quiz。"),
        "en": ("Background", "Purpose", "Why it matters", "Video", "Next", "Continue to the next step, ask a question, start the lab, run verification, or take the quiz."),
    }[lang]
    print(card(f"Episode 1 / Step {args.step}: {t(step.title, lang)}", [
        f"**{labels[0]}**：{t(step.background, lang)}",
        f"**{labels[1]}**：{t(step.purpose, lang)}",
        f"**{labels[2]}**：{t(step.why, lang)}",
        f"**{labels[3]}**：`{video_path}`",
        "",
        f"**{labels[4]}**：{labels[5]}",
        next_cmd,
    ]))
    return 0


def safe_write(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def lab_create(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    repo = Path(args.repo).expanduser().resolve()
    overwrite = args.overwrite
    dirs = [
        "src/loopath",
        "tests",
        "demo_repos",
        "prompts",
        "evals",
        "traces",
        "docs",
    ]
    for directory in dirs:
        (repo / directory).mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[str] = []
    files = {
        "README.md": "# Loopath\n\nLoopath is a teaching project for building a mini Codex-style coding agent runtime from scratch.\n\nIt demonstrates:\n\n- structured model actions\n- tool execution\n- policy checks\n- agent loop\n- tracing\n- evals\n- loop engineering\n\nThis project is intentionally small, inspectable, and designed for learning.\n",
        "AGENTS.md": "# AGENTS.md\n\n## Project goal\n\nThis repo teaches how to build a mini coding-agent harness from scratch.\n\n## Commands\n\n- Run tests with `pytest`.\n- Keep examples simple and readable.\n\n## Engineering rules\n\n- Prefer small modules with explicit interfaces.\n- Every new core module should have tests.\n- Never bypass policy checks in the agent loop.\n- Trace every agent step.\n\n## Done when\n\n- The code runs.\n- Tests pass.\n- The design note explains why the module exists.\n",
        "pyproject.toml": "[project]\nname = \"loopath\"\nversion = \"0.1.0\"\nrequires-python = \">=3.11\"\ndependencies = []\n\n[project.optional-dependencies]\ndev = [\n  \"pytest>=8\"\n]\n\n[tool.pytest.ini_options]\npythonpath = [\"src\"]\n",
        "docs/architecture.md": "# Loopath Architecture\n\n## Core idea\n\nThe model does not directly mutate the world.\nIt proposes structured actions.\nThe harness validates, executes, observes, and records those actions.\n\n## Modules\n\n- ModelClient: produces the next action.\n- Action schema: validates model output.\n- ToolRegistry: executes allowed tools.\n- Policy: blocks unsafe actions.\n- ContextBuilder: decides what the model sees.\n- AgentLoop: controls execution.\n- TraceLogger: records what happened.\n- Evaluator: measures performance.\n",
        "docs/day1-reflection.md": "# Day 1 Reflection\n\n## 我过去如何使用 coding agent\n\n\n## 这些能力里哪些来自模型\n\n\n## 哪些来自 harness / runtime\n\n\n## 我现在对 harness 的定义\n\n",
        "src/loopath/__init__.py": "",
    }
    for relative, content in files.items():
        ok = safe_write(repo / relative, content, overwrite)
        (created if ok else skipped).append(relative)
    title = "Lab 1 project created" if lang == "en" else "Lab 1 项目已创建"
    body = [
        f"Repo: `{repo}`",
        f"Created: {', '.join(created) if created else '-'}",
        f"Skipped existing files: {', '.join(skipped) if skipped else '-'}",
        "",
        f"Verify: `python3 {ROOT / 'scripts' / 'loopath.py'} verify --episode 1 --repo {repo} --lang {lang}`",
    ]
    print(card(title, body))
    return 0


def load_lab01_verifier():
    path = ROOT / "labs" / "lab01" / "verify.py"
    spec = importlib.util.spec_from_file_location("loopath_lab01_verify", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load verifier: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    module = load_lab01_verifier()
    results = module.verify(Path(args.repo))
    passed = all(result.passed for result in results)
    ok_count = sum(1 for result in results if result.passed)
    total = len(results)
    if args.json:
        print(json.dumps({
            "passed": passed,
            "score": ok_count,
            "total": total,
            "checks": [result.__dict__ for result in results],
        }, ensure_ascii=False, indent=2))
        return 0 if passed else 1
    status = "PASS" if passed else "NEEDS WORK"
    color = "#DCFCE7" if passed else "#FEE2E2"
    fg = "#166534" if passed else "#991B1B"
    title = "Lab 1 Verification" if lang == "en" else "Lab 1 验收结果"
    print(f'<div style="border:1px solid #E5E7EB;border-radius:8px;padding:14px;font-family:ui-sans-serif,system-ui;">')
    print(f'<div style="display:inline-block;background:{color};color:{fg};font-weight:700;padding:4px 10px;border-radius:999px;">{status}</div>')
    print(f"<h3>{title}</h3>")
    print(f"<p><strong>{ok_count}/{total}</strong> checks passed.</p>")
    print("<table><thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead><tbody>")
    for result in results:
        badge = "PASS" if result.passed else "FAIL"
        badge_color = "#166534" if result.passed else "#991B1B"
        print(f"<tr><td><code>{result.name}</code></td><td style=\"color:{badge_color};font-weight:700;\">{badge}</td><td>{result.detail}</td></tr>")
    print("</tbody></table>")
    print("</div>")
    return 0 if passed else 1


def quiz(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    item = QUIZ.get(args.question)
    if not item:
        raise SystemExit(f"Question {args.question} is not available.")
    lines = [t(item["question"], lang)]
    if item["type"] == "multiple_choice":
        lines.append("")
        lines.extend(item["choices"][lang])
    lines.append("")
    lines.append("Answer this question, then ask the agent to grade it." if lang == "en" else "请先回答这一题，然后让 agent 评分。")
    print(card(f"Quiz {args.question}", lines))
    return 0


def grade(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    item = QUIZ.get(args.question)
    if not item:
        raise SystemExit(f"Question {args.question} is not available.")
    answer = args.answer or (Path(args.answer_file).read_text(encoding="utf-8") if args.answer_file else "")
    normalized = answer.strip().lower()
    if item["type"] == "multiple_choice":
        expected = item["answer"].lower()
        score = 10 if normalized.startswith(expected) or expected in normalized[:5] else 0
        feedback = ("Correct." if score else "Not quite.") if lang == "en" else ("正确。" if score else "不太对。")
    else:
        keywords = item["keywords"]
        hit = sum(1 for key in keywords if key.lower() in normalized)
        score = min(10, max(0, round(hit / max(1, len(keywords)) * 10)))
        if score >= 8:
            feedback = "Strong answer with the key boundaries covered." if lang == "en" else "回答很扎实，关键边界基本覆盖。"
        elif score >= 5:
            feedback = "Partially correct, but missing some runtime boundaries." if lang == "en" else "部分正确，但还缺少一些 runtime 边界。"
        else:
            feedback = "Needs more detail about harness boundaries and verification." if lang == "en" else "需要补充 harness 边界和验证机制。"
    reference_label = "Reference answer" if lang == "en" else "参考答案"
    print(card(f"Quiz {args.question} Score: {score}/10", [
        feedback,
        "",
        f"**{reference_label}**：{t(item['reference'], lang)}",
    ]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Loopath interactive course helper.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("start")
    p.add_argument("--lang", default="auto")
    p.add_argument("--text", default="")
    p.set_defaults(func=start)

    p = sub.add_parser("step")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--step", type=int, required=True)
    p.add_argument("--lang", default="auto")
    p.set_defaults(func=render_step)

    p = sub.add_parser("lab-create")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--repo", required=True)
    p.add_argument("--lang", default="auto")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=lab_create)

    p = sub.add_parser("verify")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--repo", required=True)
    p.add_argument("--lang", default="auto")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=verify)

    p = sub.add_parser("quiz")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--question", type=int, required=True)
    p.add_argument("--lang", default="auto")
    p.set_defaults(func=quiz)

    p = sub.add_parser("grade")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--question", type=int, required=True)
    p.add_argument("--answer", default="")
    p.add_argument("--answer-file")
    p.add_argument("--lang", default="auto")
    p.set_defaults(func=grade)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
