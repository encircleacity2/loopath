#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FRAMES = ROOT / "frames"
AUDIO = ROOT / "audio"
CLIPS = ROOT / "clips"
DIST = ROOT / "dist"
PREVIEW = ROOT / "preview"
W, H = 1920, 1080
FPS = 30


SCENES = [
    {
        "id": "01-hook",
        "kicker": "EPISODE 01",
        "title": "Loopath",
        "subtitle": "从使用 Coding Agent 到理解 Loop Engineering",
        "body": [
            "目标不是再写一个 prompt demo",
            "而是搭一个小而完整的 agent runtime",
            "最终每一步都能被验证、追踪和评分",
        ],
        "chips": ["model", "action", "tool", "policy", "trace", "eval"],
        "narration": "欢迎来到 Loopath 第一课。这个项目的目标很简单：像 nanoGPT 帮你理解 GPT 一样，Loopath 帮你从零理解 coding agent 背后的 loop engineering。今天我们不急着接模型，而是先把系统边界和第一个 lab 做扎实。",
        "accent": "#2563EB",
    },
    {
        "id": "02-promise",
        "kicker": "WHAT YOU WILL BUILD",
        "title": "一个能跑、能验、能解释的小 Harness",
        "body": [
            "输入：用户给一个 coding task",
            "过程：模型提出结构化 action",
            "边界：policy 决定动作是否允许",
            "证据：trace 记录每一步发生了什么",
        ],
        "code": [
            "$ loopath run \"Fix the failing test\"",
            "read_file -> edit_file -> run_command -> final_answer",
            "trace: traces/2026-xx-xx-bugfix.json",
        ],
        "narration": "整个课程最后会得到一个小 harness。用户给一个 coding task，模型提出结构化 action，policy 检查动作，tool 执行动作，trace 记录过程，eval 验证结果。它不大，但它是真的工程系统。",
        "accent": "#059669",
    },
    {
        "id": "03-not-wrapper",
        "kicker": "KEY IDEA",
        "title": "Harness 不是 API Wrapper",
        "body": [
            "API wrapper：文本输入，文本输出",
            "Agent harness：意图、动作、执行、观察、评测闭环",
            "Loop engineering：把改进变成可重复实验",
        ],
        "columns": [
            ("wrapper", ["prompt", "call model", "answer"]),
            ("harness", ["action schema", "tool boundary", "policy", "trace", "eval"]),
        ],
        "narration": "第一件事要分清楚：harness 不是 API wrapper。API wrapper 只负责把文本送进模型，再拿回答。Agent harness 负责把模型的意图变成可审查的动作，再把真实执行结果变成下一轮观察。",
        "accent": "#7C3AED",
    },
    {
        "id": "04-layers",
        "kicker": "MENTAL MODEL",
        "title": "三层不要混",
        "body": [
            "Model：推理和生成下一步",
            "Agent：选择 action，读取 observation",
            "Harness：执行、权限、记录、评测",
        ],
        "diagram": ["Model", "Agent", "Harness", "World"],
        "narration": "我们用一个很实用的三层模型：Model 负责推理，Agent 负责选择 action，Harness 负责执行、权限、记录和评测。模型不应该直接改世界，它应该提出动作，然后由 harness 决定能不能做。",
        "accent": "#EA580C",
    },
    {
        "id": "05-lab-target",
        "kicker": "LAB 1 TARGET",
        "title": "第一节课不写模型，先搭项目骨架",
        "body": [
            "创建 repo 结构",
            "写 README：项目承诺",
            "写 architecture：系统边界",
            "写 AGENTS.md：给未来 agent 的工作规则",
            "写 verify 脚本：让 lab 可验收",
        ],
        "narration": "第一节课的 lab 不写模型，也不接 API。我们先创建项目结构，写 README，写 architecture，写 AGENTS 点 md，最后写一个 verify 脚本。目标是让后续每一节课都站在清楚边界上。",
        "accent": "#0F766E",
    },
    {
        "id": "06-folders",
        "kicker": "STEP 1",
        "title": "创建 Loopath 目录",
        "body": [
            "代码放在 src/loopath",
            "测试放在 tests",
            "demo task 放在 demo_repos",
            "eval、trace、docs 从第一天就存在",
        ],
        "code": [
            "mkdir loopath && cd loopath",
            "mkdir -p src/loopath tests demo_repos prompts evals traces docs",
            "touch README.md AGENTS.md pyproject.toml",
            "touch src/loopath/__init__.py",
        ],
        "narration": "第一步创建目录。注意 evals、traces 和 docs 从第一天就存在。因为 Loopath 的重点不是让模型偶尔跑通，而是让每一次行动都能被记录、验证和改进。",
        "accent": "#0284C7",
    },
    {
        "id": "07-readme",
        "kicker": "STEP 2",
        "title": "README 是产品承诺",
        "body": [
            "它告诉读者：这个 repo 解决什么",
            "它告诉自己：暂时不解决什么",
            "短项目更需要清楚边界",
        ],
        "code": [
            "# Loopath",
            "A tiny reference implementation",
            "for loop engineering.",
            "",
            "- structured model actions",
            "- tool execution",
            "- policy checks",
            "- tracing and evals",
        ],
        "narration": "第二步写 README。README 不是装饰，它是产品承诺。Loopath 的承诺是一句话：一个用于理解 loop engineering 的 tiny reference implementation。它会展示 action、tool、policy、trace 和 eval。",
        "accent": "#DB2777",
    },
    {
        "id": "08-architecture",
        "kicker": "STEP 3",
        "title": "Architecture 先写核心约束",
        "body": [
            "最重要的一句话：model 不直接修改世界",
            "模型提出 action",
            "harness 负责验证、执行、观察、记录",
        ],
        "code": [
            "The model does not directly",
            "mutate the world.",
            "It proposes structured actions.",
            "The harness validates, executes,",
            "observes, and records.",
        ],
        "narration": "第三步写 architecture。第一版不需要长，最关键是写下系统约束：model 不直接修改世界。它只提出结构化 action，harness 负责验证、执行、观察和记录。",
        "accent": "#16A34A",
    },
    {
        "id": "09-loop",
        "kicker": "CORE LOOP",
        "title": "第一版循环先画出来",
        "body": [
            "context -> action -> policy -> tool",
            "tool -> observation -> trace -> next step",
            "eval 判断任务是否真的完成",
        ],
        "diagram": ["Context", "Action", "Policy", "Tool", "Observation", "Trace", "Eval"],
        "narration": "接着把核心 loop 画出来。构建上下文，生成 action，policy 检查，tool 执行，得到 observation，写入 trace，然后继续下一步。最后 eval 判断任务是不是真的完成。",
        "accent": "#4F46E5",
    },
    {
        "id": "10-agents",
        "kicker": "STEP 4",
        "title": "AGENTS.md 是给未来 Agent 的说明书",
        "body": [
            "不要只写给人看",
            "写清楚测试命令",
            "写清楚工程规则",
            "写清楚 Done When",
        ],
        "code": [
            "Run tests with pytest.",
            "Never bypass policy checks in the agent loop.",
            "Trace every agent step.",
            "Done when: code runs, tests pass, design note explains why.",
        ],
        "narration": "第四步写 AGENTS 点 md。它不是普通说明文档，而是给未来 coding agent 的 durable instruction。你要告诉 agent 怎么跑测试，哪些规则不能破坏，什么叫完成。",
        "accent": "#CA8A04",
    },
    {
        "id": "11-pyproject",
        "kicker": "STEP 5",
        "title": "pyproject 只放最小依赖",
        "body": [
            "第一课不接真实模型",
            "不引入复杂框架",
            "只保留后续测试需要的基础结构",
        ],
        "code": [
            "[project]",
            "name = \"loopath\"",
            "requires-python = \">=3.11\"",
            "",
            "[project.optional-dependencies]",
            "dev = [\"pytest>=8\"]",
        ],
        "narration": "第五步写 pyproject。第一课不接真实模型，也不引入复杂框架。我们先让项目能被安装、能跑测试、能被后续 agent 稳定接手。",
        "accent": "#0891B2",
    },
    {
        "id": "12-verify",
        "kicker": "STEP 6",
        "title": "每个 Lab 都要能被验证",
        "body": [
            "检查必需路径是否存在",
            "检查 README 是否写出 loop engineering",
            "检查 architecture 是否写出关键约束",
            "检查 AGENTS.md 是否包含 policy 和 trace 规则",
        ],
        "code": [
            "assert Path(\"README.md\").exists()",
            "assert \"loop engineering\" in readme",
            "assert \"does not directly mutate\" in architecture",
            "assert \"Trace every agent step\" in agents",
            "print(\"Lab 1 verification passed\")",
        ],
        "narration": "第六步是这门课和普通教程不一样的地方：每个 lab 都要能被验证。第一课的 verify 脚本检查路径、README、architecture 和 AGENTS 点 md。通过时输出 Lab 1 verification passed。",
        "accent": "#DC2626",
    },
    {
        "id": "13-agent-verifier",
        "kicker": "AGENT VERIFIER",
        "title": "让 Agent 也能按 Rubric 打分",
        "body": [
            "先运行自检命令",
            "再阅读关键文件",
            "返回 score、evidence、missing requirements",
            "不要直接替学生重写项目",
        ],
        "code": [
            "Score: 0-10",
            "Evidence: commands run and files inspected",
            "Missing requirements",
            "One concrete next improvement",
        ],
        "narration": "学生做完 lab 后，可以让 coding agent 当 verifier。它先运行自检命令，再检查关键文件，最后给出分数、证据、缺失项和一个具体改进建议。注意，verifier 不应该直接替学生重写项目。",
        "accent": "#9333EA",
    },
    {
        "id": "14-quiz",
        "kicker": "QUIZ DESIGN",
        "title": "Quiz 分三档",
        "body": [
            "Level 1：概念选择题",
            "Level 2：工程判断题",
            "Level 3：开放解答题",
            "模型按正确性、具体性、取舍意识、表达清晰评分",
        ],
        "narration": "每节课还会有三档 quiz。第一档检查概念，第二档检查工程判断，第三档要求学生写解释，由模型按正确性、具体性、取舍意识和表达清晰度评分。",
        "accent": "#65A30D",
    },
    {
        "id": "15-done",
        "kicker": "DONE WHEN",
        "title": "第一课完成标准",
        "body": [
            "项目结构存在",
            "README 能说明项目目的",
            "architecture 写清楚 model 不直接改世界",
            "AGENTS.md 有测试、policy、trace 规则",
            "verify 脚本通过",
        ],
        "narration": "所以第一课的完成标准很清楚：项目结构存在，README 能说明项目目的，architecture 写清楚 model 不直接改世界，AGENTS 点 md 有测试、policy 和 trace 规则，verify 脚本通过。",
        "accent": "#0D9488",
    },
    {
        "id": "16-next",
        "kicker": "NEXT EPISODE",
        "title": "下一课：Action Schema",
        "body": [
            "把模型的自然语言想法",
            "变成可执行、可审查、可测试的 action protocol",
            "这是 Loopath 的第一道可靠性防线",
        ],
        "code": [
            "{\"type\":\"read_file\",\"path\":\"app.py\"}",
            "{\"type\":\"run_command\",\"command\":\"pytest\"}",
            "{\"type\":\"final_answer\",\"message\":\"Done\"}",
        ],
        "narration": "下一课我们开始写第一道可靠性防线：Action Schema。我们会把模型的自然语言想法，变成可执行、可审查、可测试的 action protocol。",
        "accent": "#2563EB",
    },
]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("+", " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, check=True, **kwargs)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def visual_units(value: str) -> float:
    total = 0.0
    for ch in value:
        if ch == " ":
            total += 0.35
        elif ord(ch) < 128:
            total += 0.58
        else:
            total += 1.0
    return total


def wrap_text(value: str, max_units: float) -> list[str]:
    if not value:
        return [""]
    if "\n" in value:
        lines: list[str] = []
        for part in value.splitlines():
            lines.extend(wrap_text(part, max_units))
        return lines
    if visual_units(value) <= max_units:
        return [value]
    lines: list[str] = []
    current = ""
    for ch in value:
        candidate = current + ch
        if current and visual_units(candidate) > max_units:
            lines.append(current.rstrip())
            current = ch.lstrip()
        else:
            current = candidate
    if current:
        lines.append(current.rstrip())
    return lines


def text(
    x: int,
    y: int,
    content: str,
    size: int,
    weight: int = 500,
    fill: str = "#111827",
    anchor: str = "start",
    family: str = "PingFang SC, Hiragino Sans GB, Arial, sans-serif",
) -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}">{esc(content)}</text>'
    )


def multiline(
    x: int,
    y: int,
    content: str,
    size: int,
    max_width: int,
    weight: int = 500,
    fill: str = "#111827",
    line_gap: int | None = None,
    family: str = "PingFang SC, Hiragino Sans GB, Arial, sans-serif",
) -> tuple[list[str], int]:
    units = max_width / size
    gap = line_gap or int(size * 1.32)
    lines = wrap_text(content, units)
    parts = [
        text(x, y + idx * gap, line, size, weight, fill, family=family)
        for idx, line in enumerate(lines)
    ]
    return parts, y + len(lines) * gap


def render_code_panel(parts: list[str], scene: dict, accent: str) -> None:
    code = scene.get("code")
    if not code:
        return
    x, y, w, h = 1060, 300, 700, 470
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#0F172A"/>')
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="54" rx="18" fill="{accent}" opacity="0.24"/>')
    parts.append(text(x + 28, y + 37, "lab snippet", 22, 700, "#E5E7EB"))
    cy = y + 104
    for line in code:
        if line == "":
            cy += 24
            continue
        wrapped = wrap_text(line, 58)
        for sub in wrapped[:2]:
            parts.append(text(x + 34, cy, sub, 24, 500, "#D1FAE5", family="Menlo, Monaco, Consolas, monospace"))
            cy += 38
        if cy > y + h - 44:
            break


def render_columns(parts: list[str], scene: dict, accent: str) -> None:
    columns = scene.get("columns")
    if not columns:
        return
    x0, y0 = 1060, 310
    for idx, (title, items) in enumerate(columns):
        x = x0 + idx * 350
        parts.append(f'<rect x="{x}" y="{y0}" width="310" height="390" rx="22" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="2"/>')
        parts.append(text(x + 26, y0 + 58, title, 34, 800, accent))
        cy = y0 + 118
        for item in items:
            parts.append(f'<circle cx="{x+34}" cy="{cy-8}" r="5" fill="{accent}"/>')
            wrapped, next_y = multiline(x + 54, cy, item, 26, 220, 600, "#334155", 34)
            parts.extend(wrapped)
            cy = next_y + 14


def render_diagram(parts: list[str], scene: dict, accent: str) -> None:
    labels = scene.get("diagram")
    if not labels:
        return
    if len(labels) == 4:
        x, y = 1080, 330
        for idx, label in enumerate(labels):
            yy = y + idx * 112
            parts.append(f'<rect x="{x}" y="{yy}" width="570" height="78" rx="20" fill="{accent}" opacity="{0.13 + idx * 0.03}" stroke="{accent}" stroke-width="2"/>')
            parts.append(text(x + 285, yy + 50, label, 30, 800, "#0F172A", "middle"))
            if idx < len(labels) - 1:
                parts.append(f'<path d="M {x+285} {yy+84} L {x+285} {yy+106}" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>')
                parts.append(f'<path d="M {x+285} {yy+106} l -9 -11 m 9 11 l 9 -11" stroke="{accent}" stroke-width="5" fill="none" stroke-linecap="round"/>')
        return
    x0, y0 = 1030, 328
    box_w, box_h, gap = 214, 84, 24
    for idx, label in enumerate(labels):
        row = 0 if idx < 3 else 1 if idx < 6 else 2
        col = idx if idx < 3 else idx - 3 if idx < 6 else idx - 6
        x = x0 + col * (box_w + gap)
        y = y0 + row * 126
        parts.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="20" fill="{accent}" opacity="{0.12 + idx * 0.015}" stroke="{accent}" stroke-width="2"/>')
        parts.append(text(x + box_w // 2, y + 53, label, 24, 800, "#0F172A", "middle"))
        if idx < len(labels) - 1 and col < 2:
            ax = x + box_w + 4
            parts.append(f'<path d="M {ax} {y+42} L {ax+gap-8} {y+42}" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>')
            parts.append(f'<path d="M {ax+gap-8} {y+42} l -8 -7 m 8 7 l -8 7" stroke="{accent}" stroke-width="4" fill="none" stroke-linecap="round"/>')


def render_scene_svg(scene: dict, index: int) -> str:
    accent = scene["accent"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="1920" height="1080" fill="#F8FAFC"/>',
        f'<rect x="0" y="0" width="1920" height="18" fill="{accent}"/>',
        '<rect x="92" y="76" width="1736" height="928" rx="28" fill="white" stroke="#E2E8F0" stroke-width="2"/>',
        text(145, 150, scene["kicker"], 30, 800, accent),
    ]
    title_parts, title_bottom = multiline(145, 250, scene["title"], 58, 780, 850, "#0F172A", 70)
    parts.extend(title_parts)
    if scene.get("subtitle"):
        subtitle_parts, title_bottom = multiline(145, title_bottom + 18, scene["subtitle"], 32, 780, 600, "#475569", 42)
        parts.extend(subtitle_parts)
    y = max(430, title_bottom + 40)
    for line in scene.get("body", []):
        parts.append(f'<circle cx="165" cy="{y-12}" r="7" fill="{accent}"/>')
        wrapped, next_y = multiline(190, y, line, 31, 780, 550, "#334155", 42)
        parts.extend(wrapped)
        y = next_y + 14
    if scene.get("chips"):
        x = 145
        y = max(y + 42, 760)
        for chip in scene["chips"]:
            width = int(88 + visual_units(chip) * 25)
            parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="62" rx="31" fill="{accent}" opacity="0.11" stroke="{accent}" stroke-width="2"/>')
            parts.append(text(x + width // 2, y + 40, chip, 24, 800, accent, "middle"))
            x += width + 18
    render_code_panel(parts, scene, accent)
    render_columns(parts, scene, accent)
    render_diagram(parts, scene, accent)
    parts.append(text(145, 944, "Loopath · Episode 01 · Lab 1", 26, 650, "#64748B"))
    parts.append(text(1775, 944, f"{index:02d}/{len(SCENES):02d}", 26, 700, "#64748B", "end"))
    parts.append("</svg>")
    return "\n".join(parts)


def write_story_files() -> None:
    storyboard = {
        "title": "Loopath Episode 1",
        "mode": "pure-broll-product-demo",
        "aspect_ratio": "16:9",
        "width": W,
        "height": H,
        "segments": [
            {
                "id": scene["id"],
                "kicker": scene["kicker"],
                "title": scene["title"],
                "narration": scene["narration"],
            }
            for scene in SCENES
        ],
    }
    (ROOT / "storyboard.json").write_text(json.dumps(storyboard, ensure_ascii=False, indent=2))
    (ROOT / "narration.txt").write_text("\n\n".join(scene["narration"] for scene in SCENES))


def make_frames() -> None:
    for i, scene in enumerate(SCENES, start=1):
        svg = FRAMES / f"{i:02d}-{scene['id']}.svg"
        png = FRAMES / f"{i:02d}-{scene['id']}.png"
        svg.write_text(render_scene_svg(scene, i))
        if png.exists():
            png.unlink()
        run(["sips", "-s", "format", "png", str(svg), "--out", str(png)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not png.exists():
            raise RuntimeError(f"Expected PNG missing: {png}")


def make_audio() -> list[Path]:
    audio_paths: list[Path] = []
    for i, scene in enumerate(SCENES, start=1):
        out = AUDIO / f"{i:02d}-{scene['id']}.aiff"
        if out.exists():
            out.unlink()
        run(["say", "-v", "Tingting", "-r", "176", "-o", str(out), scene["narration"]])
        audio_paths.append(out)
    return audio_paths


def duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def make_clips(audio_paths: list[Path]) -> list[Path]:
    clips: list[Path] = []
    for i, (scene, audio) in enumerate(zip(SCENES, audio_paths), start=1):
        png = FRAMES / f"{i:02d}-{scene['id']}.png"
        out = CLIPS / f"{i:02d}-{scene['id']}.mp4"
        dur = duration(audio) + 0.45
        vf = "scale=1920:1080,format=yuv420p,fade=t=in:st=0:d=0.20,fade=t=out:st={:.2f}:d=0.20".format(max(0.1, dur - 0.20))
        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(png),
                "-i",
                str(audio),
                "-t",
                f"{dur:.3f}",
                "-vf",
                vf,
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "160k",
                "-pix_fmt",
                "yuv420p",
                "-shortest",
                str(out),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        clips.append(out)
    return clips


def concat_clips(clips: list[Path]) -> Path:
    list_file = ROOT / "clips.txt"
    list_file.write_text("\n".join(f"file '{clip.resolve()}'" for clip in clips) + "\n")
    out = DIST / "loopath-episode-01.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out


def make_preview(video: Path) -> None:
    contact = PREVIEW / "contact-sheet.png"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vf",
            "fps=1/24,scale=480:270,tile=4x4",
            "-frames:v",
            "1",
            str(contact),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for second, name in [(6, "frame-006.png"), (60, "frame-060.png"), (120, "frame-120.png"), (180, "frame-180.png")]:
        run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(second),
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(PREVIEW / name),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def main() -> None:
    for path in (FRAMES, AUDIO, CLIPS, DIST, PREVIEW):
        path.mkdir(parents=True, exist_ok=True)
    write_story_files()
    make_frames()
    audio_paths = make_audio()
    clips = make_clips(audio_paths)
    out = concat_clips(clips)
    make_preview(out)
    total = duration(out)
    print(f"\nDone: {out}")
    print(f"Duration: {total:.1f}s")


if __name__ == "__main__":
    main()
