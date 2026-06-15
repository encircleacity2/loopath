#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loopath_motion import render_episode_01


if __name__ == "__main__":
    render_episode_01()
