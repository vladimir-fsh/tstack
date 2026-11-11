# Cursor CLI reviewer

Check `agent --version`, `agent status`, and `agent models`. If authentication
is missing, ask the user to run `agent login` in their terminal. Report the
council as incomplete until the configured reviewer is available.

Use the user's choice recorded in [Council](../SKILL.md). If no choice has
been recorded for this run, complete Council's selection step first. Resolve
the chosen family to its latest available flagship model, or use the exact
model requested by the user. Set `cursor_model` to the exact listed ID; do not
pin a version in this skill or use Auto, which may duplicate another council model.
If the requested model is absent, report it rather than substituting. Use a
high reasoning variant only when the current CLI/model listing supports it.

Create unique absolute `brief`, `result`, and `log` paths in a private temporary
directory. Write the same complete review brief supplied to the other seats,
including repository rules, scope, diff, and check results. Require read-only
review, no nested reviewers, a score, verdict, and evidence for findings.
From the trusted repository checkout, launch alongside Sol and Claude:

```bash
agent --print --mode ask --model "$cursor_model" --output-format json \
  "$(cat "$brief")" > "$result" 2> "$log"
```

Ask mode is read-only; print mode alone permits writes and shell commands.
Keep Ask mode and omit force, automatic MCP approval, and permission bypasses.
Start a fresh process per round, without `--continue` or `--resume`; include
the findings ledger and updated diff in each new brief.

Keep the process handle and collect output in waits of at most 60 seconds.
Check exit status, valid JSON, error fields, and a complete review verdict.
Exit 0 alone is not approval. Inspect stderr on failure, and stop the owned
process before retrying or handing off. Preserve each round's output. Record
the requested model and any identity confirmed by the output separately.

Reference: [Cursor CLI modes](https://cursor.com/docs/cli/overview).
