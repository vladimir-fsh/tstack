---
name: sol-loop
description: Review changes iteratively with the latest available GPT Sol through native Codex subagents. Use when the user asks for "sol loop" or another skill requires it.
---

# sol-loop

This is a workflow for making your code changes more correct before (or
sometimes after) filing a pull request. tl;dr - use OpenAI's GPT Sol to review
your code in a loop.

Make the most minimal possible changes to appease the Sol reviewers. Be careful
of scope creep and don't be scared to push back.

## Budget

- Default: 3 rounds total. Round 1 is full. Later rounds check only
  changed code and open findings.
- Extend to 5 only for security, permissions, auth, data loss, or
  state/concurrency, while a blocker or should stays open with evidence. Or when
  the user asks.
- Stop early if a round returns only nits. Declined nits and comment,
  doc, or format-only fixes need no new round.
- One reviewer only. Sol must not start subagents or reviewers.
- Keep a ledger: id, severity, outcome, usage if returned. Never guess it.

## 1. Scope

Run `git status --short`. Do not stash, discard, or include unrelated
changes. Limit review to the change paths if they separate cleanly.
Otherwise stop and ask.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Check out the branch
  only if clean. Confirm `HEAD` is the PR head, or ahead only by this
  change. Base: `git merge-base HEAD origin/<baseRefName>`.
- Local: `git merge-base HEAD origin/<default-branch>`. No remote: a base
  the user names, or `HEAD` for uncommitted changes only.

The change is base to working tree in those paths, with untracked files.
Use one diff command all rounds. State intent and out-of-scope in 1-2
sentences. Run covering checks. Do not send code this change breaks. Note
missing or pre-failing checks in the brief.

## 2. Start Sol

Read the model IDs exposed by the current Codex runtime and select the latest
available Sol on every invocation. Do not hardcode an ID or substitute a model.
If native subagents or the selected Sol are unavailable, report the blocker.
Use `collaboration.spawn_agent` with that model, `reasoning_effort: "high"`
(unless the user specified another effort), and `fork_turns: "none"`. Supply a
self-contained brief and save the agent ID. Record model and effort only from
the actual spawn parameters; a full-history fork cannot override them.

Use `collaboration.followup_task` to start later rounds on the saved agent;
`send_message` alone does not start an idle agent. Collect results through
`collaboration.wait_agent`, using waits of at most 60 seconds, and read the
delivered messages. The parent can continue independent work while Sol runs.

Do not edit scoped files while review runs or start a second sol-loop reviewer.
Timeout, error, or no reply is not approval. On failure, interrupt the old agent,
verify it stopped, and restart with the ledger.

Round 1 brief (the reviewer starts without parent history):

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents.
Repo: <abs path> Base: <sha> Intent: <intent> Out of scope: <scope> Checks: <results>
Read the applicable AGENTS.md and repository rules before judging the change.
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Read surrounding code. Find bugs, broken callers, mismatch with intent.
Skip style unless it hides a bug. Hold to the smallest change. Flag code,
tests, or guards the intent does not need. Small perf and extra compat: nits.
Severity follows impact, including rare security, data-loss, and concurrency bugs.
blocker = intended behavior is wrong or creates serious harm.
should = a material bug in scope. nit = optional improvement.
Reply:
VERDICT: APPROVE or CHANGES
S1 [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion> (stable ids)
```

## 3. Answer findings

Check each finding and severity yourself. Judge impact and relevance to the
requested behavior; rarity alone does not make security or data-loss bugs nits.

- Agree: smallest fix. Prefer delete or narrow over new lock, cache,
  helper, or option. Fix the case that happened. Add one focused test
  that fails without the fix, if intent needs it.
- Disagree: say why, with evidence (file:line, test, output).
- Out of scope or nit: decline in one line. List as follow-up.

Update the ledger. Re-run checks and `git diff --shortstat <base>`. If
review grew the diff, cut first. Do not agree just to end the loop.

## 4. Next round

Start one only if budget remains and a blocker or should is open, behavior code
changed, or approval does not cover the current behavior diff. Use
`collaboration.followup_task` on the saved native agent ID. Send the round 1 brief,
the ledger (`fixed:` / `disagree:` / `declined:` + evidence), the same base
diff, and the change since last round. Tell Sol: open ids and changed code only.
Mark each old id `resolved` or `still open: <reason>`.

## 5. Stop and ship

Agreed: APPROVE on the current behavior diff, no blocker or should open,
no concern of your own. Stuck: an item stays disputed after two replies,
or budget ends. Show both sides in 2-3 lines each. The user decides.
Budget end is not approval.

Do not push during the loop. Push after agreement only if the user asked
to push, ship, or update the PR. When a PR description is being created or
updated within the authorized task, include a concise review note where its
template permits:

`Reviewed with sol-loop: <N> rounds with <model>. Sol verdict: approved`.

Add `on <effort>` only if verified. Preserve the repository template and existing
generated sections. Do not edit or comment on a PR solely because this review ran.

Report: rounds, model, what Sol changed, diff size before/after, fixed and
declined findings with reasons, usage if exposed (else say not), pushed or not.
