---
name: babysit-pr
description: Babysit a PR with a Claude review, one automatic fix and re-review, then user-approved repeat rounds. Also supports read-only PR monitoring.
---

# Babysit PR

For an actionable babysit request, follow the [Claude cycle](references/claude-cycle.md):
request review, wait, fix valid findings, clean up that round's comments, request
review again, then ask before fixing the new findings. Each yes permits one more
fix, cleanup, and review round. This is also the default when another skill calls
`babysit-pr`; a caller's general autonomy does not skip the repeat-round question.

An explicitly read-only watch request only observes checks and feedback; it does
not invoke Claude, change code, or delete comments. If the user explicitly chooses
another reviewer or CI-only monitoring, follow that scope using the guidance below.

## Waiting

Never write your own watcher, polling loop, or `sleep` loop. Use one `pr-wait`
watcher per PR. Every watcher on a GitHub account shares one rate limit.
Only the parent that owns the PR watches it; review delegates do not.
Handle existing checks and comments before starting the watcher.
A watcher event is news, not a merge decision; check the merge gate yourself.

### `pr-wait`

Wait with `scripts/pr-wait` from this skill's directory (use its absolute
path).

```bash
pr-wait <pr> [--repo owner/name] [--until ready|green|any-change] [--review-author LOGIN]
```

It prints one line per real event. It exits 0 when the `--until` condition is
met or the PR merges, 1 when it needs you (a required check failed, conflicts,
unresolved threads, PR closed), and 2 on bad input.

- `ready` (default): checks green, Greptile or Macroscope reviewed the head,
  and no unresolved threads. Use it when one of those bots is expected.
- `green`: required checks, or all CI checks when none are marked required.
  Use it when the repo has no Greptile or Macroscope; assess reviews separately.
- `any-change`: exit on the first event.

For Claude, use `any-change` with `--review-author` for the exact account(s)
confirmed by the repository's integration. This includes edits to progress
comments and bot reviews that ordinary watching skips. Repeat the flag for
multiple accounts. An activity event is not proof that Claude finished; use the
completion rules in the Claude cycle. `ready` does not wait for Claude.

When no checks exist or are expected, assess readiness directly; neither
`green` nor `ready` completes on an empty check set. Exit 0 alone does not prove
the full merge gate; read the event to distinguish ready from already merged.

In Codex, run the bundled script with `/usr/bin/python3` and its absolute path.
Keep the process/session ID and collect output in waits of at most 60 seconds.
Stay active while waiting; ending a Codex turn does not arrange a future wakeup.
The parent can do independent work while CI runs. Stop the owned watcher before
a final handoff or a question that ends active work. Continue until the current
review completes, readiness is reached, or a real blocker appears, unless the
user specifies a time limit. The Claude cycle's decision point takes precedence
over continuing to readiness.

In Claude Code, run it with the Monitor tool (`timeout_ms: 3600000`), so each
line wakes you. Without a monitor, run it as one long command. It ends on its
own.

Start it again after you push, after you handle an exit 1, and after a resume.
It remembers what it already reported, so nothing that arrived in between is
lost. If it says another pid already watches the PR, do not start a second one.
Stop the old one only after confirming it is a stale watcher owned by this task.

When an event needs no action, keep waiting quietly. Only end the turn when a
service-side watcher or Monitor will wake it. Never post or say "still waiting".

## GitHub rate limits

`gh pr create`, `gh pr view`, and `gh pr checks` use GraphQL. When GraphQL is
used up, the REST limit is separate and usually still has room. Use
`gh api repos/<owner>/<repo>/pulls/<n>` to read a PR, and
`gh api repos/<owner>/<repo>/commits/<sha>/check-runs` for checks.

## Reviews

Evaluate checks on the latest PR head and reconcile still-open findings,
including older threads, against the current source. Fix real findings and CI
failures, distinguish repository failures from infrastructure flakes, and reply
with a written reason when dismissing false positives.

If the repo has `.macroscope/check-run-agents/*.md`, read those rules before you
reply to a Macroscope finding. Its findings cite them.

CodeRabbit is advisory. Treat its findings like any other finding, but never
wait for it and never hold a merge for it.

Within authorized PR maintenance, explain dismissed feedback with evidence
and resolve the thread after the reply succeeds. A read-only monitoring request
does not authorize fixes or replies. Use the `leaving-pr-comments` skill
for every comment posted on the user's behalf.

Screenshots and videos help as well, when you have a way to upload them.

Keep the PR at the size the user's goal needs. Review loops tend to grow a
PR one cheap-looking fix at a time. Fix real bugs in the intended case.
Decline unrelated suggestions with a reason, and list them as follow-ups:
unneeded tests, extra integration or compatibility, and small performance costs.
Judge uncommon security, data-loss, and concurrency failures by impact. Prefer
the fix that deletes or narrows code.

## Base branch and merging

Track the PR's actual target branch and rebase when updates are authorized.
`pr-wait` reports when new base commits touch this PR's files, and when the PR
becomes BEHIND or DIRTY.
Check the current head, base, and merge gate before declaring the PR ready.
If an overlapping PR makes this one obsolete, stop monitoring, report it to the
user, and ask before closing the PR unless closure was explicitly authorized.

If nothing has changed, stay quiet rather than posting filler comments. Stop
when `pr-wait` exits 0 and the merge gate passes on the latest head. Merge only when the user explicitly requested it;
otherwise report that the PR is ready. Right before a merge, run `git fetch` and
check the PR again. Never merge when it is BEHIND or DIRTY, or when base commits
that landed after the last green run touch this PR's files. Rebase, push, and
wait for green again.
