# tstack

A personal adaptation of [t3dotgg/tstack](https://github.com/t3dotgg/tstack)
for Codex. Sol reviews use native subagents; council runs latest Sol,
latest Opus through Claude Code CLI, and Gemini Pro through Cursor CLI
in parallel.

## Skills

| Skill | Say | What it does |
|---|---|---|
| `full-send` | "full send" | Takes a change to a merged PR with nobody watching: proves it, reviews it, files it, babysits it, merges it. |
| `full-stop` | "full stop" | Same as `full-send`, but stops when the PR is ready for you to merge. |
| `council` | "council" | Gets three parallel reviews: native Sol, Claude CLI, and Gemini Pro through Cursor CLI. |
| `sol-loop` | "sol loop" | Reviews a change with the latest available GPT Sol until agreement or the review budget is reached. |
| `file-pr` | "file a PR" | Files a short PR that leads with the problem, not an inventory of changes. |
| `takeover` | "take over" | Finishes someone else's PR, branch, or agent thread, and keeps their credit. |
| `babysit-pr` | "babysit" | Watches a PR through CI and review bots, and fixes the real findings. |
| `modernize` | "modernize" | Rebases an old PR and decides if it should still exist. |
| `leaving-pr-comments` | (automatic) | Formats comments that an agent posts on your behalf. |

Some skills call others. Install the ones they need too:

- `full-send` uses `sol-loop`, `file-pr`, and `babysit-pr`.
- `full-stop` uses `full-send`.
- `council` uses `sol-loop` for Codex model selection and agent lifecycle.
- `takeover` uses `modernize`, `file-pr`, `babysit-pr`, and `leaving-pr-comments`.
- `file-pr`, `babysit-pr`, and `modernize` use `leaving-pr-comments`.

## Install

```bash
git clone https://github.com/vladimir-fsh/tstack
mkdir -p ~/.codex/skills
cp -R tstack/skills/* ~/.codex/skills/
```

## Requirements

- An authenticated [GitHub CLI](https://cli.github.com) (`gh`).
- Codex with native subagent tools and access to a Sol model. Always select the
  latest available Sol from the current runtime; no version is pinned.
- `/usr/bin/python3` for `babysit-pr`'s bundled `pr-wait` script on this Mac.
- For `council` only: Claude Code CLI with a working login (`claude auth login`),
  plus Cursor CLI (`agent login`) with Gemini Pro available in `agent models`.
  Model versions are selected at runtime. Other workflows, including `sol-loop`
  and `full-send`, do not require either external CLI.

`pr-wait` runs inside the active Codex task. It does not arrange a wakeup after
that task ends. Repository PR skills, templates, and permission rules apply.

## Make them yours

Edit the skill instructions in this repository, inspect the Git diff, then
copy the updated skill directories to `~/.codex/skills/` to use them globally.
Keep project-specific instructions in that project's `AGENTS.md` rather than
baking them into the shared workflow.

## License

[MIT](LICENSE)
