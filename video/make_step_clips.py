#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "loopath.py"
MEDIA_OUT = ROOT / "media"
SCREENSHOT_OUT = ROOT / "media" / "screenshots"
W, H = 1280, 720
FPS = 30
DURATION = 7


def load_loopath():
    spec = importlib.util.spec_from_file_location("loopath_course_script", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        candidates = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/SFNSMono.ttf"]
    elif bold:
        candidates = [
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
        ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


F = {
    "hero": font(46, True),
    "title": font(38, True),
    "label": font(19, True),
    "body": font(23),
    "small": font(18),
    "mono": font(18, mono=True),
}


ACCENT = {"zh": "#0F766E", "en": "#4F46E5"}
BG = "#F8FAFC"
INK = "#111827"
MUTED = "#64748B"
LINE = "#E2E8F0"
CARD = "#FFFFFF"


def visual_units(text: str) -> float:
    total = 0.0
    for ch in text:
        if ch == " ":
            total += 0.35
        elif ch.isascii():
            total += 0.56
        else:
            total += 1.0
    return total


def wrap(text: str, max_units: float, max_lines: int = 3) -> list[str]:
    if visual_units(text) <= max_units:
        return [text]
    lines: list[str] = []
    truncated = False
    if all(ch.isascii() for ch in text):
        current = ""
        words = text.split()
        for index, word in enumerate(words):
            candidate = f"{current} {word}".strip()
            if current and visual_units(candidate) > max_units:
                lines.append(current)
                current = word
            else:
                current = candidate
            if len(lines) >= max_lines:
                truncated = index < len(words) - 1 or bool(current)
                break
        if current and len(lines) < max_lines:
            lines.append(current)
    else:
        tokens: list[str] = []
        current = ""
        for ch in text:
            if ch.isascii() and (ch.isalnum() or ch in "._-"):
                current += ch
            else:
                if current:
                    tokens.append(current)
                    current = ""
                tokens.append(ch)
        if current:
            tokens.append(current)
        current = ""
        for index, token in enumerate(tokens):
            candidate = current + token
            if current and visual_units(candidate) > max_units:
                lines.append(current.rstrip())
                current = token.lstrip()
            else:
                current = candidate
            if len(lines) >= max_lines:
                truncated = index < len(tokens) - 1 or bool(current)
                break
        if current and len(lines) < max_lines:
            lines.append(current.rstrip())
    if lines and (truncated or visual_units(lines[-1]) > max_units):
        suffix = "..."
        base = lines[-1].rstrip()
        while base and visual_units(base + suffix) > max_units:
            base = base[:-1].rstrip()
        lines[-1] = (base or lines[-1][:1]) + suffix
    return lines[:max_lines]


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, fnt, fill=INK, anchor=None) -> None:
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def draw_panel(draw: ImageDraw.ImageDraw, box, label: str, body: str, accent: str, p: float) -> None:
    x0, y0, x1, y1 = box
    rounded(draw, box, 18, CARD, LINE, 2)
    draw_text(draw, (x0 + 28, y0 + 36), label.upper(), F["label"], accent)
    lines = wrap(body, (x1 - x0 - 56) / F["body"].size, 3)
    y = y0 + 76
    visible = max(1, int(round(len(lines) * ease(p))))
    for line in lines[:visible]:
        draw_text(draw, (x0 + 28, y), line, F["body"], INK)
        y += 34


def render_step_frame(module, lang: str, episode_idx: int, step_idx: int, frame_idx: int) -> Image.Image:
    episode = module.EPISODES[episode_idx]
    step = episode.steps[step_idx - 1]
    p = frame_idx / max(1, (DURATION * FPS - 1))
    accent = ACCENT[lang]
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 10), fill=accent)

    # Soft background shapes stay outside text areas.
    draw.ellipse((860, -120, 1370, 390), fill="#ECE7FF")
    draw.ellipse((980, 360, 1420, 850), fill="#E9F7F1" if lang == "zh" else "#EEF2FF")

    draw_text(draw, (76, 72), f"Episode {episode_idx} / Step {step_idx:02d}", F["small"], accent)
    title = module.t(step.title, lang)
    title_lines = wrap(title, 18, 2)
    y = 128
    for line in title_lines:
        draw_text(draw, (76, y), line, F["hero"], INK)
        y += 56

    subtitle = "Loopath interactive course" if lang == "en" else "Loopath 互动课程"
    draw_text(draw, (76, y + 10), subtitle, F["body"], MUTED)

    labels = {
        "zh": ("背景", "目标", "为什么重要"),
        "en": ("Background", "Goal", "Why it matters"),
    }[lang]
    bodies = [
        module.t(step.background, lang),
        module.t(step.purpose, lang),
        module.t(step.why, lang),
    ]
    panel_p = [min(1, max(0, (p - offset) / 0.45)) for offset in (0.08, 0.24, 0.40)]
    top = 338
    for idx, (label, body) in enumerate(zip(labels, bodies)):
        x0 = 76 + idx * 386
        draw_panel(draw, (x0, top, x0 + 340, top + 190), label, body, accent, panel_p[idx])

    # Bottom action strip. Keep labels short to avoid all overflow.
    strip_y = 594
    rounded(draw, (76, strip_y, W - 76, strip_y + 62), 20, "#FFFFFF", LINE, 2)
    draw_text(draw, (104, strip_y + 40), "next", F["label"], accent)
    actions = ["ask", "continue", "lab", "verify", "quiz"] if lang == "en" else ["提问", "继续", "lab", "验收", "quiz"]
    x = 220
    for action in actions:
        rounded(draw, (x, strip_y + 13, x + 120, strip_y + 49), 18, "#F8FAFC", LINE, 1)
        draw_text(draw, (x + 60, strip_y + 37), action, F["small"], INK, "mm")
        x += 138
    return img


def render_clip(module, lang: str, episode_idx: int, step_idx: int) -> Path:
    out_dir = MEDIA_OUT / f"episode-{episode_idx:02d}" / "clips" / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"step-{step_idx:02d}.mp4"
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
        "-t",
        str(DURATION),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for frame_idx in range(DURATION * FPS):
            img = render_step_frame(module, lang, episode_idx, step_idx, frame_idx)
            proc.stdin.write(img.tobytes())
    finally:
        proc.stdin.close()
    stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(stderr[-3000:])
    return out


def draw_chat_screenshot(lang: str, kind: str) -> Image.Image:
    img = Image.new("RGB", (1280, 820), "#F8FAFC")
    draw = ImageDraw.Draw(img)
    accent = ACCENT[lang]
    draw.rectangle((0, 0, 1280, 10), fill=accent)
    draw_text(draw, (70, 70), "Loopath in an agent" if lang == "en" else "Agent 中的 Loopath", F["title"], INK)
    draw_text(draw, (70, 118), "Reference screenshot" if lang == "en" else "参考截图", F["body"], MUTED)

    # User prompt.
    rounded(draw, (700, 82, 1200, 152), 24, accent)
    prompt = "Use $loopath to start" if lang == "en" else "Use $loopath 开始课程"
    draw_text(draw, (950, 125), prompt, F["body"], "#FFFFFF", "mm")

    x0, y0, x1, y1 = 70, 210, 1210, 730
    rounded(draw, (x0, y0, x1, y1), 28, "#FFFFFF", LINE, 2)
    draw_text(draw, (x0 + 34, y0 + 52), "$loopath", F["body"], accent)

    if kind == "start":
        title = "Loopath Interactive Course" if lang == "en" else "Loopath 互动课程"
        lines = [
            "Default language: English" if lang == "en" else "默认语言：中文",
            "One small topic at a time" if lang == "en" else "每次一个小课题",
            "You can ask, continue, start lab, verify, or quiz" if lang == "en" else "可以提问、继续、开始 lab、验收或 quiz",
            "Recommended start: Episode 1 / Step 1" if lang == "en" else "建议从 Episode 1 / Step 1 开始",
        ]
    elif kind == "step":
        title = "Episode 1 / Step 1: What Loopath Is" if lang == "en" else "Episode 1 / Step 1: Loopath 是什么"
        lines = [
            "Background: people use agents without seeing the loop." if lang == "en" else "背景：很多人会用 agent，但看不到背后的 loop。",
            "Goal: frame Loopath as a tiny reference implementation." if lang == "en" else "目标：把 Loopath 定位成小而完整的参考实现。",
            "Video: media/episode-01/clips/{}/step-01.mp4".format(lang),
            "Next: continue, ask, lab, verify, or quiz." if lang == "en" else "下一步：继续、提问、lab、验收或 quiz。",
        ]
    else:
        title = "Lab 1 Verification" if lang == "en" else "Lab 1 验收结果"
        lines = [
            "PASS 15/15 checks passed",
            "README.md",
            "AGENTS.md",
            "docs/architecture.md",
            "policy rules",
            "trace rules",
        ]

    draw_text(draw, (x0 + 34, y0 + 112), title, F["title"], INK)
    y = y0 + 180
    for idx, line in enumerate(lines):
        if kind == "verify" and idx == 0:
            rounded(draw, (x0 + 34, y - 30, x0 + 360, y + 24), 18, "#DCFCE7")
            draw_text(draw, (x0 + 58, y + 6), line, F["body"], "#166534")
            y += 76
            continue
        draw.ellipse((x0 + 42, y - 14, x0 + 54, y - 2), fill=accent if kind != "verify" else "#16A34A")
        draw_text(draw, (x0 + 78, y), line, F["body"], "#30303D")
        y += 56
    return img


def render_screenshots() -> None:
    SCREENSHOT_OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "zh"):
        for kind in ("start", "step", "verify"):
            img = draw_chat_screenshot(lang, kind)
            img.save(SCREENSHOT_OUT / f"agent-{kind}-{lang}.png")


def main() -> int:
    module = load_loopath()
    for episode_idx in sorted(module.EPISODES):
        episode = module.EPISODES[episode_idx]
        for lang in ("zh", "en"):
            for step_idx in range(1, len(episode.steps) + 1):
                print(render_clip(module, lang, episode_idx, step_idx))
    render_screenshots()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
