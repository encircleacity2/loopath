#!/usr/bin/env python3
"""Cache Loopath course videos into an installed skill directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


GITHUB_API = "https://api.github.com/repos/encircleacity2/loopath/releases/tags/{tag}"
USER_AGENT = "loopath-video-cache/1.0"


@dataclass(frozen=True)
class Asset:
    name: str
    url: str
    size: int
    digest: str | None


def load_config(root: Path) -> dict:
    config_path = root / "video_sources.json"
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def release_assets(tag: str) -> list[Asset]:
    data = request_json(GITHUB_API.format(tag=tag))
    assets = []
    for raw in data.get("assets", []):
        if raw.get("content_type") != "video/mp4":
            continue
        assets.append(
            Asset(
                name=raw["name"],
                url=raw["browser_download_url"],
                size=int(raw["size"]),
                digest=raw.get("digest"),
            )
        )
    return assets


def language_allowed(name: str, languages: set[str]) -> bool:
    if languages == {"en", "zh"}:
        return True
    return any(f"-{lang}-" in name or f".{lang}." in name for lang in languages)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_complete(path: Path, asset: Asset, verify_hash: bool) -> bool:
    if not path.exists() or path.stat().st_size != asset.size:
        return False
    if verify_hash and asset.digest and asset.digest.startswith("sha256:"):
        return sha256(path) == asset.digest.split(":", 1)[1]
    return True


def download(asset: Asset, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".part")
    request = urllib.request.Request(asset.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, tmp.open("wb") as f:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    if tmp.stat().st_size != asset.size:
        raise RuntimeError(f"{asset.name}: expected {asset.size} bytes, got {tmp.stat().st_size}")
    tmp.replace(path)


def cache_release(
    *,
    tag: str,
    dest: Path,
    languages: set[str],
    force: bool,
    verify_existing: bool,
    dry_run: bool,
) -> tuple[int, int]:
    dest.mkdir(parents=True, exist_ok=True)
    assets = [asset for asset in release_assets(tag) if language_allowed(asset.name, languages)]
    downloaded = 0
    skipped = 0

    for asset in assets:
        out = dest / asset.name
        if not force and is_complete(out, asset, verify_existing):
            print(f"skip {asset.name}")
            skipped += 1
            continue
        if dry_run:
            print(f"would download {asset.name} -> {out}")
            continue
        print(f"download {asset.name}")
        try:
            download(asset, out)
        except urllib.error.URLError as exc:
            raise RuntimeError(f"{asset.name}: download failed: {exc}") from exc
        if asset.digest and asset.digest.startswith("sha256:"):
            expected = asset.digest.split(":", 1)[1]
            actual = sha256(out)
            if actual != expected:
                raise RuntimeError(f"{asset.name}: sha256 mismatch")
        downloaded += 1
    return downloaded, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Loopath skill root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--langs",
        default="all",
        choices=("all", "en", "zh"),
        help="Which language videos to cache. Defaults to all.",
    )
    parser.add_argument(
        "--section",
        default="all",
        choices=("all", "intro", "clips"),
        help="Which video section to cache. Defaults to all.",
    )
    parser.add_argument("--force", action="store_true", help="Redownload files even if sizes match.")
    parser.add_argument(
        "--verify-existing",
        action="store_true",
        help="Hash-check existing files before skipping them.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be downloaded.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    config = load_config(root)
    local = config.get("local_cache", {})
    tags = local.get("release_tags", {})
    cache_dir = root / local.get("dir", "media/local")
    languages = {"en", "zh"} if args.langs == "all" else {args.langs}

    jobs = []
    if args.section in {"all", "intro"}:
        jobs.append((tags.get("intro", "intro-v1"), cache_dir / "intro-v1"))
    if args.section in {"all", "clips"}:
        jobs.append((tags.get("clips", "clips-v1"), cache_dir / "clips-v1"))

    total_downloaded = 0
    total_skipped = 0
    for tag, dest in jobs:
        print(f"{tag} -> {dest}")
        downloaded, skipped = cache_release(
            tag=tag,
            dest=dest,
            languages=languages,
            force=args.force,
            verify_existing=args.verify_existing,
            dry_run=args.dry_run,
        )
        total_downloaded += downloaded
        total_skipped += skipped

    if args.dry_run:
        print("Dry run complete.")
    else:
        print(f"Video cache ready: downloaded={total_downloaded}, skipped={total_skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
