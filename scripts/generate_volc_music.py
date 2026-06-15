#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests
from volcengine.Credentials import Credentials
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request


def load_config() -> dict:
    path = Path.home() / ".explainer-video" / "config.json"
    if not path.exists():
        raise SystemExit("Missing ~/.explainer-video/config.json")
    cfg = json.loads(path.read_text())
    if not cfg.get("music_enabled"):
        raise SystemExit("Music is disabled in ~/.explainer-video/config.json")
    for key in ("volc_music_ak", "volc_music_sk"):
        if not cfg.get(key):
            raise SystemExit(f"Missing {key} in ~/.explainer-video/config.json")
    return cfg


def call_volc(cfg: dict, action: str, body_dict: dict) -> dict:
    body = json.dumps(body_dict, ensure_ascii=False)
    req = Request()
    req.method = "POST"
    req.scheme = "https"
    req.host = "open.volcengineapi.com"
    req.path = "/"
    req.query = {"Action": action, "Version": "2024-08-12"}
    req.headers = {"Content-Type": "application/json", "Host": req.host}
    req.body = body
    SignerV4.sign(
        req,
        Credentials(
            cfg["volc_music_ak"],
            cfg["volc_music_sk"],
            "imagination",
            "cn-beijing",
        ),
    )
    response = requests.post(
        f"https://{req.host}/",
        params=req.query,
        data=body.encode("utf-8"),
        headers=req.headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if "Error" in data:
        raise RuntimeError(data["Error"])
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate instrumental BGM with Volcengine music.")
    parser.add_argument("--out", required=True, help="Output wav path.")
    parser.add_argument("--duration", type=int, default=45)
    parser.add_argument(
        "--prompt",
        default=(
            "Cinematic uplifting ambient instrumental for an educational AI engineering course launch. "
            "Modern electronic pulses, soft synth arpeggios, confident but not aggressive, "
            "clean technology feel, gentle build, no vocals, no lyrics, instrumental only."
        ),
    )
    parser.add_argument("--poll-seconds", type=int, default=8)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    cfg = load_config()
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    submit = call_volc(
        cfg,
        "GenBGM",
        {
            "Text": args.prompt,
            "Duration": max(30, min(120, args.duration)),
            "Version": "v5.0",
            "EnableInputRewrite": False,
        },
    )
    task_id = submit["Result"]["TaskID"]
    deadline = time.time() + args.timeout_seconds

    while time.time() < deadline:
        status_response = call_volc(cfg, "QuerySong", {"TaskID": task_id})
        result = status_response["Result"]
        status = result["Status"]
        if status == 2:
            detail = result["SongDetail"]
            audio_url = detail["AudioUrl"]
            audio = requests.get(audio_url, timeout=60)
            audio.raise_for_status()
            out.write_bytes(audio.content)
            print(out)
            return 0
        if status == 3:
            raise RuntimeError(f"Music task failed: {result.get('FailureReason')}")
        time.sleep(args.poll_seconds)

    raise TimeoutError(f"Music generation timed out for task {task_id}")


if __name__ == "__main__":
    raise SystemExit(main())
