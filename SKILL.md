---
name: loopath
description: Interactive bilingual course skill for learning loop engineering through Loopath. Use when a user wants to start, continue, install, teach, study, verify, or be quizzed on the Loopath course; when they ask for an agent-guided course on coding-agent loops, harness design, AGENTS.md, action schemas, tool use, policy, traces, evals, or loop engineering; or when they provide the Loopath GitHub repo and want a conversational learning experience in Chinese or English.
---

# Loopath

Guide the user through Loopath as a conversational course, **not** as a static document. You are the course runtime: you read structured course data, teach one small step at a time, build the lab by writing files yourself, and grade quizzes against reference answers.

There is no course engine script to run. All course content lives in data and Markdown in this repo — read it with your normal file tools. (Earlier versions shelled out to `scripts/loopath.py`; that script no longer exists and must not be recreated.) The only script is the optional video-cache helper, used after the learner opts in.

## Course data

The single source of truth is **`course/episodes.json`**. Read it once at the start of a session and keep it in context. Its shape:

- `course` — `name`, bilingual `tagline`, the `loop` string, `episode_count`, and `open_ended_rubric` (use this rubric verbatim when grading short-answer questions).
- `episodes[]` — 14 entries. Each has: `n`, `week`, `title{zh,en}`, `thesis{zh,en}`, `objectives{zh,en}`, `steps[]`, `lab`, and `quiz[]`.
  - `steps[]` — Episode 1 has 14 steps; Episodes 2–14 have 5. Each step has `title`, `background`, `purpose`, `why`, all `{zh,en}`.
  - `lab` — `deliverables{zh,en}`, `verify{zh,en}`, `dir` (path to this episode's on-disk lab templates), `files[]` (workspace-relative paths to write), optional `dirs[]` (workspace dirs to create), and optional `integrations[]` (`*.snippet.md` files describing edits to *earlier* files).
  - `quiz[]` — each is `multiple_choice` (with `choices{zh,en}` and `answer`) or `short_answer` (with `keywords[]`); both carry `reference{zh,en}`.

For deeper teaching beyond the step beats, read the long-form source:
- `references/episode-01.zh.md`, `references/episode-01.en.md` — full Episode 1 notes.
- `course/loopath-course.md` — the complete long-form course (Chinese), with full code listings, design discussions, and the per-episode quiz bank. Load the relevant section on demand.

## Language

Infer the default language from the user's current conversation:

- Mostly Chinese → `zh`. Mostly English → `en`. Mixed → the dominant one. Unclear → default to `en` and ask one short question.

Use the selected language for all explanations, questions, quiz feedback, and cards — and serve the matching-language video (see below).

## Video

Videos are configured in **`video_sources.json`**. Read that file and resolve links yourself. The repo stays lean by default; full local video caching is opt-in.

### Local cache prompt

At the very start of a Codex tutorial session, before the first lesson step, check `local_cache` in `video_sources.json`:

1. Resolve `local_cache.dir` relative to the skill root.
2. If the directory is missing or has fewer than `local_cache.expected_mp4_count` `.mp4` files, ask the learner one short question in their language:
   - zh: "要不要先把全课程视频下载到本地？大约 {estimated_size_mb} MB。下载后我会在每一步直接嵌入可播放视频；不下载也可以继续用远程链接。"
   - en: "Do you want to cache all course videos locally first? It is about {estimated_size_mb} MB. After that I can embed playable video in each step; otherwise we can continue with remote links."
3. If the learner says yes, run:

```bash
python3 scripts/cache_videos.py --root <skill_root> --langs all
```

4. If the learner says no, or the download fails, continue with remote links. Do not block the lesson on media.

If the local cache is complete, use it without asking again.

### Resolving a video

- **Intro**: use `local_cache.intro[<lang>]` if the file exists; otherwise use `intro[<lang>]`.
- **Per-step clip**: use `local_cache.clip_path_template` if the file exists; otherwise fill `clip_url_template` with `ep`, `step`, `lang` (zero-padded where the template uses `{ep:02d}`/`{step:02d}`).
- **Codex rendering**: when the selected video is a local `.mp4` path, present it as playable Markdown image syntax, e.g. `![Loopath Episode 2 Step 1](/absolute/path.mp4)`. When it is remote, present it as a normal Markdown link.

Surface the clip for the current step, and offer the intro at the very start. If `video_sources.json` is missing or a link can't be formed, just teach without the video — never block on media.

## Course flow

One small topic at a time:

1. State the current episode and step (e.g. "Episode 2 / Step 3").
2. Teach from the step's `background` → `purpose` → `why`, in the user's language. Expand conversationally; don't just dump the JSON fields verbatim. Pull richer detail from `course/loopath-course.md` when the user wants depth.
3. Offer the matching step-clip link.
4. Ask what's next: continue to the next step, ask a question, start the lab, run verification, or take the quiz.
5. Do **not** dump a whole episode unless the user asks.

At the very start (user says "start", "continue", "开始 / 学习 Loopath", or similar): detect language, give a short bilingual-aware welcome that names the course scope (14 episodes), handle the local video-cache prompt above, offer the intro video, and recommend starting at Episode 1 / Step 1. Then wait for the user's choice.

## Lab

The lab happens **inside the conversation**. Build it for the user with the **Write tool** — don't tell them to type shell commands or run a generator, unless they explicitly want to practice the shell.

Every episode ships **ready-to-write, English lab templates on disk** under `lab.dir` (e.g. `course/labs/episode-03/`). The files there are laid out exactly as they belong in the student's project (`src/loopath/tools.py`, `tests/test_tools.py`, …). Don't hand-translate code from the course doc — copy these templates.

To run a lab:

1. Ask for a workspace path the first time (propose `./loopath-dev` if none given); reuse it for later episodes so the project accumulates.
2. Ensure any `lab.dirs` exist in the workspace.
3. For each path in `lab.files`: read `<skill_root>/<lab.dir>/<path>` and write it to `<workspace>/<path>` with the Write tool. (The same workspace-relative path applies on both sides.)
4. For each entry in `lab.integrations` (e.g. `loop_policy.snippet.md`): read that file from `lab.dir` — it describes a small **edit to an earlier file** (like wiring policy into `loop.py`). Apply the edit with the Edit tool and explain it; do **not** copy a snippet file into the workspace verbatim.
5. Walk the user through each file in chat — what it is, why it exists, the design tradeoffs. Pull deeper narration from the matching section of `course/loopath-course.md` when they want it.

Note: some files legitimately evolve across episodes — e.g. Episode 9's `src/loopath/tracing.py` supersedes Episode 4's. Writing the newer template over the older file is expected.

After building, run the lab's `verify` conversationally: check the deliverables exist and meet the `verify` criteria (required files present, key sentences in docs, or run `pytest` if the user has a working ≥3.11 environment). Report what passed and what's missing — don't just claim success.

## Quiz

Run quizzes **one question at a time**, reading from the episode's `quiz[]`:

1. Present one question (for `multiple_choice`, include `choices` in the user's language). Wait for the answer.
2. Grade it yourself:
   - `multiple_choice` — compare against `answer`. Correct → 10/10, otherwise 0/10, and explain why.
   - `short_answer` — grade with the `course.open_ended_rubric` (correctness 4 / specificity 3 / tradeoff awareness 2 / clarity 1). Use `keywords` only as hints to what a strong answer covers, not as a literal substring count. **Quote a specific sentence from the user's answer as evidence** — never give vague praise.
3. Show the score, your feedback, and the `reference` answer in the user's language.
4. Ask whether to continue to the next question.

## Quick map for navigation

- Start / welcome → read `episodes.json`, detect language, offer intro from `video_sources.json`.
- "Episode N step M" → `episodes[N-1].steps[M-1]`.
- "Start the lab" → `episodes[N-1].lab`: copy each `files[]` template from `lab.dir` into the workspace, then apply any `integrations[]` snippets.
- "Quiz me" → iterate `episodes[N-1].quiz`, grade against `reference` + rubric.
