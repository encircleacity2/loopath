#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "media" / "intro"
FRAME_DIR = OUT_DIR / "frames"
W, H = 1920, 1080
FPS = 30
DURATION = 42


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


FONT_TITLE = font(88, True)
FONT_H2 = font(48, True)
FONT_BODY = font(34)
FONT_SMALL = font(26)
FONT_MONO = font(28)


def ease(x: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, x)))


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill=(15, 23, 42)) -> None:
    draw.text(xy, text, font=fnt, fill=fill)


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width=1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def scene_for_time(t: float) -> int:
    return min(5, int(t // 7))


def render_frame(i: int) -> Path:
    t = i / FPS
    scene = scene_for_time(t)
    local = t - scene * 7
    p = ease(local / 7)
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    accent = ["#2563EB", "#059669", "#7C3AED", "#EA580C", "#0F766E", "#111827"][scene]
    draw.rectangle((0, 0, W, 18), fill=accent)
    rounded(draw, (92, 76, 1828, 1004), 32, "white", "#E2E8F0", 2)

    # Moving loop rail.
    rail_y = 840
    draw.line((250, rail_y, 1670, rail_y), fill="#CBD5E1", width=6)
    nodes = ["Context", "Action", "Policy", "Tool", "Trace", "Eval"]
    for idx, name in enumerate(nodes):
        x = 250 + idx * 284
        pulse = 0.5 + 0.5 * math.sin(t * 2.2 + idx)
        color = accent if idx <= scene else "#E2E8F0"
        rounded(draw, (x - 74, rail_y - 42, x + 74, rail_y + 42), 24, color, None)
        draw_text(draw, (x - 48, rail_y - 13), name, FONT_SMALL, "white" if idx <= scene else "#334155")
        if idx == scene:
            r = int(56 + pulse * 10)
            draw.ellipse((x - r, rail_y - r, x + r, rail_y + r), outline=accent, width=4)

    if scene == 0:
        draw_text(draw, (145, 150), "LOOPATH", FONT_SMALL, accent)
        draw_text(draw, (145, 250), "Loopath", FONT_TITLE)
        draw_text(draw, (145, 370), "A tiny reference implementation", FONT_H2)
        draw_text(draw, (145, 430), "for loop engineering.", FONT_H2, "#334155")
        for idx, chip in enumerate(["coding agents", "harness", "trace", "eval"]):
            x = 145 + idx * 260 + int(12 * math.sin(t * 2 + idx))
            rounded(draw, (x, 570, x + 220, 630), 30, "#DBEAFE", "#BFDBFE", 2)
            draw_text(draw, (x + 28, 588), chip, FONT_SMALL, "#1D4ED8")
    elif scene == 1:
        draw_text(draw, (145, 150), "FROM API CALLS", FONT_SMALL, accent)
        draw_text(draw, (145, 245), "Not a wrapper.", FONT_TITLE)
        draw_text(draw, (145, 355), "A controlled action loop.", FONT_H2, "#334155")
        code_x = 1070 - int(80 * (1 - p))
        rounded(draw, (code_x, 235, 1745, 610), 24, "#0F172A")
        lines = ["prompt + api = answer", "", "action + policy + trace", "+ eval = agent runtime"]
        for n, line in enumerate(lines):
            draw_text(draw, (code_x + 42, 300 + n * 58), line, FONT_MONO, "#D1FAE5")
    elif scene == 2:
        draw_text(draw, (145, 150), "THE COURSE IS A SKILL", FONT_SMALL, accent)
        draw_text(draw, (145, 245), "Install. Ask. Learn.", FONT_TITLE)
        draw_text(draw, (145, 360), "The agent teaches one small topic at a time.", FONT_H2, "#334155")
        for idx, label in enumerate(["Explain", "Lab", "Verify", "Quiz"]):
            y = 490 + idx * 76
            x = 1020 + int(40 * math.sin(t * 2 + idx))
            rounded(draw, (x, y, x + 580, y + 56), 18, "#F3E8FF", "#DDD6FE", 2)
            draw_text(draw, (x + 28, y + 14), label, FONT_BODY, "#5B21B6")
    elif scene == 3:
        draw_text(draw, (145, 150), "BILINGUAL BY DEFAULT", FONT_SMALL, accent)
        draw_text(draw, (145, 245), "中文 / English", FONT_TITLE)
        draw_text(draw, (145, 360), "The skill follows the user's conversation language.", FONT_H2, "#334155")
        rounded(draw, (1020, 260, 1660, 390), 24, "#ECFDF5", "#A7F3D0", 2)
        rounded(draw, (1060, 430, 1700, 560), 24, "#EFF6FF", "#BFDBFE", 2)
        draw_text(draw, (1060, 304), "默认语言：中文", FONT_H2, "#047857")
        draw_text(draw, (1100, 474), "Default language: English", FONT_H2, "#1D4ED8")
    elif scene == 4:
        draw_text(draw, (145, 150), "LABS HAPPEN IN THE AGENT", FONT_SMALL, accent)
        draw_text(draw, (145, 245), "No copy-paste marathon.", FONT_TITLE)
        draw_text(draw, (145, 360), "The agent creates files, then runs verification.", FONT_H2, "#334155")
        rounded(draw, (1030, 260, 1710, 620), 24, "#0F172A")
        lines = [
            "$ loopath lab-create --repo ./loopath-dev",
            "created README.md",
            "created AGENTS.md",
            "created docs/architecture.md",
            "verification: PASS 15/15",
        ]
        for n, line in enumerate(lines):
            color = "#D1FAE5" if n != 4 else "#86EFAC"
            draw_text(draw, (1070, 320 + n * 56), line, FONT_MONO, color)
    else:
        draw_text(draw, (145, 150), "WHAT EPISODE 1 COVERS", FONT_SMALL, accent)
        draw_text(draw, (145, 245), "Boundaries first.", FONT_TITLE)
        topics = ["README", "AGENTS.md", "architecture", "lab verifier", "quiz rubric"]
        for idx, topic in enumerate(topics):
            x = 145 + (idx % 3) * 500
            y = 430 + (idx // 3) * 120
            rounded(draw, (x, y, x + 410, y + 80), 22, "#F1F5F9", "#CBD5E1", 2)
            draw_text(draw, (x + 30, y + 24), topic, FONT_BODY, "#0F172A")

    path = FRAME_DIR / f"frame-{i:04d}.png"
    img.save(path)
    return path


def make_synthetic_music(path: Path, duration: int) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=196:duration={duration}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=392:duration={duration}",
            "-filter_complex",
            "[0:a]volume=0.08[a0];[1:a]volume=0.04[a1];[a0][a1]amix=inputs=2,afade=t=in:st=0:d=2,afade=t=out:st=39:d=3[a]",
            "-map",
            "[a]",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the Loopath README intro video.")
    parser.add_argument("--music", default=str(OUT_DIR / "music_bed.m4a"))
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    total_frames = DURATION * FPS
    for i in range(total_frames):
        render_frame(i)
    silent = OUT_DIR / "loopath-intro-silent.mp4"
    final = OUT_DIR / "loopath-intro.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(FRAME_DIR / "frame-%04d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            str(silent),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    music = Path(args.music)
    if not music.exists():
        make_synthetic_music(music, DURATION)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent),
            "-i",
            str(music),
            "-t",
            str(DURATION),
            "-filter_complex",
            "[1:a]volume=0.45,afade=t=out:st=39:d=3[a]",
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(final),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
