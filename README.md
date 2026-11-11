# tstack

A personal adaptation of [t3dotgg/tstack](https://github.com/t3dotgg/tstack)
packaged as a versioned Codex plugin. Sol reviews use native subagents; council
runs latest Sol, latest Opus through Claude Code CLI, and Gemini Pro through
Cursor CLI in parallel.

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

The plugin includes all nine skills and their bundled scripts and references.
Some skills call others:

- `full-send` uses `sol-loop`, `file-pr`, and `babysit-pr`.
- `full-stop` uses `full-send`.
- `council` uses `sol-loop` for Codex model selection and agent lifecycle.
- `takeover` uses `modernize`, `file-pr`, `babysit-pr`, and `leaving-pr-comments`.
- `file-pr`, `babysit-pr`, and `modernize` use `leaving-pr-comments`.

## Install

Once the plugin files are published to this repository:

```bash
codex plugin marketplace add vladimir-fsh/tstack
codex plugin add tstack@vmh-tstack
```

Start a new chat to use the installed skills. If you previously copied these
skills to `~/.codex/skills/`, move those nine copies out of the skills directory
after verifying the plugin installation, so Codex does not discover both copies.
Keep unrelated personal skills.

For local development, register this checkout instead of the GitHub source:

```bash
codex plugin marketplace add /absolute/path/to/tstack
codex plugin add tstack@vmh-tstack
```

Both sources use the same marketplace name. Choose one source at a time.

## Update

For a GitHub-backed installation, refresh the marketplace and install the current
plugin version:

```bash
codex plugin marketplace upgrade vmh-tstack
codex plugin add tstack@vmh-tstack
```

For a local source, run `codex plugin add tstack@vmh-tstack` again after editing
the checkout. Local plugins are installed as cached copies; editing this checkout
does not edit an existing installation. Start a new chat after updating.

## Release

The version in `.codex-plugin/plugin.json` is the single source of truth. Bump it
from any working directory with the script's absolute path, or from this repo:

```bash
/usr/bin/python3 scripts/bump_version.py patch
```

Use `patch` for fixes, `minor` for added workflows, and `major` for breaking
changes. The script changes only the manifest version. Review and commit the
skill changes together with the version bump, then push them to the branch
tracked by the marketplace. A bump alone does not publish an update. Git tags
such as `v0.1.1` are optional release markers.

The marketplace at `.agents/plugins/marketplace.json` points to this repository's
root. The plugin reuses `skills/` directly; there is no build step or generated
copy of the skills to keep in sync.

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
release and update the plugin as described above.
Keep project-specific instructions in that project's `AGENTS.md` rather than
baking them into the shared workflow.

## License

[MIT](LICENSE)
