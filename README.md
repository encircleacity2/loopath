<div align="center">

# Loopath

### Learn how coding agents *actually* work — by building the loop yourself, inside your agent.

[![Watch the intro](media/intro/loopath-hero.gif)](https://github.com/encircleacity2/loopath/releases/download/intro-v1/loopath-intro.en.mp4)

<sub>▶︎ **[Watch the full 2-min intro — English](https://github.com/encircleacity2/loopath/releases/download/intro-v1/loopath-intro.en.mp4) · [中文](https://github.com/encircleacity2/loopath/releases/download/intro-v1/loopath-intro.zh.mp4)**</sub>

![MIT License](https://img.shields.io/badge/license-MIT-7763D9) ![Bilingual](https://img.shields.io/badge/中文%20%2F%20English-bilingual-7763D9) ![Runs in](https://img.shields.io/badge/runs%20in-Codex%20%2F%20Claude%20Code-0B0B10)

</div>

---

Most agent tutorials stop at `prompt → model → answer`. That's not the harness.

**Loopath** is an interactive course that lives *inside* Codex or Claude Code and teaches **loop engineering** — the runtime system around a coding agent — by having you build a tiny, complete one from scratch. It's nanoGPT, but for the agent loop.

It teaches one small step at a time, in your language, with a short narrated clip for every step. Not a doc you read — a course your agent runs.

## Install

```bash
# Claude Code
git clone https://github.com/encircleacity2/loopath ~/.claude/skills/loopath
# Codex — same repo, swap the path:  ~/.codex/skills/loopath
```

Restart your agent, then say:

> **Use $loopath to start the course.**

The skill auto-detects whether you're writing in **中文 or English** and teaches in that language — matching video *and* content.

## The loop you'll build

```
context → action → policy → tool → observation → trace → eval → ↺
```

- Why a harness is a **runtime system**, not an API wrapper
- Structured **action schemas**, **tool registries**, and **policy gates**
- **Traces**, **evals**, **loop engineering**, and **self-repair**
- **14 episodes** → one small, runnable, inspectable agent harness you can explain in an interview

## How it works

- 🎬 **One step at a time** — each with a short narrated clip (中文 / English)
- 🌐 **Fully bilingual** — auto-routes language for video and explanations
- 🧪 **Hands-on lab** built conversationally inside your agent — no setup busywork
- ❓ **Quiz with grading** to check you actually understood it

## Getting started in 20 seconds

1. `git clone … ~/.claude/skills/loopath` (above)
2. Restart your agent
3. Say *"Use $loopath to start the course"*
4. Watch the intro, then learn the loop one step at a time

> Built with [Git LFS](https://git-lfs.com) for the video assets — `git lfs install` once if you don't have it, so the clips download on clone.

<details>
<summary><b>中文快速开始</b></summary>

**Loopath** 是一个在 Codex / Claude Code 里运行的中英双语互动课程，带你从零搭一个最小但完整的 coding-agent harness，真正理解 agent 背后的 **loop engineering**。

安装（Claude Code，Codex 把路径换成 `~/.codex/skills/loopath`）：

```bash
git clone https://github.com/encircleacity2/loopath ~/.claude/skills/loopath
```

重启 agent，然后说：**`用 $loopath 开始 Loopath 课程`**。skill 会根据你的语言自动选择中文或英文，视频和讲解都跟着切换。一次一个小课题，每个 step 配有旁白短视频，最后用 quiz 检验理解。导论视频：[中文](https://github.com/encircleacity2/loopath/releases/download/intro-v1/loopath-intro.zh.mp4) · [English](https://github.com/encircleacity2/loopath/releases/download/intro-v1/loopath-intro.en.mp4)。

</details>

<details>
<summary><b>Maintainer commands & course materials</b></summary>

Deterministic course engine (the skill calls this for you):

```bash
python3 scripts/loopath.py start --lang en
python3 scripts/loopath.py step --episode 1 --step 1 --lang en   # any episode 1-14
python3 scripts/loopath.py lab-create --repo ./loopath-dev --lang en
python3 scripts/loopath.py quiz --episode 10 --question 1 --lang en
python3 scripts/loopath.py grade --episode 10 --question 1 --answer "B" --lang en
```

- [Full course draft](course/loopath-course.md)
- Bilingual step clips: `media/episode-01/` … `media/episode-14/` (Episode 1: 14 steps; Episodes 2–14: 5 steps each), both `zh` and `en`, narrated.
- Intro videos: `media/intro/loopath-intro.{en,zh}.mp4`

</details>

## License

MIT — share it, remix it, teach with it.
