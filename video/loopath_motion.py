#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
W, H = 1920, 1080
FPS = 60


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        candidates = [
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/SFNSMono.ttf",
        ]
    elif bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/PingFang.ttc",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/PingFang.ttc",
        ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


F = {
    "hero": font(92, True),
    "title": font(70, True),
    "h2": font(48, True),
    "body": font(34),
    "small": font(25),
    "tiny": font(20),
    "mono": font(27, mono=True),
    "mono_small": font(21, mono=True),
}

PALETTE = {
    "bg": "#FAFAF9",
    "fg": "#0B0B10",
    "dim": "#67677A",
    "line": "#E7E5E4",
    "accent": "#7763D9",
    "accent2": "#B7A2FF",
    "ink": "#111827",
    "green": "#16A34A",
    "red": "#DC2626",
    "terminal": "#0E0E12",
}


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_in_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)


def visual_units(value: str) -> float:
    total = 0.0
    for ch in value:
        if ch == " ":
            total += 0.35
        elif ord(ch) < 128:
            total += 0.55
        else:
            total += 1.0
    return total


def wrap_text(value: str, max_units: float) -> list[str]:
    if not value:
        return []
    lines: list[str] = []
    for paragraph in value.splitlines():
        if visual_units(paragraph) <= max_units:
            lines.append(paragraph)
            continue
        if all(ord(ch) < 128 for ch in paragraph):
            current = ""
            for word in paragraph.split(" "):
                candidate = f"{current} {word}".strip()
                if current and visual_units(candidate) > max_units:
                    lines.append(current)
                    current = word
                else:
                    current = candidate
            if current:
                lines.append(current)
        else:
            current = ""
            for ch in paragraph:
                candidate = current + ch
                if current and visual_units(candidate) > max_units:
                    lines.append(current.rstrip())
                    current = ch.lstrip()
                else:
                    current = candidate
            if current:
                lines.append(current.rstrip())
    return lines


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    value: str,
    fnt: ImageFont.FreeTypeFont,
    fill: str = PALETTE["fg"],
    anchor: str | None = None,
) -> None:
    draw.text(xy, value, font=fnt, fill=fill, anchor=anchor)


def draw_multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    fnt: ImageFont.FreeTypeFont,
    max_width: int,
    fill: str = PALETTE["fg"],
    gap: int | None = None,
) -> int:
    size = getattr(fnt, "size", 30)
    lines = wrap_text(value, max_width / size)
    gap = gap or int(size * 1.35)
    x, y = xy
    for line in lines:
        draw_text(draw, (x, y), line, fnt, fill)
        y += gap
    return y


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def shadow_card(
    img: Image.Image,
    box: tuple[int, int, int, int],
    radius: int = 28,
    fill: str = "#FFFFFF",
    outline: str = "#E7E5E4",
) -> ImageDraw.ImageDraw:
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    x0, y0, x1, y1 = box
    for offset, alpha in [(34, 24), (16, 20), (5, 18)]:
        sd.rounded_rectangle((x0, y0 + offset, x1, y1 + offset), radius=radius, fill=(20, 8, 60, alpha))
    img.alpha_composite(shadow)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)
    return draw


def draw_background(draw: ImageDraw.ImageDraw, t: float, accent: str) -> None:
    draw.rectangle((0, 0, W, H), fill=PALETTE["bg"])
    ax, ay = 1390 + 80 * math.sin(t * 0.4), 180 + 50 * math.cos(t * 0.5)
    bx, by = 1540 + 60 * math.cos(t * 0.3), 760 + 45 * math.sin(t * 0.45)
    for center, radius, color in [((ax, ay), 390, "#E7DEFF"), ((bx, by), 330, "#DAD0FF")]:
        cx, cy = center
        for r in range(radius, 0, -28):
            alpha = r / radius
            rgb = hex_rgb(color)
            fill = tuple(int(lerp(250, c, alpha * 0.34)) for c in rgb)
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)
    draw.rectangle((0, 0, W, 12), fill=accent)


def enter_y(base: int, p: float, offset: int = 38) -> float:
    return base + (1 - ease_out(p)) * offset


def progress_bar(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    x0, y0, w = 132, 992, 360
    rounded(draw, (x0, y0, x0 + w, y0 + 8), 4, "#E7E5E4")
    rounded(draw, (x0, y0, x0 + w * max(0.05, p), y0 + 8), 4, accent)


def draw_kicker(draw: ImageDraw.ImageDraw, value: str, accent: str, p: float) -> None:
    y = enter_y(128, p, 18)
    draw_text(draw, (132, y), value.upper(), F["small"], accent)


def draw_heading(draw: ImageDraw.ImageDraw, title: str, subtitle: str, p: float, max_width: int = 760) -> int:
    y = int(enter_y(224, p))
    y = draw_multiline(draw, (132, y), title, F["title"], max_width, PALETTE["fg"], 78)
    if subtitle:
        y = draw_multiline(draw, (132, y + 22), subtitle, F["body"], max_width, PALETTE["dim"], 46)
    return y


def draw_bullets(draw: ImageDraw.ImageDraw, bullets: Iterable[str], x: int, y: int, accent: str) -> int:
    for bullet in bullets:
        draw.ellipse((x, y + 8, x + 12, y + 20), fill=accent)
        y = draw_multiline(draw, (x + 32, y), bullet, F["body"], 780, "#30303D", 48) + 26
    return y


def draw_code_window(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    lines: list[str],
    accent: str,
    title: str = "terminal",
    p: float = 1.0,
) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, box, 24, PALETTE["terminal"])
    rounded(draw, (x0, y0, x1, y0 + 58), 24, "#171720")
    for idx, color in enumerate(["#FF5F57", "#FFBD2E", "#28C840"]):
        draw.ellipse((x0 + 28 + idx * 34, y0 + 22, x0 + 42 + idx * 34, y0 + 36), fill=color)
    draw_text(draw, (x0 + 150, y0 + 37), title, F["tiny"], "#A7A7B4")
    visible = max(1, min(len(lines), int(math.ceil(len(lines) * ease_out(p)))))
    y = y0 + 104
    for idx, line in enumerate(lines[:visible]):
        color = "#E6E6EC"
        if line.startswith("+") or "PASS" in line:
            color = "#86EFAC"
        elif line.startswith("#"):
            color = "#B7A2FF"
        if line.startswith("$"):
            color = "#D8B4FE"
        for sub in wrap_text(line, 58):
            draw_text(draw, (x0 + 42, y), sub, F["mono"], color)
            y += 42
            if y > y1 - 34:
                return


def draw_agent_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, lines: list[str], accent: str, p: float) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, box, 28, "#FFFFFF", "#E7E5E4", 2)
    rounded(draw, (x0 + 28, y0 + 28, x0 + 120, y0 + 72), 22, "#F1EEFF")
    draw_text(draw, (x0 + 48, y0 + 58), "AI", F["small"], accent)
    draw_text(draw, (x0 + 142, y0 + 58), title, F["body"], PALETTE["fg"])
    y = y0 + 132
    visible = max(1, min(len(lines), int(math.ceil(len(lines) * ease_out(p)))))
    for line in lines[:visible]:
        rounded(draw, (x0 + 42, y - 30, x1 - 42, y + 32), 18, "#FAFAF9", "#EFEDEA")
        y = draw_multiline(draw, (x0 + 68, y - 8), line, F["small"], x1 - x0 - 140, "#31313D", 34) + 26


def draw_verify_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], p: float) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, box, 26, "#FFFFFF", "#DCFCE7", 3)
    rounded(draw, (x0 + 34, y0 + 30, x0 + 156, y0 + 72), 22, "#DCFCE7")
    draw_text(draw, (x0 + 58, y0 + 59), "PASS", F["small"], "#166534")
    draw_text(draw, (x0 + 34, y0 + 128), "Lab verification", F["h2"], PALETTE["fg"])
    draw_text(draw, (x0 + 34, y0 + 182), "15/15 checks passed", F["body"], "#166534")
    checks = ["README.md", "AGENTS.md", "architecture.md", "policy rules", "trace rules", "eval baseline"]
    visible = max(1, min(len(checks), int(math.ceil(len(checks) * ease_out(p)))))
    y = y0 + 240
    for item in checks[:visible]:
        draw.ellipse((x0 + 42, y - 18, x0 + 68, y + 8), fill="#DCFCE7")
        draw_text(draw, (x0 + 48, y), "✓", F["tiny"], "#166534")
        draw_text(draw, (x0 + 86, y), item, F["small"], "#30303D")
        y += 47


def draw_quiz_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], p: float) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, box, 26, "#FFFFFF", "#E7E5E4", 2)
    draw_text(draw, (x0 + 42, y0 + 68), "Quiz 1", F["h2"], PALETTE["fg"])
    question = "Harness 和 API wrapper 最大区别是什么？"
    draw_multiline(draw, (x0 + 42, y0 + 132), question, F["body"], x1 - x0 - 84, "#30303D", 43)
    answers = [
        "A. 让 prompt 更长",
        "B. 负责 action、tool、policy、trace、eval",
        "C. 只能用于本地模型",
    ]
    visible = max(1, min(len(answers), int(math.ceil(len(answers) * ease_out(p)))))
    y = y0 + 245
    for idx, answer in enumerate(answers[:visible]):
        fill = "#F1EEFF" if idx == 1 and p > 0.72 else "#FAFAF9"
        outline = PALETTE["accent"] if idx == 1 and p > 0.72 else "#EFEDEA"
        rounded(draw, (x0 + 42, y, x1 - 42, y + 62), 18, fill, outline, 2)
        draw_text(draw, (x0 + 68, y + 40), answer, F["small"], "#30303D")
        y += 82
    if p > 0.82:
        rounded(draw, (x0 + 42, y1 - 112, x1 - 42, y1 - 44), 20, "#DCFCE7")
        draw_text(draw, (x0 + 70, y1 - 69), "Score: 10/10 · Reference answer shown", F["small"], "#166534")


def draw_file_tree(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], p: float) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, box, 26, "#FFFFFF", "#E7E5E4", 2)
    draw_text(draw, (x0 + 42, y0 + 68), "Generated lab files", F["h2"], PALETTE["fg"])
    files = [
        "loopath-dev/",
        "  README.md",
        "  AGENTS.md",
        "  pyproject.toml",
        "  docs/architecture.md",
        "  labs/lab01/verify.py",
        "  traces/",
        "  evals/",
    ]
    visible = max(1, min(len(files), int(math.ceil(len(files) * ease_out(p)))))
    y = y0 + 138
    for line in files[:visible]:
        color = PALETTE["accent"] if line.endswith("/") else "#30303D"
        draw_text(draw, (x0 + 56, y), line, F["mono"], color)
        y += 50


def draw_loop_rail(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], p: float, accent: str) -> None:
    x0, y0, x1, y1 = box
    labels = ["ctx", "action", "policy", "tool", "obs", "trace", "eval"]
    center_y = (y0 + y1) // 2
    draw.line((x0 + 74, center_y, x1 - 74, center_y), fill="#D8D4E8", width=7)
    active = min(len(labels) - 1, int(p * len(labels)))
    for idx, label in enumerate(labels):
        x = int(lerp(x0 + 84, x1 - 84, idx / (len(labels) - 1)))
        fill = accent if idx <= active else "#FFFFFF"
        outline = accent if idx <= active else "#D8D4E8"
        rounded(draw, (x - 76, center_y - 48, x + 76, center_y + 48), 26, fill, outline, 3)
        draw_text(draw, (x, center_y + 9), label, F["tiny"], "#FFFFFF" if idx <= active else "#555567", "mm")
        if idx == active:
            r = 66 + 8 * math.sin(p * math.pi * 6)
            draw.ellipse((x - r, center_y - r, x + r, center_y + r), outline=accent, width=4)


@dataclass
class Scene:
    frame_name: str
    duration: float
    kicker: str
    title: str
    subtitle: str = ""
    bullets: tuple[str, ...] = ()
    visual: str = "code"
    code: tuple[str, ...] = ()
    agent_lines: tuple[str, ...] = ()
    accent: str = PALETTE["accent"]
    silent_reason: str = "pure-broll: on-screen copy carries the narration"


INTRO_SCENES = [
    Scene(
        "SUMMON",
        5.0,
        "Loopath",
        "Learn loop engineering inside your agent.",
        "A GitHub skill that teaches by doing.",
        ("Install the repo as a skill", "Start with $loopath", "Learn one small topic at a time"),
        "loop",
    ),
    Scene(
        "CLONE",
        7.0,
        "Install",
        "Clone the skill into your agent.",
        "Codex or Claude Code can auto-discover SKILL.md.",
        visual="code",
        code=(
            "$ git clone https://github.com/encircleacity2/loopath \\",
            "  ~/.codex/skills/loopath",
            "",
            "$ git clone https://github.com/encircleacity2/loopath \\",
            "  ~/.claude/skills/loopath",
            "",
            "# restart your agent session",
        ),
        accent="#5B4FD9",
    ),
    Scene(
        "START",
        6.0,
        "Start",
        "Say: Use $loopath.",
        "The skill detects your conversation language.",
        visual="agent",
        agent_lines=(
            "Default language: English",
            "Learning mode: one small topic at a time.",
            "Recommended start: Episode 1 / Step 1",
        ),
        accent="#2563EB",
    ),
    Scene(
        "STEP",
        7.0,
        "Study",
        "Each topic is a card, not a wall of text.",
        "Background, purpose, why it matters, and the matching explainer clip.",
        visual="agent",
        agent_lines=(
            "Episode 1 / Step 1: What Loopath Is",
            "Background: people use agents without seeing the loop.",
            "Video: media/episode-01/clips/en/step-01.mp4",
            "Next: continue, ask, lab, verify, or quiz.",
        ),
        accent="#7C3AED",
    ),
    Scene(
        "BUILD",
        7.0,
        "Lab",
        "The agent creates the project with you.",
        "No copy-paste marathon. The lab is a conversation.",
        visual="files",
        accent="#0F766E",
    ),
    Scene(
        "VERIFY",
        6.5,
        "Verify",
        "Run the rubric automatically.",
        "A clear result card shows what passed and what is missing.",
        visual="verify",
        accent="#16A34A",
    ),
    Scene(
        "QUIZ",
        6.5,
        "Quiz",
        "One question at a time.",
        "Answer, get a score, compare with the reference answer.",
        visual="quiz",
        accent="#EA580C",
    ),
    Scene(
        "PROMISE",
        5.0,
        "Loopath",
        "A tiny path into agent loops.",
        "Install. Study. Build. Verify.",
        ("context -> action -> policy -> tool", "observation -> trace -> eval"),
        "loop",
        accent="#7763D9",
    ),
]


EPISODE_SCENES = [
    Scene(
        "HOOK",
        6.0,
        "Episode 1",
        "Before code, define the harness.",
        "Mina wants a coding agent she can trust, not another prompt wrapper.",
        ("The first lesson creates boundaries", "Everything later becomes easier to verify"),
        "loop",
    ),
    Scene(
        "BOUNDARY",
        7.0,
        "Why not start with API calls?",
        "Because API calls only move text.",
        "Loop engineering controls behavior.",
        ("Context decides what the model sees", "Action schema controls what it can propose", "Policy decides what can run"),
        "loop",
        accent="#2563EB",
    ),
    Scene(
        "README",
        7.0,
        "README",
        "Write the promise first.",
        "A tiny reference implementation for loop engineering.",
        ("What this repo teaches", "What it does not try to be", "How a student knows where to start"),
        "code",
        code=(
            "# Loopath",
            "A tiny reference implementation",
            "for loop engineering.",
            "",
            "- structured model actions",
            "- policy-gated tools",
            "- traces and evals",
        ),
        accent="#7C3AED",
    ),
    Scene(
        "AGENTS",
        7.5,
        "AGENTS.md",
        "Give future agents durable instructions.",
        "This is the harness rulebook for coding collaborators.",
        ("How to run tests", "What not to bypass", "What counts as done"),
        "code",
        code=(
            "Run tests with pytest.",
            "Never bypass policy checks.",
            "Trace every agent step.",
            "Done when: tests pass",
            "and the design note explains why.",
        ),
        accent="#CA8A04",
    ),
    Scene(
        "ARCHITECTURE",
        8.0,
        "architecture.md",
        "The model does not mutate the world.",
        "It proposes actions. The harness validates, executes, observes, and records.",
        ("This sentence is the safety boundary", "It turns output into controlled behavior"),
        "code",
        code=(
            "User input",
            "  -> build context",
            "  -> model proposes action",
            "  -> policy checks action",
            "  -> tool executes",
            "  -> observation + trace",
            "  -> eval decides next loop",
        ),
        accent="#0F766E",
    ),
    Scene(
        "LOOP",
        7.5,
        "The loop",
        "Make every step observable.",
        "If you cannot trace it, you cannot improve it.",
        ("context -> action -> policy -> tool", "observation -> trace -> eval", "then the loop can continue or stop"),
        "loop",
        accent="#4F46E5",
    ),
    Scene(
        "LAB",
        8.0,
        "Lab",
        "Let the agent create the skeleton.",
        "The student interacts; the agent writes the files.",
        visual="files",
        accent="#0891B2",
    ),
    Scene(
        "VERIFY",
        7.0,
        "Verification",
        "A lab is not complete until it can be checked.",
        "The verifier inspects paths, content, policy rules, and trace rules.",
        visual="verify",
        accent="#16A34A",
    ),
    Scene(
        "QUIZ",
        7.0,
        "Quiz",
        "Understanding needs a second signal.",
        "Multiple choice checks concepts. Written answers check judgment.",
        visual="quiz",
        accent="#EA580C",
    ),
    Scene(
        "PROMISE",
        6.0,
        "Done when",
        "The repo has a boundary, a rulebook, a lab, and a verifier.",
        "Now the next lesson can safely add action schema.",
        ("README", "AGENTS.md", "architecture.md", "verify.py", "quiz rubric"),
        "loop",
        accent="#7763D9",
    ),
]


def render_scene(scene: Scene, scene_p: float, global_t: float) -> Image.Image:
    img = Image.new("RGBA", (W, H), PALETTE["bg"])
    draw = ImageDraw.Draw(img)
    p = ease_out(scene_p)
    draw_background(draw, global_t, scene.accent)
    if scene.frame_name in {"SUMMON", "PROMISE", "HOOK"}:
        y = int(enter_y(218, p, 60))
        draw_text(draw, (W // 2, y), scene.kicker.upper(), F["small"], scene.accent, "mm")
        y += 126
        for line in wrap_text(scene.title, 20):
            draw_text(draw, (W // 2, y), line, F["hero"], PALETTE["fg"], "mm")
            y += 104
        y += 8
        for line in wrap_text(scene.subtitle, 36):
            draw_text(draw, (W // 2, y), line, F["h2"], PALETTE["dim"], "mm")
            y += 62
        if scene.bullets:
            bx = 380
            by = 710
            for idx, bullet in enumerate(scene.bullets):
                w = 340 if idx < 4 else 500
                x = bx + (idx % 4) * 300
                y = by + (idx // 4) * 84
                rounded(draw, (x, y, x + w, y + 58), 29, "#FFFFFF", "#E7E5E4", 2)
                draw_text(draw, (x + w / 2, y + 33), bullet, F["small"], "#30303D", "mm")
        draw_loop_rail(draw, (380, 830, 1540, 950), scene_p, scene.accent)
        progress_bar(draw, scene_p, scene.accent)
        return img

    draw_kicker(draw, scene.kicker, scene.accent, scene_p)
    text_bottom = draw_heading(draw, scene.title, scene.subtitle, scene_p)
    if scene.bullets:
        draw_bullets(draw, scene.bullets, 150, max(470, text_bottom + 46), scene.accent)
    card_p = max(0.0, min(1.0, (scene_p - 0.18) / 0.72))
    x_shift = int((1 - ease_out(card_p)) * 80)
    box = (1038 + x_shift, 188, 1788 + x_shift, 842)
    shadow_card(img, box, 30, "#FFFFFF", "#E7E5E4")
    draw = ImageDraw.Draw(img)
    if scene.visual == "code":
        draw_code_window(draw, (1068 + x_shift, 248, 1758 + x_shift, 786), list(scene.code), scene.accent, "loopath", card_p)
    elif scene.visual == "agent":
        draw_agent_card(draw, (1068 + x_shift, 248, 1758 + x_shift, 786), "$loopath", list(scene.agent_lines), scene.accent, card_p)
    elif scene.visual == "files":
        draw_file_tree(draw, (1068 + x_shift, 248, 1758 + x_shift, 786), card_p)
    elif scene.visual == "verify":
        draw_verify_card(draw, (1068 + x_shift, 248, 1758 + x_shift, 786), card_p)
    elif scene.visual == "quiz":
        draw_quiz_card(draw, (1068 + x_shift, 248, 1758 + x_shift, 786), card_p)
    elif scene.visual == "loop":
        draw_loop_rail(draw, (1058 + x_shift, 318, 1768 + x_shift, 710), card_p, scene.accent)
    draw_text(draw, (132, 942), f"Loopath · {scene.frame_name}", F["small"], PALETTE["dim"])
    progress_bar(draw, scene_p, scene.accent)
    return img


def scene_at(scenes: list[Scene], t: float) -> tuple[int, float, float]:
    elapsed = 0.0
    for idx, scene in enumerate(scenes):
        if t < elapsed + scene.duration:
            return idx, t - elapsed, elapsed
        elapsed += scene.duration
    return len(scenes) - 1, scenes[-1].duration, elapsed - scenes[-1].duration


def total_duration(scenes: list[Scene]) -> float:
    return sum(scene.duration for scene in scenes)


def render_video(scenes: list[Scene], out: Path, music: Path | None, music_volume: float = 0.55) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    duration = total_duration(scenes)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "-",
    ]
    filter_complex = None
    if music and music.exists():
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        fade_out = max(0.0, duration - 2.0)
        filter_complex = f"[1:a]volume={music_volume},afade=t=in:st=0:d=1.2,afade=t=out:st={fade_out:.2f}:d=1.8[a]"
    cmd += [
        "-t",
        f"{duration:.3f}",
    ]
    if filter_complex:
        cmd += ["-filter_complex", filter_complex, "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v"]
    cmd += [
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
    ]
    if filter_complex:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd.append(str(out))

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    frames = int(round(duration * FPS))
    try:
        for frame in range(frames):
            t = frame / FPS
            idx, local, _ = scene_at(scenes, t)
            scene = scenes[idx]
            local_p = min(1.0, local / max(0.001, scene.duration))
            image = render_scene(scene, local_p, t)
            if local < 0.42 and idx > 0:
                prev = scenes[idx - 1]
                prev_img = render_scene(prev, 1.0, t)
                alpha = ease_in_out(local / 0.42)
                image = Image.blend(prev_img, image, alpha)
            proc.stdin.write(image.convert("RGB").tobytes())
    finally:
        proc.stdin.close()
    stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(stderr[-4000:])


def write_storyboard(name: str, scenes: list[Scene], path: Path, target: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    start = 0.0
    rows = []
    for idx, scene in enumerate(scenes, start=1):
        end = start + scene.duration
        rows.append((idx, start, end, scene))
        start = end
    payload = {
        "title": name,
        "mode": "pure-broll-product-demo",
        "channel": "GitHub README / website hero",
        "aspect_ratio": "16:9",
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "style_preset": "openai-clean",
        "duration_seconds": round(total_duration(scenes), 2),
        "visual_quality_bar": {
            "animation_target": "launch-grade product motion with layered micro-interactions",
            "overflow_policy": "resize and split text before render",
            "zoom_policy": "target-led camera moves and slow product-state reveals",
        },
        "cast": {
            "protagonist": "Mina, a builder learning how coding agents really work",
            "supporting": ["Codex", "Claude Code", "Loopath verifier"],
        },
        "canon": [
            "Loopath GitHub repo",
            "$loopath course entrypoint",
            "README.md",
            "AGENTS.md",
            "docs/architecture.md",
            "Lab verification: PASS 15/15",
        ],
        "echo": [{"artifact": "$loopath", "frames": ["START", "STEP", "QUIZ"]}],
        "arc_map": {
            "hook": [scenes[0].frame_name],
            "tension": [scene.frame_name for scene in scenes[1:3]],
            "reveal": [scene.frame_name for scene in scenes[3:5]],
            "magic": [scene.frame_name for scene in scenes[5:-1]],
            "promise": [scenes[-1].frame_name],
        },
        "segments": [
            {
                "id": f"{idx:02d}-{scene.frame_name.lower()}",
                "frame_name": scene.frame_name,
                "start": round(start, 2),
                "end": round(end, 2),
                "title": scene.title,
                "visual": scene.visual,
                "silent": True,
                "silent_reason": scene.silent_reason,
                "motion": {
                    "quality": "pure-broll product motion",
                    "entrance": "opacity + y + scale, power3-style cubic",
                    "continuous": "liquid lavender background drift and loop rail pulse",
                    "micro_interactions": "terminal typing, file reveal, verification check reveal, quiz scoring",
                    "exit": "scene transition crossfade only",
                },
                "layout_guardrails": {
                    "safe_margin_px": 96,
                    "text_fit": "wrapped by visual unit width",
                    "max_text_lines": 4,
                    "overflow_policy": "split lines before render",
                },
                "camera_path": [
                    {"at": round(start, 2), "scale": 1.0, "target": "scene context", "intent": "establish the beat"},
                    {"at": round(end - 0.4, 2), "scale": 1.035, "target": scene.visual, "intent": "focus on product action"},
                ],
            }
            for idx, start, end, scene in rows
        ],
    }
    (path.with_suffix(".json")).write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    lines = [
        f"# {name}",
        "",
        "- Mode: pure-broll-product-demo",
        "- Channel: GitHub README / website hero",
        "- Aspect: 16:9",
        f"- Resolution: {W}x{H} @ {FPS}fps",
        "- Style preset: openai-clean",
        f"- Output: `{target}`",
        "",
        "## Timeline",
        "",
        "| # | Time | Frame | What happens | Cue |",
        "|---|---:|---|---|---|",
    ]
    for idx, start, end, scene in rows:
        lines.append(
            f"| {idx} | {start:05.2f}-{end:05.2f}s | **{scene.frame_name}** | {scene.title} | silent: {scene.silent_reason} |"
        )
    lines += [
        "",
        "## Canon",
        "",
        "- Loopath GitHub repo",
        "- `$loopath` course entrypoint",
        "- `README.md`, `AGENTS.md`, `docs/architecture.md`",
        "- Lab verification: `PASS 15/15`",
        "",
        "## What drives the narrative forward",
        "",
        "The viewer moves from install, to interactive learning, to lab creation, to verification and quiz scoring.",
        "",
        "## What's locked",
        "",
        f"- Target duration: {total_duration(scenes):.1f}s",
        "- Pure B-roll, no presenter, no TTS",
        "- 16:9, 60fps, OpenAI-clean visual system",
    ]
    path.write_text("\n".join(lines) + "\n")


def make_contact_sheet(video: Path, out: Path, tile: str = "4x3", every: int = 8) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vf",
            f"fps=1/{every},scale=480:270,tile={tile}",
            "-frames:v",
            "1",
            str(out),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def make_gif(video: Path, out: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-filter_complex",
            "fps=12,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5",
            "-loop",
            "0",
            str(out),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def render_intro() -> None:
    target = ROOT / "media" / "intro" / "loopath-intro.mp4"
    music = ROOT / "media" / "intro" / "music_bed.m4a"
    write_storyboard("Loopath Intro", INTRO_SCENES, ROOT / "video" / "intro" / "storyboard.md", target)
    render_video(INTRO_SCENES, target, music, 0.55)
    make_contact_sheet(target, ROOT / "media" / "intro" / "loopath-intro-contact-sheet.png", "3x2", 8)
    make_gif(target, ROOT / "media" / "intro" / "loopath-intro.gif")


def render_episode_01() -> None:
    target = ROOT / "media" / "loopath-episode-01.mp4"
    music = ROOT / "media" / "intro" / "music_bed.m4a"
    write_storyboard("Loopath Episode 1", EPISODE_SCENES, ROOT / "video" / "episode-01" / "storyboard.md", target)
    narration = ROOT / "video" / "episode-01" / "narration.txt"
    narration.write_text(
        "No TTS narration in this version. The video is pure B-roll; on-screen copy carries the teaching beats.\n"
        "The MP4 keeps the generated music bed as background audio.\n"
    )
    render_video(EPISODE_SCENES, target, music, 0.42)
    make_contact_sheet(target, ROOT / "media" / "episode-01-contact-sheet.png", "4x3", 7)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Loopath explainer videos.")
    parser.add_argument("target", choices=["intro", "episode-01", "all"])
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required")
    if args.target in {"intro", "all"}:
        render_intro()
    if args.target in {"episode-01", "all"}:
        render_episode_01()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
