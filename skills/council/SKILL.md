---
name: council
description: Get three parallel reviews using the latest Sol in Codex, Claude Code CLI, and a user-selected Gemini, Grok, or Muse model through Cursor CLI. Use when the user asks for "council".
---

# Council

Before launching any reviewer, ask the user to choose the third council member:
Gemini, Grok, or Muse, all accessed through Cursor CLI. If the user already
selected a member for this council run, use that choice without asking again.
Use the available question tool to present the three choices and wait for an
explicit answer; a preselected option or no response is not a choice. If no
question tool is available, ask in chat and wait. Keep the selection for later
rounds of the same council run unless the user changes it.

Before an audit, address outstanding PR comments, fix known issues, and run
relevant checks. Give council the updated implementation; do not defer known
fixes until reviews return. If the user wants to discard the implementation
and explore new ideas, skip fixes to code being replaced.

Bring in three delegates to help with the user's request, usually for review
or feedback. Use one strong model from each of three different providers, at
high reasoning effort where supported. If the user's instructions name council
members, use those. For a chosen model family, use its latest available flagship
model from the current model list.

In this Codex environment, use one latest-Sol native agent, one latest-Opus
reviewer through Claude Code CLI, and the user-selected Cursor CLI reviewer.
Resolve the selected family to an exact available model ID before launching
any reviewer. If unavailable, report that and ask the user to choose again;
keep the council pending until the choice can be honored.
Cursor is the access route; the selected model determines the third provider.
Use model selection and native agent lifecycle from
[sol-loop](../sol-loop/SKILL.md), section 2, and the recipes for
[Claude CLI](references/claude-cli.md) and [Cursor CLI](references/cursor-cli.md).
Record actual model IDs when exposed. An unavailable member remains a blocker;
do not silently replace Cursor with another Sol agent.

Start the native Sol agent and both CLI processes before waiting for any result,
within runtime concurrency limits. Save the agent ID and both process handles;
start later rounds in parallel too. Report an unavailable configured route
instead of silently replacing a reviewer.

Give each delegate the same request, repository rules, scope, diff (including
relevant uncommitted files), and observed checks. Keep contexts independent
until all return. For review or feedback, keep their work read-only without
nested reviewers; keep scoped files unchanged while they review. The parent
can do independent work outside that scope. Collect all three responses and
summarize the useful findings, disagreements, and recommended next steps.

For a code review, ask each delegate for a score out of 10 and an explicit
APPROVE or CHANGES verdict with file/line evidence and stable finding IDs.
Count each full review pass as one round.
A fresh review after fixes starts a new round.

If the work ends in a pull request, put the results in the PR description.
Preserve the repository template; put this section before the model and
harness line at the end when the template permits. For the Codex council:

```markdown
## Council review

Rounds: 2

| Delegate | Round 1 | Round 2 |
| --- | --- | --- |
| Claude CLI (<verified model>) | 7/10 | 9/10 |
| Latest Sol (<verified model>) | 8/10 | 10/10 |
| Cursor CLI (<verified selected model>) | 7/10 | 9/10 |
```

If a delegate gives no score, write `no score`. Do not invent one.
If the PR is open and its description update is authorized, edit it rather
than posting a comment.
If there is no PR, put the same results in the final reply only.

If you agree with their recommendations, make the smallest justified changes,
rerun focused checks, and request a fresh review after. Continue until all
three delegates are satisfied with the current diff, or a genuine blocker,
unresolved disagreement, or user-specified budget requires handoff. A missing
or failed reviewer is not consensus. Report each seat's verdict and limitations.

Do not let repeated reviews result in scope creep. It is your job to fight to
keep scope limited.
