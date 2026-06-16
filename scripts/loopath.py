#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Step:
    title: dict[str, str]
    background: dict[str, str]
    purpose: dict[str, str]
    why: dict[str, str]


@dataclass(frozen=True)
class Episode:
    title: dict[str, str]
    steps: list[Step]


@dataclass(frozen=True)
class EpisodeSpec:
    title: dict[str, str]
    thesis: dict[str, str]
    core: dict[str, str]
    lab: dict[str, str]
    verify: dict[str, str]
    quiz: dict[str, str]


EPISODE1_STEPS: list[Step] = [
    Step(
        {"zh": "Loopath 是什么", "en": "What Loopath Is"},
        {
            "zh": "很多人会使用 Codex、Claude Code 或 Cursor，但并不清楚这些工具背后的 agent loop 是如何被约束和验证的。",
            "en": "Many people use Codex, Claude Code, or Cursor without seeing the agent loop that constrains and verifies the work.",
        },
        {
            "zh": "把 Loopath 定位成一个小而完整的 loop engineering 参考实现。",
            "en": "Frame Loopath as a small reference for loop engineering.",
        },
        {
            "zh": "先定义项目定位，后面的 README、AGENTS.md、architecture、lab 和 verifier 才会服务同一个目标。",
            "en": "A clear frame keeps README, AGENTS.md, architecture, labs, and verification aligned.",
        },
    ),
    Step(
        {"zh": "最终会构建什么", "en": "What You Will Build"},
        {
            "zh": "API 调用只能得到模型输出，不能自动形成一个可审查、可追踪、可评测的行动系统。",
            "en": "An API call returns model output, but not an auditable, traceable, evaluable action system.",
        },
        {
            "zh": "理解最终系统能力：context -> action -> policy -> tool -> observation -> trace -> eval。",
            "en": "Understand the target system: context -> action -> policy -> tool -> observation -> trace -> eval.",
        },
        {
            "zh": "先看终局，才能知道第一节课为什么先搭边界，而不是直接写 action parser。",
            "en": "Seeing the end state explains why Episode 1 starts with boundaries instead of an action parser.",
        },
    ),
    Step(
        {"zh": "Harness 不是 API Wrapper", "en": "A Harness Is Not an API Wrapper"},
        {
            "zh": "Wrapper 只处理文本输入输出；harness 处理真实行动、权限、观察和评测。",
            "en": "A wrapper handles text input and output; a harness handles action, permission, observation, and evaluation.",
        },
        {
            "zh": "区分 model wrapper 和 agent runtime。",
            "en": "Separate a model wrapper from an agent runtime.",
        },
        {
            "zh": "这个区别决定后续模块是否需要 policy、trace 和 eval。",
            "en": "This distinction determines why policy, trace, and eval must exist.",
        },
    ),
    Step(
        {"zh": "四层边界", "en": "Four Boundaries"},
        {
            "zh": "Model、Agent、Harness、World 混在一起时，失败很难定位。",
            "en": "When Model, Agent, Harness, and World are mixed together, failures are hard to diagnose.",
        },
        {
            "zh": "建立模型负责想、harness 负责执行边界的心智模型。",
            "en": "Build the mental model: the model proposes; the harness controls execution.",
        },
        {
            "zh": "模型不应该直接修改世界，它应该提出结构化 action。",
            "en": "The model should not directly mutate the world; it should propose structured actions.",
        },
    ),
    Step(
        {"zh": "Lab 1 目标", "en": "Lab 1 Target"},
        {
            "zh": "第一节课的产物不是模型能力，而是后续所有 lab 的工程边界。",
            "en": "Episode 1 produces engineering boundaries, not model capability.",
        },
        {
            "zh": "创建项目骨架、README、AGENTS.md、architecture.md、pyproject.toml。",
            "en": "Create the project skeleton, README, AGENTS.md, architecture.md, and pyproject.toml.",
        },
        {
            "zh": "先有稳定结构，agent 才能在后续对话中安全继续创建文件和修改代码。",
            "en": "A stable structure lets the agent safely continue creating files and code in later steps.",
        },
    ),
    Step(
        {"zh": "创建目录结构", "en": "Create the Directory Structure"},
        {
            "zh": "传统课程让学生手敲命令；Loopath skill 会让 agent 直接创建 lab 项目。",
            "en": "Traditional courses ask students to type commands; the Loopath skill lets the agent create the lab project.",
        },
        {
            "zh": "理解每个目录为什么存在：src、tests、demo_repos、prompts、evals、traces、docs。",
            "en": "Understand why each directory exists: src, tests, demo_repos, prompts, evals, traces, docs.",
        },
        {
            "zh": "目录本身就是 harness 设计的一部分：代码、评测、trace、文档从第一天就分层。",
            "en": "The directory structure is part of the harness design: code, evals, traces, and docs are separated from day one.",
        },
    ),
    Step(
        {"zh": "README 是产品承诺", "en": "README as Product Promise"},
        {
            "zh": "README 不只是说明文件，它决定读者和 agent 如何理解项目目标。",
            "en": "README is not just documentation; it shapes how humans and agents understand the project goal.",
        },
        {
            "zh": "写清楚 Loopath 是 tiny reference implementation，不是完整 agent framework。",
            "en": "State that Loopath is a tiny reference implementation, not a full agent framework.",
        },
        {
            "zh": "边界越清楚，后续 agent 越不容易把项目做歪。",
            "en": "Clear boundaries reduce the chance that future agents take the project in the wrong direction.",
        },
    ),
    Step(
        {"zh": "Architecture 写核心约束", "en": "Architecture as Core Constraints"},
        {
            "zh": "直接写 action parser 会只解决局部问题，architecture 先定义完整运行路径。",
            "en": "Jumping into an action parser solves a local problem; architecture defines the whole runtime path first.",
        },
        {
            "zh": "写下最重要约束：model does not directly mutate the world。",
            "en": "Write the key constraint: the model does not directly mutate the world.",
        },
        {
            "zh": "这句话决定后续 action schema、policy、tool、trace、eval 的存在理由。",
            "en": "That sentence explains why action schema, policy, tools, traces, and evals exist.",
        },
    ),
    Step(
        {"zh": "画出 Core Loop", "en": "Draw the Core Loop"},
        {
            "zh": "Agent 不是一次性回答，而是在观察结果后决定下一步。",
            "en": "An agent is not a one-shot answer; it decides the next step after observing results.",
        },
        {
            "zh": "把 context、action、policy、tool、observation、trace、eval 画成闭环。",
            "en": "Draw context, action, policy, tool, observation, trace, and eval as a loop.",
        },
        {
            "zh": "图可以让后续每个模块都知道自己处在 loop 的哪个位置。",
            "en": "The diagram tells every later module where it sits in the loop.",
        },
    ),
    Step(
        {"zh": "AGENTS.md 是场景工作协议", "en": "AGENTS.md as Scenario Protocol"},
        {
            "zh": "AGENTS.md 不只用于代码开发，它把日常生产力场景里的隐性规则显性化。",
            "en": "AGENTS.md is not only for coding; it makes implicit working rules explicit for productivity scenarios.",
        },
        {
            "zh": "定义 Goal、Can do、Must not do、Done when。",
            "en": "Define Goal, Can do, Must not do, and Done when.",
        },
        {
            "zh": "没有 AGENTS.md，agent 每次都靠当前 prompt 猜你的偏好和边界。",
            "en": "Without AGENTS.md, the agent has to infer your preferences and boundaries from the current prompt.",
        },
    ),
    Step(
        {"zh": "pyproject.toml", "en": "pyproject.toml"},
        {
            "zh": "Python 项目需要一个统一配置入口，声明项目名、版本、依赖、测试配置和 CLI。",
            "en": "A Python project needs one configuration entry point for name, version, dependencies, tests, and CLI.",
        },
        {
            "zh": "先写最小 pyproject，不引入复杂依赖。",
            "en": "Start with a minimal pyproject without unnecessary dependencies.",
        },
        {
            "zh": "越早建立项目身份，后续越容易安装、测试和验证。",
            "en": "A clear project identity makes later installation, testing, and verification easier.",
        },
    ),
    Step(
        {"zh": "Verifier 自动验收", "en": "Automated Verification"},
        {
            "zh": "正式课程体验不应该让用户复制大段命令，而应该由 agent 自动运行 verifier。",
            "en": "A real course should not ask users to copy long commands; the agent should run the verifier.",
        },
        {
            "zh": "运行 Lab 1 verifier，输出检测卡片。",
            "en": "Run the Lab 1 verifier and render a result card.",
        },
        {
            "zh": "verification 是 loop engineering 的关键：没有自动验收，就无法稳定改进。",
            "en": "Verification is central to loop engineering: without it, improvement cannot be stable.",
        },
    ),
    Step(
        {"zh": "Agent Rubric 检查", "en": "Agent Rubric Review"},
        {
            "zh": "脚本检查结构和关键词，agent rubric 检查解释质量和设计取舍。",
            "en": "Scripts check structure and required text; an agent rubric checks explanation quality and design tradeoffs.",
        },
        {
            "zh": "让 agent 返回 score、evidence、missing requirements、next improvement。",
            "en": "Ask the agent to return score, evidence, missing requirements, and one next improvement.",
        },
        {
            "zh": "脚本和 agent 评分结合，可以同时覆盖确定性和开放性学习目标。",
            "en": "Combining scripts and agent grading covers both deterministic and open-ended learning goals.",
        },
    ),
    Step(
        {"zh": "Quiz 一问一答", "en": "One-question-at-a-time Quiz"},
        {
            "zh": "一次展示太多题会打断学习节奏。",
            "en": "Showing too many questions at once breaks the learning rhythm.",
        },
        {
            "zh": "每次只问一题，用户回答后给参考答案和评分。",
            "en": "Ask one question at a time, then provide the reference answer and score.",
        },
        {
            "zh": "这让 quiz 像 tutor，而不是静态练习册。",
            "en": "This makes quiz feel like tutoring, not a static worksheet.",
        },
    ),
]


EPISODE_SPECS: dict[int, EpisodeSpec] = {
    2: EpisodeSpec(
        {"zh": "Action Schema", "en": "Action Schema"},
        {
            "zh": "自然语言不能直接驱动工具，模型输出必须先变成可验证的动作协议。",
            "en": "Natural language cannot safely drive tools; model output must become a validated action protocol.",
        },
        {
            "zh": "用 type discriminator 设计 read_file、search、run_command、edit_file、final_answer。",
            "en": "Use a type discriminator for read_file, search, run_command, edit_file, and final_answer.",
        },
        {
            "zh": "实现 actions.py 和 parser tests，把非法 JSON、未知 action、缺失字段分开处理。",
            "en": "Implement actions.py and parser tests that separate invalid JSON, unknown actions, and missing fields.",
        },
        {
            "zh": "运行 tests/test_actions.py；能解释 parse error 和 tool execution error 的区别。",
            "en": "Run tests/test_actions.py and explain parse errors versus tool execution errors.",
        },
        {
            "zh": "判断 action set 为什么要小，并设计 list_files action 的安全边界。",
            "en": "Explain why the action set stays small and design safety boundaries for list_files.",
        },
    ),
    3: EpisodeSpec(
        {"zh": "Tool Registry", "en": "Tool Registry"},
        {
            "zh": "Tool use 不是普通函数调用，而是 agent 可控行动空间的边界。",
            "en": "Tool use is not plain function calling; it is the boundary of the agent's action space.",
        },
        {
            "zh": "统一 ToolResult，集中 workspace path resolver，并实现 read/search/run/edit。",
            "en": "Create ToolResult, centralize workspace path resolution, and implement read/search/run/edit.",
        },
        {
            "zh": "实现 tools.py 和 tests/test_tools.py，覆盖越界路径、搜索行号、命令失败和写文件。",
            "en": "Implement tools.py and tests/test_tools.py for path escape, search line numbers, command failure, and writing.",
        },
        {
            "zh": "运行 tests/test_tools.py；失败也必须成为 observation，而不是直接中断 loop。",
            "en": "Run tests/test_tools.py; failures must become observations instead of crashing the loop.",
        },
        {
            "zh": "回答 ToolResult metadata、搜索行号、workspace resolver 为什么重要。",
            "en": "Explain why ToolResult metadata, search line numbers, and workspace resolvers matter.",
        },
    ),
    4: EpisodeSpec(
        {"zh": "Agent Loop", "en": "Agent Loop"},
        {
            "zh": "Agent loop 是 harness 的心脏：context、action、tool、observation 不断闭环。",
            "en": "The agent loop is the harness heart: context, action, tool, and observation form a cycle.",
        },
        {
            "zh": "用 FakeModel 让 loop 行为确定化，先测试 runtime，再接真实模型。",
            "en": "Use FakeModel to make the loop deterministic, proving the runtime before adding real models.",
        },
        {
            "zh": "实现 model.py、loop.py、tracing.py，并跑通 read_file 到 final_answer。",
            "en": "Implement model.py, loop.py, tracing.py, and run read_file through final_answer.",
        },
        {
            "zh": "运行 tests/test_loop.py；确认 max_steps、history、final_answer trace 都存在。",
            "en": "Run tests/test_loop.py and confirm max_steps, history, and final_answer tracing.",
        },
        {
            "zh": "解释为什么 final_answer 也是 action，以及什么时候 success=False 仍要保留 trace。",
            "en": "Explain why final_answer is an action and when success=False still keeps a trace.",
        },
    ),
    5: EpisodeSpec(
        {"zh": "Context Engineering", "en": "Context Engineering"},
        {
            "zh": "模型不是知道整个 repo；它只知道 harness 给它看的 context。",
            "en": "The model does not know the whole repo; it only sees the context the harness provides.",
        },
        {
            "zh": "实现 minimal、search_first、repo_map 三种 context strategy 和 char budget。",
            "en": "Implement minimal, search_first, and repo_map strategies with a character budget.",
        },
        {
            "zh": "实现 context.py，让同一任务在不同策略下产生不同上下文。",
            "en": "Implement context.py so the same task produces different context under different strategies.",
        },
        {
            "zh": "运行 tests/test_context.py；超预算时必须显式标记 TRUNCATED。",
            "en": "Run tests/test_context.py; over-budget context must be marked TRUNCATED.",
        },
        {
            "zh": "构造 minimal 失败、repo_map 成功的案例，写入 context-failure.md。",
            "en": "Build a case where minimal fails and repo_map succeeds, then write context-failure.md.",
        },
    ),
    6: EpisodeSpec(
        {"zh": "Policy 与 Sandbox", "en": "Policy and Sandbox"},
        {
            "zh": "Sandbox 是外部边界，policy 是内部决策；两者一起约束 agent 行动。",
            "en": "Sandbox is the outer boundary; policy is the internal decision layer for agent actions.",
        },
        {
            "zh": "实现 PolicyDecision、command policy，并在 tool 执行前检查 action。",
            "en": "Implement PolicyDecision, command policy, and check actions before tool execution.",
        },
        {
            "zh": "加入 prompt injection demo，验证 env、ssh、危险命令不会被执行。",
            "en": "Add a prompt-injection demo and prove env, ssh, and dangerous commands are blocked.",
        },
        {
            "zh": "运行 tests/test_policy.py；policy block 也要进入 observation 和 trace。",
            "en": "Run tests/test_policy.py; policy blocks must appear in observations and traces.",
        },
        {
            "zh": "解释 prompt injection 为什么不能只靠 prompt 防住，并设计禁止写 .env 的规则。",
            "en": "Explain why prompts alone cannot stop injection and design a rule blocking .env writes.",
        },
    ),
    7: EpisodeSpec(
        {"zh": "Week 1 Capstone", "en": "Week 1 Capstone"},
        {
            "zh": "前 6 集的模块要串成一个可演示的 v0 harness。",
            "en": "The first six modules become a runnable v0 harness demo.",
        },
        {
            "zh": "用 FakeModel 跑 bugfix：read test、read app、edit、pytest、final_answer。",
            "en": "Use FakeModel for bugfix: read test, read app, edit, pytest, final_answer.",
        },
        {
            "zh": "创建 todo_bug demo repo，并生成一次完整 bugfix trace。",
            "en": "Create the todo_bug demo repo and generate a complete bugfix trace.",
        },
        {
            "zh": "确认测试通过、trace 存在、每一步 action/result 可审计。",
            "en": "Confirm tests pass, trace exists, and each action/result is auditable.",
        },
        {
            "zh": "复盘 action schema、policy、context、trace、eval 之间的依赖。",
            "en": "Review how action schema, policy, context, trace, and eval depend on one another.",
        },
    ),
    8: EpisodeSpec(
        {"zh": "Eval Set", "en": "Eval Set"},
        {
            "zh": "没有 eval，就只能靠感觉判断 agent 有没有变好。",
            "en": "Without evals, agent improvement is only a feeling.",
        },
        {
            "zh": "区分 task success 和 trajectory quality，并设计 eval task schema。",
            "en": "Separate task success from trajectory quality and design the eval task schema.",
        },
        {
            "zh": "实现 evals/tasks.jsonl、EvalTask、EvalResult、verify_task 和 eval runner。",
            "en": "Implement evals/tasks.jsonl, EvalTask, EvalResult, verify_task, and an eval runner.",
        },
        {
            "zh": "至少 10 个 eval task；runner 输出 success rate、avg steps 和失败任务。",
            "en": "Use at least 10 eval tasks; the runner reports success rate, average steps, and failures.",
        },
        {
            "zh": "解释为什么 test pass 不等于 agent success，并给 README task 设计 verify。",
            "en": "Explain why test pass is not agent success and design verification for a README task.",
        },
    ),
    9: EpisodeSpec(
        {"zh": "Tracing", "en": "Tracing"},
        {
            "zh": "Agent 失败时，trace 要把“模型不行”拆成可诊断的 failure mode。",
            "en": "When agents fail, traces turn 'the model failed' into diagnosable failure modes.",
        },
        {
            "zh": "设计 JSON trace：run_id、context preview、policy、action、result、final。",
            "en": "Design JSON traces with run_id, context preview, policy, action, result, and final status.",
        },
        {
            "zh": "实现 TraceLogger，保存 JSON，并渲染 Markdown trace report。",
            "en": "Implement TraceLogger to save JSON and render Markdown trace reports.",
        },
        {
            "zh": "用失败 trace 定位根因，而不是只看最终报错。",
            "en": "Use failed traces to identify root cause instead of reading only the final error.",
        },
        {
            "zh": "写 3 个 failure analysis：symptom、root cause、trace evidence、fix idea。",
            "en": "Write three failure analyses with symptom, root cause, trace evidence, and fix idea.",
        },
    ),
    10: EpisodeSpec(
        {"zh": "Loop Engineering", "en": "Loop Engineering"},
        {
            "zh": "Loop engineering 是用 eval 和 trace 系统性改进 agent，而不是手感调 prompt。",
            "en": "Loop engineering improves agents with evals and traces, not prompt tweaks by feel.",
        },
        {
            "zh": "设计 baseline、strict_tools、planner 等 variant，并比较 success rate 和 avg steps。",
            "en": "Design variants such as baseline, strict_tools, and planner, then compare success rate and avg steps.",
        },
        {
            "zh": "实现 experiment runner，输出 variant 对比报告和失败模式。",
            "en": "Implement an experiment runner that reports variant comparisons and failure modes.",
        },
        {
            "zh": "报告必须说明 what improved、what got worse、which traces explain it。",
            "en": "The report must say what improved, what got worse, and which traces explain it.",
        },
        {
            "zh": "写 loop-engineering-definition.md，区分 prompt engineering 和 loop engineering。",
            "en": "Write loop-engineering-definition.md comparing prompt engineering and loop engineering.",
        },
    ),
    11: EpisodeSpec(
        {"zh": "Reviewer Subagent", "en": "Reviewer Subagent"},
        {
            "zh": "Subagent 的价值是隔离上下文噪音，用另一个视角审查结果。",
            "en": "A subagent reduces context noise and reviews results from another perspective.",
        },
        {
            "zh": "先实现 rule-based reviewer，检查 edit 后是否运行测试、是否有 policy block。",
            "en": "Start with a rule-based reviewer that checks tests after edits and policy blocks.",
        },
        {
            "zh": "定义 ReviewResult、summarize_trace_for_review，并在 final_answer 前审查。",
            "en": "Define ReviewResult, summarize_trace_for_review, and review before final_answer.",
        },
        {
            "zh": "验证 reviewer 失败时 agent 不应直接给用户最终答案。",
            "en": "Verify that reviewer rejection prevents the agent from returning a final answer.",
        },
        {
            "zh": "解释 reviewer 为什么不该直接改代码，以及 rule-based baseline 的优势。",
            "en": "Explain why reviewers should not directly edit code and why rule-based baselines help.",
        },
    ),
    12: EpisodeSpec(
        {"zh": "Self-Repair", "en": "Self-Repair"},
        {
            "zh": "Self-repair 不是盲目重试，而是用失败信号缩小修复范围。",
            "en": "Self-repair is not blind retry; it uses failure signals to narrow the fix.",
        },
        {
            "zh": "识别 pytest failure，摘要失败日志，限制 repair budget。",
            "en": "Detect pytest failures, summarize failure logs, and enforce a repair budget.",
        },
        {
            "zh": "在 loop 层接入 repair context，让下一步 action 针对具体失败。",
            "en": "Wire repair context into the loop so the next action targets the specific failure.",
        },
        {
            "zh": "至少一个 demo 第一次失败、第二次修好，并在 trace 中标记 repair phase。",
            "en": "Show one demo that fails first, repairs second, and marks repair phase in the trace.",
        },
        {
            "zh": "解释为什么 repair 不能无限 retry，为什么 prompt 要限制 scope。",
            "en": "Explain why repairs need retry limits and scoped repair prompts.",
        },
    ),
    13: EpisodeSpec(
        {"zh": "CLI / MCP / Skills", "en": "CLI / MCP / Skills"},
        {
            "zh": "把教学 harness 放进真实生态，需要区分 AGENTS.md、skill、MCP 和 CLI。",
            "en": "Putting the teaching harness into real ecosystems requires separating AGENTS.md, skills, MCP, and CLI.",
        },
        {
            "zh": "先做 CLI 作为 product surface，再设计用户意图级 MCP tools。",
            "en": "Build the CLI as the product surface first, then design intent-level MCP tools.",
        },
        {
            "zh": "实现 cli.py、project scripts，并写 docs/mcp-design.md。",
            "en": "Implement cli.py, project scripts, and docs/mcp-design.md.",
        },
        {
            "zh": "CLI smoke test 能跑 run/eval；MCP design 不暴露内部私有函数。",
            "en": "CLI smoke tests run run/eval; MCP design does not expose private internals.",
        },
        {
            "zh": "解释 AGENTS.md 和 skill 的区别，以及什么场景适合 MCP。",
            "en": "Explain AGENTS.md versus skills and what scenarios deserve MCP tools.",
        },
    ),
    14: EpisodeSpec(
        {"zh": "Capstone Demo", "en": "Capstone Demo"},
        {
            "zh": "最后一集不是继续堆功能，而是把项目包装成能展示、能解释、能验证的作品。",
            "en": "The final episode packages the project into work that can be shown, explained, and verified.",
        },
        {
            "zh": "整理 README、demo script、eval report、failure analysis 和面试问答。",
            "en": "Prepare README, demo script, eval report, failure analysis, and interview answers.",
        },
        {
            "zh": "准备 5 分钟 demo：problem、architecture、bugfix、trace、eval、lessons。",
            "en": "Prepare a five-minute demo: problem, architecture, bugfix, trace, eval, and lessons.",
        },
        {
            "zh": "最终 checklist：quickstart 能跑、trace/eval/report 存在、limitations 清楚。",
            "en": "Final checklist: quickstart runs, traces/evals/reports exist, and limitations are clear.",
        },
        {
            "zh": "用 capstone rubric 自评：架构、代码、tool/policy、trace、eval、表达。",
            "en": "Self-grade with the capstone rubric: architecture, code, tool/policy, trace, eval, communication.",
        },
    ),
}


def build_episode_steps(spec: EpisodeSpec) -> list[Step]:
    return [
        Step(
            {"zh": f"{spec.title['zh']}：为什么重要", "en": f"{spec.title['en']}: Why It Matters"},
            spec.thesis,
            {"zh": "建立本集要解决的 agent 工程问题。", "en": "Frame the agent engineering problem this episode solves."},
            {"zh": "先理解问题，lab 里的实现才不会变成照抄代码。", "en": "Understanding the problem first keeps the lab from becoming copy-paste coding."},
        ),
        Step(
            {"zh": f"{spec.title['zh']}：核心设计", "en": f"{spec.title['en']}: Core Design"},
            spec.core,
            {"zh": "明确模块边界、输入输出和取舍。", "en": "Clarify module boundaries, inputs, outputs, and tradeoffs."},
            {"zh": "边界清楚后，policy、trace 和 eval 才能稳定接上。", "en": "Clear boundaries make policy, tracing, and eval integration stable."},
        ),
        Step(
            {"zh": f"{spec.title['zh']}：Lab 产物", "en": f"{spec.title['en']}: Lab Deliverables"},
            spec.lab,
            {"zh": "把概念落到具体文件、测试和 demo。", "en": "Turn the concept into concrete files, tests, and demos."},
            {"zh": "可运行产物比概念定义更能暴露设计问题。", "en": "Runnable artifacts reveal design problems better than concept definitions."},
        ),
        Step(
            {"zh": f"{spec.title['zh']}：验收标准", "en": f"{spec.title['en']}: Verification"},
            spec.verify,
            {"zh": "确认本集产物可以被脚本、测试或 agent rubric 检查。", "en": "Confirm the episode output can be checked by scripts, tests, or an agent rubric."},
            {"zh": "没有验收标准，就无法证明学习者真的完成了 lab。", "en": "Without verification, completion is only a claim."},
        ),
        Step(
            {"zh": f"{spec.title['zh']}：Quiz 与作业", "en": f"{spec.title['en']}: Quiz and Assignment"},
            spec.quiz,
            {"zh": "用一问一答检查概念，用作业检查工程判断。", "en": "Use quiz questions for concepts and assignments for engineering judgment."},
            {"zh": "这一步把视频学习转成可评分、可反馈的练习。", "en": "This turns video learning into scorable, feedback-ready practice."},
        ),
    ]


EPISODES: dict[int, Episode] = {
    1: Episode({"zh": "Harness 边界", "en": "Harness Boundaries"}, EPISODE1_STEPS),
    **{number: Episode(spec.title, build_episode_steps(spec)) for number, spec in EPISODE_SPECS.items()},
}


QUIZ = {
    1: {
        "type": "multiple_choice",
        "question": {
            "zh": "Harness 和 API wrapper 最大区别是什么？",
            "en": "What is the biggest difference between a harness and an API wrapper?",
        },
        "choices": {
            "zh": [
                "A. Harness 会把 prompt 写得更长。",
                "B. Harness 负责 action、tool、policy、trace、eval 等运行时边界。",
                "C. Harness 只能用于本地模型。",
                "D. Harness 不需要测试。",
            ],
            "en": [
                "A. A harness makes prompts longer.",
                "B. A harness owns runtime boundaries such as actions, tools, policy, traces, and evals.",
                "C. A harness only works with local models.",
                "D. A harness does not need tests.",
            ],
        },
        "answer": "B",
        "reference": {
            "zh": "正确答案是 B。Wrapper 处理模型输入输出；harness 处理动作协议、工具执行、权限边界、trace 和 eval。",
            "en": "The correct answer is B. A wrapper handles model input/output; a harness handles action protocols, tool execution, permission boundaries, traces, and evals.",
        },
    },
    2: {
        "type": "short_answer",
        "question": {
            "zh": "为什么第一课先写 README、AGENTS.md 和 architecture.md，而不是直接写 action parser？",
            "en": "Why does Episode 1 start with README, AGENTS.md, and architecture.md instead of an action parser?",
        },
        "reference": {
            "zh": "因为 action parser 只解决模型输出到动作的局部问题。README 定义项目目标，AGENTS.md 定义场景工作协议和 done criteria，architecture.md 定义从用户输入到 context、action、policy、tool、observation、trace、eval 的完整边界。先有边界，parser 才知道服务于什么系统。",
            "en": "Because an action parser only solves the local problem of turning model output into actions. README defines the project goal, AGENTS.md defines the scenario protocol and done criteria, and architecture.md defines the full boundary from user input to context, action, policy, tool, observation, trace, and eval. Boundaries should come before parser implementation.",
        },
        "keywords": ["README", "AGENTS", "architecture", "boundary", "policy", "trace", "eval", "context", "action"],
    },
    3: {
        "type": "short_answer",
        "question": {
            "zh": "为什么 AGENTS.md 是 harness 工程的一部分？",
            "en": "Why is AGENTS.md part of harness engineering?",
        },
        "reference": {
            "zh": "因为它把人的偏好、场景边界、可做/不可做、完成标准写成 agent 可以稳定读取的规则。它不是代码里的 policy，但会影响 context、tool use、done criteria 和 agent 的行为边界。",
            "en": "Because it turns human preferences, scenario boundaries, allowed/disallowed actions, and done criteria into rules an agent can reliably read. It is not code-level policy, but it shapes context, tool use, done criteria, and behavioral boundaries.",
        },
        "keywords": ["AGENTS", "boundary", "done", "policy", "context", "tool", "rules", "scenario"],
    },
}


def normalize_lang(lang: str | None, text: str = "") -> str:
    if lang in {"zh", "en"}:
        return lang
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    ascii_letters = sum(1 for ch in text if ch.isascii() and ch.isalpha())
    return "zh" if cjk >= max(2, ascii_letters // 4) else "en"


def t(value: dict[str, str], lang: str) -> str:
    return value.get(lang) or value["en"]


def card(title: str, body: list[str]) -> str:
    lines = [f"> **{title}**", ">"]
    lines.extend(f"> {line}" if line else ">" for line in body)
    return "\n".join(lines)


def _load_video_sources() -> dict:
    """Optional external video hosting. If video_sources.json exists at repo root,
    clips and intros resolve to hosted URLs; otherwise they fall back to local
    media/ paths. Shape:
      {"clip_base_url": "https://cdn.example.com/loopath",
       "intro": {"en": "https://youtu.be/...", "zh": "https://youtu.be/..."}}
    """
    path = ROOT / "video_sources.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


VIDEO_SOURCES = _load_video_sources()


def clip_ref(episode: int, step: int, lang: str) -> str:
    rel = f"episode-{episode:02d}/clips/{lang}/step-{step:02d}.mp4"
    base = VIDEO_SOURCES.get("clip_base_url")
    return f"{base.rstrip('/')}/{rel}" if base else f"media/{rel}"


def intro_ref(lang: str) -> str:
    return (VIDEO_SOURCES.get("intro", {}) or {}).get(lang) or f"media/intro/loopath-intro.{lang}.mp4"


def start(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang, args.text or "")
    episode_count = len(EPISODES)
    if lang == "zh":
        print(card("Loopath 互动课程", [
            "默认语言：中文",
            f"课程范围：{episode_count} 个 episodes。每个 episode 都有对应 step clips。",
            f"先看 90 秒导论视频：{intro_ref('zh')}",
            "学习方式：每次一个小课题。你可以随时提问、继续下一节、开始 lab、跑 verification 或进入 quiz。",
            "",
            "建议从 Episode 1 / Step 1 开始：",
            "`python3 scripts/loopath.py step --episode 1 --step 1 --lang zh`",
        ]))
    else:
        print(card("Loopath Interactive Course", [
            "Default language: English",
            f"Course scope: {episode_count} episodes. Every episode has matching step clips.",
            f"Watch the 90-second intro first: {intro_ref('en')}",
            "Learning mode: one small topic at a time. You can ask questions, continue, start the lab, run verification, or take the quiz.",
            "",
            "Recommended start: Episode 1 / Step 1:",
            "`python3 scripts/loopath.py step --episode 1 --step 1 --lang en`",
        ]))
    return 0


def render_step(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    episode = EPISODES.get(args.episode)
    if episode is None:
        raise SystemExit(f"Episode must be between 1 and {max(EPISODES)}.")
    if args.step < 1 or args.step > len(episode.steps):
        raise SystemExit(f"Step must be between 1 and {len(episode.steps)} for Episode {args.episode}.")
    step = episode.steps[args.step - 1]
    video_path = clip_ref(args.episode, args.step, lang)
    if args.step < len(episode.steps):
        next_cmd = f"`python3 scripts/loopath.py step --episode {args.episode} --step {args.step + 1} --lang {lang}`"
        next_text = "继续下一小节、提问、开始 lab、跑 verification，或进入 quiz。" if lang == "zh" else "Continue to the next step, ask a question, start the lab, run verification, or take the quiz."
    elif args.episode < max(EPISODES):
        next_cmd = f"`python3 scripts/loopath.py step --episode {args.episode + 1} --step 1 --lang {lang}`"
        next_text = f"进入 Episode {args.episode + 1}，或先提问、开始 lab、跑 verification，或进入 quiz。" if lang == "zh" else f"Continue to Episode {args.episode + 1}, ask a question, start the lab, run verification, or take the quiz."
    else:
        next_cmd = f"`python3 scripts/loopath.py quiz --episode {args.episode} --question 1 --lang {lang}`"
        next_text = "课程 clips 已到最后一步。建议进入 quiz 或回顾 capstone rubric。" if lang == "zh" else "This is the final clip step. Take the quiz or review the capstone rubric."
    labels = {
        "zh": ("背景", "目的", "为什么重要", "视频片段", "下一步"),
        "en": ("Background", "Purpose", "Why it matters", "Clip", "Next"),
    }[lang]
    sep = "：" if lang == "zh" else ": "
    print(card(f"Episode {args.episode} / Step {args.step}: {t(step.title, lang)}", [
        f"**{labels[0]}**{sep}{t(step.background, lang)}",
        f"**{labels[1]}**{sep}{t(step.purpose, lang)}",
        f"**{labels[2]}**{sep}{t(step.why, lang)}",
        f"**{labels[3]}**{sep}`{video_path}`",
        "",
        f"**{labels[4]}**{sep}{next_text}",
        next_cmd,
    ]))
    return 0


def safe_write(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def lab_create(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    repo = Path(args.repo).expanduser().resolve()
    overwrite = args.overwrite
    dirs = [
        "src/loopath",
        "tests",
        "demo_repos",
        "prompts",
        "evals",
        "traces",
        "docs",
    ]
    for directory in dirs:
        (repo / directory).mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[str] = []
    files = {
        "README.md": "# Loopath\n\nLoopath is a teaching project for building a mini Codex-style coding agent runtime from scratch.\n\nIt demonstrates:\n\n- structured model actions\n- tool execution\n- policy checks\n- agent loop\n- tracing\n- evals\n- loop engineering\n\nThis project is intentionally small, inspectable, and designed for learning.\n",
        "AGENTS.md": "# AGENTS.md\n\n## Project goal\n\nThis repo teaches how to build a mini coding-agent harness from scratch.\n\n## Commands\n\n- Run tests with `pytest`.\n- Keep examples simple and readable.\n\n## Engineering rules\n\n- Prefer small modules with explicit interfaces.\n- Every new core module should have tests.\n- Never bypass policy checks in the agent loop.\n- Trace every agent step.\n\n## Done when\n\n- The code runs.\n- Tests pass.\n- The design note explains why the module exists.\n",
        "pyproject.toml": "[project]\nname = \"loopath\"\nversion = \"0.1.0\"\nrequires-python = \">=3.11\"\ndependencies = []\n\n[project.optional-dependencies]\ndev = [\n  \"pytest>=8\"\n]\n\n[tool.pytest.ini_options]\npythonpath = [\"src\"]\n",
        "docs/architecture.md": "# Loopath Architecture\n\n## Core idea\n\nThe model does not directly mutate the world.\nIt proposes structured actions.\nThe harness validates, executes, observes, and records those actions.\n\n## Modules\n\n- ModelClient: produces the next action.\n- Action schema: validates model output.\n- ToolRegistry: executes allowed tools.\n- Policy: blocks unsafe actions.\n- ContextBuilder: decides what the model sees.\n- AgentLoop: controls execution.\n- TraceLogger: records what happened.\n- Evaluator: measures performance.\n",
        "docs/day1-reflection.md": "# Day 1 Reflection\n\n## 我过去如何使用 coding agent\n\n\n## 这些能力里哪些来自模型\n\n\n## 哪些来自 harness / runtime\n\n\n## 我现在对 harness 的定义\n\n",
        "src/loopath/__init__.py": "",
    }
    for relative, content in files.items():
        ok = safe_write(repo / relative, content, overwrite)
        (created if ok else skipped).append(relative)
    title = "Lab 1 project created" if lang == "en" else "Lab 1 项目已创建"
    body = [
        f"Repo: `{repo}`",
        f"Created: {', '.join(created) if created else '-'}",
        f"Skipped existing files: {', '.join(skipped) if skipped else '-'}",
        "",
        ("接下来：在对话里逐个文件查看内容、解释设计取舍，再继续下一步。" if lang == "zh"
         else "Next: review each file in the conversation, explain the design tradeoffs, then continue."),
    ]
    print(card(title, body))
    return 0


def get_quiz_item(episode_number: int, question_number: int) -> dict:
    if episode_number == 1:
        item = QUIZ.get(question_number)
        if not item:
            raise SystemExit(f"Question {question_number} is not available for Episode 1.")
        return item
    spec = EPISODE_SPECS.get(episode_number)
    if spec is None:
        raise SystemExit(f"Episode must be between 1 and {max(EPISODES)}.")
    if question_number != 1:
        raise SystemExit(f"Only Question 1 is available for Episode {episode_number}.")
    return {
        "type": "multiple_choice",
        "question": {
            "zh": f"Episode {episode_number} 的核心工程目标是什么？",
            "en": f"What is the core engineering goal of Episode {episode_number}?",
        },
        "choices": {
            "zh": [
                "A. 让 prompt 更长。",
                f"B. {spec.core['zh']}",
                "C. 跳过验证，直接相信最终答案。",
                "D. 把所有内部函数都暴露成工具。",
            ],
            "en": [
                "A. Make the prompt longer.",
                f"B. {spec.core['en']}",
                "C. Skip verification and trust the final answer.",
                "D. Expose every internal function as a tool.",
            ],
        },
        "answer": "B",
        "reference": {
            "zh": f"正确答案是 B。{spec.core['zh']} 本集的 lab 和验收都围绕这个目标展开。",
            "en": f"The correct answer is B. {spec.core['en']} The lab and verification are built around that goal.",
        },
    }


def quiz(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    item = get_quiz_item(args.episode, args.question)
    lines = [t(item["question"], lang)]
    if item["type"] == "multiple_choice":
        lines.append("")
        lines.extend(item["choices"][lang])
    lines.append("")
    lines.append("Answer this question, then ask the agent to grade it." if lang == "en" else "请先回答这一题，然后让 agent 评分。")
    print(card(f"Episode {args.episode} Quiz {args.question}", lines))
    return 0


def grade(args: argparse.Namespace) -> int:
    lang = normalize_lang(args.lang)
    item = get_quiz_item(args.episode, args.question)
    answer = args.answer or (Path(args.answer_file).read_text(encoding="utf-8") if args.answer_file else "")
    normalized = answer.strip().lower()
    if item["type"] == "multiple_choice":
        expected = item["answer"].lower()
        score = 10 if normalized.startswith(expected) or expected in normalized[:5] else 0
        feedback = ("Correct." if score else "Not quite.") if lang == "en" else ("正确。" if score else "不太对。")
    else:
        keywords = item["keywords"]
        hit = sum(1 for key in keywords if key.lower() in normalized)
        score = min(10, max(0, round(hit / max(1, len(keywords)) * 10)))
        if score >= 8:
            feedback = "Strong answer with the key boundaries covered." if lang == "en" else "回答很扎实，关键边界基本覆盖。"
        elif score >= 5:
            feedback = "Partially correct, but missing some runtime boundaries." if lang == "en" else "部分正确，但还缺少一些 runtime 边界。"
        else:
            feedback = "Needs more detail about harness boundaries and verification." if lang == "en" else "需要补充 harness 边界和验证机制。"
    reference_label = "Reference answer" if lang == "en" else "参考答案"
    print(card(f"Episode {args.episode} Quiz {args.question} Score: {score}/10", [
        feedback,
        "",
        f"**{reference_label}**{'：' if lang == 'zh' else ': '}{t(item['reference'], lang)}",
    ]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Loopath interactive course helper.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("start")
    p.add_argument("--lang", default="auto")
    p.add_argument("--text", default="")
    p.set_defaults(func=start)

    p = sub.add_parser("step")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--step", type=int, required=True)
    p.add_argument("--lang", default="auto")
    p.set_defaults(func=render_step)

    p = sub.add_parser("lab-create")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--repo", required=True)
    p.add_argument("--lang", default="auto")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=lab_create)

    p = sub.add_parser("quiz")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--question", type=int, required=True)
    p.add_argument("--lang", default="auto")
    p.set_defaults(func=quiz)

    p = sub.add_parser("grade")
    p.add_argument("--episode", type=int, default=1)
    p.add_argument("--question", type=int, required=True)
    p.add_argument("--answer", default="")
    p.add_argument("--answer-file")
    p.add_argument("--lang", default="auto")
    p.set_defaults(func=grade)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
