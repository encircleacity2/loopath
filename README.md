<div align="center">

# Loopath

### Learn how coding agents *actually* work — by building the loop yourself, inside your agent.

[![Watch the intro](media/intro/loopath-hero.gif)](https://youtu.be/VhyROHm6Fkc)

<sub>▶︎ **[Watch the full 2-min intro on YouTube](https://youtu.be/VhyROHm6Fkc)**</sub>

![MIT License](https://img.shields.io/badge/license-MIT-7763D9) ![Bilingual](https://img.shields.io/badge/中文%20%2F%20English-bilingual-7763D9) ![Runs in](https://img.shields.io/badge/runs%20in-Codex%20%2F%20Claude%20Code-0B0B10)

</div>

---

Most agent tutorials stop at `prompt → model → answer`. That's not the harness.

**Loopath** is an interactive course that lives *inside* Codex or Claude Code and teaches **loop engineering** — the runtime system around a coding agent — by having you build a tiny, complete one from scratch. It's nanoGPT, but for the agent loop.

It teaches one small step at a time, in your language, with a short narrated clip for every step. Not a doc you read — a course your agent runs.

## Install

```bash
# Claude Code
git clone --depth 1 https://github.com/encircleacity2/loopath ~/.claude/skills/loopath
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

> Videos stream from external hosting (YouTube + release assets), so the repo stays lean and `git clone` is fast — no media tooling required.

<details>
<summary><b>中文快速开始</b></summary>

**Loopath** 是一个在 Codex / Claude Code 里运行的中英双语互动课程，带你从零搭一个最小但完整的 coding-agent harness，真正理解 agent 背后的 **loop engineering**。

安装（Claude Code，Codex 把路径换成 `~/.codex/skills/loopath`）：

```bash
git clone --depth 1 https://github.com/encircleacity2/loopath ~/.claude/skills/loopath
```

重启 agent，然后说：**`用 $loopath 开始 Loopath 课程`**。skill 会根据你的语言自动选择中文或英文，视频和讲解都跟着切换。一次一个小课题，每个 step 配有旁白短视频，最后用 quiz 检验理解。导论视频：[English (YouTube)](https://youtu.be/VhyROHm6Fkc) · [中文](https://github.com/encircleacity2/loopath/releases/download/intro-v1/loopath-intro.zh.mp4)。

</details>

<details>
<summary><b>How the skill is built & course materials</b></summary>

Loopath is a **data-driven** skill — no scripts to run, nothing to execute. The agent *is* the course runtime:

- [`course/episodes.json`](course/episodes.json) — the bilingual source of truth: all 14 episodes' titles, theses, learning objectives, step-by-step teaching beats, lab deliverables/verification, Episode 1's ready-to-write file templates, and a per-episode quiz bank with reference answers.
- [`SKILL.md`](SKILL.md) — instructions that tell the agent to read that data, teach one step at a time, **build the lab by writing files itself** (via the editor's file tools), grade quizzes against the reference answers + rubric, and resolve videos from `video_sources.json`.
- [Full course draft](course/loopath-course.md) — the complete long-form course (full code listings + design discussion) the agent pulls from for depth, plus [`references/`](references) for Episode 1.

> Earlier versions shelled out to a `scripts/loopath.py` engine. That's gone: executing a freshly-cloned third-party script gets blocked by agent safety classifiers on first install, and everything it did (rendering cards, grading, scaffolding the lab) is something the model does better directly. Content lives in data; the model is the runtime.

Videos stream from external hosting, configured in [`video_sources.json`](video_sources.json):

- Bilingual step clips (Episode 1: 14 steps; Episodes 2–14: 5 steps each, `zh`+`en`, narrated) are hosted on GitHub Releases (`clips-v1`) and resolved via the `clip_url_template`. To switch to your own CDN (R2/TOS/etc.), edit that file.
- Intro: [English on YouTube](https://youtu.be/VhyROHm6Fkc) · [中文 (release asset)](https://github.com/encircleacity2/loopath/releases/download/intro-v1/loopath-intro.zh.mp4)

</details>

## License

MIT — share it, remix it, teach with it.
