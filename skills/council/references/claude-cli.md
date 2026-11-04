# Claude CLI reviewer

Check `claude --version` and `claude auth status`. If not authenticated, explain
that the user needs to run `claude auth login` in their terminal.
Select the latest Opus explicitly with `--model opus`, rather than inheriting
the configured default. If the user requests a specific version, replace the
alias with its verified full model ID. Check for an `ANTHROPIC_DEFAULT_OPUS_MODEL`
override before treating the alias as latest; report a pin or access restriction
instead of silently using an older or different model.

Create a private temporary directory. Set `brief`, `result`, and `log` to unique
absolute file paths there. Write the complete brief, including the diff and
applicable repository rules, to `brief`. From the trusted repository checkout,
run this as a separate process, alongside Sol and the Cursor reviewer:

```bash
claude --safe-mode -p --model opus \
  --tools 'Read,Glob,Grep' \
  --allowedTools 'Read,Glob,Grep' \
  --disallowedTools 'mcp__*' \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --permission-mode dontAsk \
  --no-session-persistence --output-format json --effort high \
  < "$brief" > "$result" 2> "$log"
```

`--safe-mode` skips custom skills, hooks, plugins, and project instructions.
Supply applicable repository rules in the brief explicitly. The reviewer can
read source files; the parent supplies Git output and check results. Keep the
read-only tool set and permission settings. If a flag is unsupported, inspect
local `claude --help` and report the incompatibility.

Keep the shell process handle and wait in intervals of at most 60 seconds.
Check exit status, valid JSON, error/subtype and permission-denial fields, and
a complete review verdict in `result`. A successful exit alone is not approval.
Inspect stderr on failure. Cancel the owned process before retrying or handing
off. Record model identity from `modelUsage` when present, otherwise report it
as unavailable. If output shows a fallback outside the requested Opus selection,
report it rather than counting it as the requested review. Keep each round's
files separate for the review history.
