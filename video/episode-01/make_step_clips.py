#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "loopath.py"
OUT = ROOT / "media" / "episode-01" / "clips"
W, H = 1280, 720
FPS = 24
DURATION = 5


def load_loopath():
    spec = importlib.util.spec_from_file_location("loopath_course_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def font(size: int):
    path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    if Path(path).exists():
        return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


TITLE = font(52)
BODY = font(28)
SMALL = font(22)


def wrap(text: str, width: int) -> list[str]:
    lines: list[str] = []
    cur = ""
    units = 0
    for ch in text:
        add = 1 if ord(ch) > 127 else 0.55
        if cur and units + add > width:
            lines.append(cur)
            cur = ch
            units = add
        else:
            cur += ch
            units += add
    if cur:
        lines.append(cur)
    return lines


def render_clip(module, lang: str, step_idx: int) -> Path:
    step = module.STEPS[step_idx - 1]
    out_dir = OUT / lang
    frame_dir = out_dir / f"step-{step_idx:02d}-frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"step-{step_idx:02d}.mp4"
    title = module.t(step.title, lang)
    purpose = module.t(step.purpose, lang)
    why = module.t(step.why, lang)
    accent = "#2563EB" if lang == "en" else "#0F766E"
    for i in range(DURATION * FPS):
        p = i / (DURATION * FPS - 1)
        img = Image.new("RGB", (W, H), "#F8FAFC")
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, W, 12), fill=accent)
        draw.rounded_rectangle((54, 46, W - 54, H - 46), radius=24, fill="white", outline="#E2E8F0", width=2)
        x_shift = int((1 - min(1, p * 2)) * -80)
        draw.text((92 + x_shift, 92), f"Episode 1 / Step {step_idx:02d}", font=SMALL, fill=accent)
        draw.text((92 + x_shift, 145), title, font=TITLE, fill="#0F172A")
        y = 250
        label1 = "目的" if lang == "zh" else "Purpose"
        label2 = "为什么重要" if lang == "zh" else "Why it matters"
        draw.text((92, y), label1, font=SMALL, fill=accent)
        y += 40
        for line in wrap(purpose, 38)[:3]:
            draw.text((92, y), line, font=BODY, fill="#334155")
            y += 38
        y += 22
        draw.text((92, y), label2, font=SMALL, fill=accent)
        y += 40
        for line in wrap(why, 42)[:3]:
            draw.text((92, y), line, font=BODY, fill="#334155")
            y += 38
        # animated mini loop
        cx0, cy = 790, 470
        nodes = ["Context", "Action", "Policy", "Trace"]
        for n, node in enumerate(nodes):
            x = cx0 + (n % 2) * 210
            yy = cy + (n // 2) * 90
            fill = accent if p > n * 0.17 else "#E2E8F0"
            draw.rounded_rectangle((x, yy, x + 170, yy + 58), radius=18, fill=fill)
            draw.text((x + 24, yy + 18), node, font=SMALL, fill="white" if fill == accent else "#334155")
        img.save(frame_dir / f"frame-{i:04d}.png")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(frame_dir / "frame-%04d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "20",
            str(out),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out


def main() -> int:
    module = load_loopath()
    for lang in ("zh", "en"):
        for idx in range(1, len(module.STEPS) + 1):
            path = render_clip(module, lang, idx)
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
