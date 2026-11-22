# Codex CLI reviewer

Use this route for the Sol seat when the council runs outside Codex, such as
in Claude Code.

Check `codex --version` and `codex login status`. If not logged in, explain
that the user needs to run `codex login` in their terminal.

Resolve the model on every run from `codex debug models`: the latest `gpt-*-sol`
slug with `"visibility": "list"`. If the user requests a specific version, use
that exact slug. Set `sol_model` to it. If no Sol slug is listed, report the
blocker rather than substituting another model. Use `high` reasoning effort
unless the user names another level the slug lists in
`supported_reasoning_levels`.

Create a private temporary directory. Set `brief`, `result`, `events`, and
`log` to unique absolute file paths there. Write the complete brief, including
the diff and applicable repository rules, to `brief`. From the trusted
repository checkout, run this as a separate background process, alongside the
other seats:

```bash
codex exec --model "$sol_model" \
  -c model_reasoning_effort='"high"' \
  --sandbox read-only --ephemeral --color never \
  --json -o "$result" - \
  < "$brief" > "$events" 2> "$log"
```

The read-only sandbox lets Sol read files and run inspection commands such as
`git diff`, but blocks writes. `exec` never stops for approval. `-` reads the
brief from stdin. `--json` writes the event stream to `events`; `-o` writes
only Sol's final message to `result`. If a flag is unsupported, inspect local
`codex exec --help` and report the incompatibility.

Keep the shell process handle and wait in intervals of at most 60 seconds.
Check exit status, a non-empty `result`, `error` events in `events`, and a
complete review verdict. A successful exit alone is not approval. Inspect
`log` on failure. Stop the owned process before retrying or handing off.
Record the requested `sol_model` and effort as the seat's identity; the event
stream does not name the model. Start a fresh process per round, without
`codex exec resume`; include the findings ledger and updated diff in each new
brief. Keep each round's files separate for the review history.
