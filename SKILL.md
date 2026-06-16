---
name: loopath
description: Interactive bilingual course skill for learning loop engineering through Loopath. Use when a user wants to start, continue, install, teach, study, verify, or be quizzed on the Loopath course; when they ask for an agent-guided course on coding-agent loops, harness design, AGENTS.md, action schemas, tool use, policy, traces, evals, or loop engineering; or when they provide the Loopath GitHub repo and want a conversational learning experience in Chinese or English.
---

# Loopath

Guide the user through Loopath as a conversational course, not as a static document.

## Language

Infer the default language from the user's current conversation:

- Mostly Chinese -> use `zh`.
- Mostly English -> use `en`.
- Mixed -> use the dominant language.
- If unclear, default to `en` and ask one short question.

Use the selected language for explanations, questions, quiz feedback, and verification cards.

## Course Flow

Use one small topic at a time:

1. Show the current episode and step.
2. Explain the background, purpose, and why this step matters.
3. Link or mention the relevant step clip.
4. Ask whether the user wants to continue, ask questions, start the lab, verify work, or take the quiz.
5. Do not dump the whole episode unless the user asks.

For deterministic course output, run:

```bash
python3 scripts/loopath.py step --episode 1 --step 1 --lang zh
python3 scripts/loopath.py step --episode 14 --step 5 --lang en
```

## Start or Continue

When the user says "start", "continue", "开启 episode", "学习 Loopath", or similar:

1. Detect language from the user message.
2. Run `scripts/loopath.py start --lang <zh|en>`.
3. Present the returned Markdown card.
4. Wait for the user's choice.

If the user asks for a specific episode or step, run:

```bash
python3 scripts/loopath.py step --episode <1-14> --step <n> --lang <zh|en>
```

## Lab

The lab should happen inside the agent conversation. Do not tell the user to manually create files unless they explicitly want to practice shell commands.

For Lab 1, ask for or choose a workspace path. If the user gives no path, propose `./loopath-dev`. Lab automation is currently implemented for Episode 1; for later episodes, use `course/loopath-course.md` as the lab reference and guide the user through the deliverables conversationally.

Create the lab project:

```bash
python3 scripts/loopath.py lab-create --episode 1 --repo <student_repo> --lang <zh|en>
```

Then summarize what files were created and ask the user to inspect or continue.

## Verification

After the user finishes or asks "check", "verify", "验收", "检查", run:

```bash
python3 scripts/loopath.py verify --episode 1 --repo <student_repo> --lang <zh|en>
```

Return the rendered verification card verbatim. If it fails, explain only the top missing items and offer to help fix them.

## Quiz

Run quiz one question at a time:

```bash
python3 scripts/loopath.py quiz --episode <1-14> --question 1 --lang <zh|en>
```

After the user answers, grade it:

```bash
python3 scripts/loopath.py grade --episode <1-14> --question 1 --answer "<answer>" --lang <zh|en>
```

Return the score, feedback, and reference answer. Then ask whether to continue to the next question.

## References

Load only when needed:

- `references/episode-01.zh.md` and `references/episode-01.en.md` for full Episode 1 teaching notes.
- `course/loopath-course.md` for the complete long-form course draft.
- `media/episode-XX/clips/<zh|en>/step-NN.mp4` for the matching step clip across Episodes 1-14.
