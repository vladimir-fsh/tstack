---
name: full-send
description: Trigger this if the user says 'full send'.
---

# Full Send

If the user triggered this, it's because they are not watching this thread, and
they want you to complete the work end-to-end autonomously. Your updates and
your final message go unread until long after you stop. You own the work from
its current state to a merged PR.

If the user did not explicitly request "full send" in some clear way, do not
assume full autonomy. If they did, everything below applies.

The user grants you permission to:

- Merge the PR once the merge gate passes.
- Force-push the PR's own branch with `--force-with-lease` after a rebase.
- Use the test methods that Proof needs, without asking first.

## Testing permission

A "full send" request authorizes the test methods needed for this task.
Follow explicit user restrictions and harness approval requirements.

That includes computer use, browser automation, simulators and devices,
running the app or a dev server, screenshots, and visual checks. Use the method
that gives direct proof. List it in the report.

Rules about how to test still apply. Follow rules that name the correct
command, fixture, or check. Use the method that proves the change within
those permissions.

It covers only the tests needed for this task. It does not add permission
for the steps under "Asking the user", such as production changes or data
deletion. It also does not bypass a harness or system approval prompt if
one appears.

## Steps

1. **Finish the change.** Complete the goal from the user's request with the
   smallest change that works. Fix the case that happened, not every case
   that could. If you are on the default branch, create a branch first.
2. **Prove it.** Get proof for every change you made. See "Proof".
3. **Get feedback.** Use the `sol-loop` skill to verify changes.
4. **File the PR** with the `file-pr` skill, following the repository template.
   Rebase onto the latest actual target branch first. Mention proof in the
   description when it helps review, rather than listing routine green checks.
5. **Babysit the PR** with the `babysit-pr` skill. Fix real findings and CI
   failures. Get proof for each fix before you push it. Its Claude cycle permits
   the first fix and re-review automatically, then requires the user's yes for
   each further fix round. That specific decision gate overrides this workflow's
   general autonomy; a no leaves the PR open and ends the workflow.
6. **Merge** when the merge gate passes.
7. **Report** in your final message: the PR link, the merge commit, your proof,
   and each decision you made for the user.

Stay active from step 1 to step 7. If you end your turn while checks or bots are
pending, the work stops, because nobody will prompt you again. Use the watcher
from `babysit-pr`: the persistent `pr-wait` process with bounded waits.
Stop the owned watcher before a handoff.
Ending a Codex turn does not arrange a future wakeup. Keep waiting until ready
or a real blocker, unless the user specifies a time limit.

## Proof

Proof is evidence you observed yourself in this session: command output, a
reproduction, a screenshot. Use the most direct proof the change allows:

- Reproduce the original failure, apply the fix, then watch the same
  reproduction pass.
- Run the checks that the repo's CI runs (typecheck, lint, tests).
- Add one focused test that fails without the fix, when the behavior has none
  and the repo has a test setup.
- For UI and runtime behavior, run the app and look at the change. Green mocked
  tests do not prove that the user experience works. Attach screenshots to the
  PR when they help and you have a way to upload them.

When you cannot find a way to prove a change, you do not have full confidence.
Ask the user.

## Merge gate

Full confidence means all of these are true on the latest commit:

- Your proof covers every change in the diff.
- Required checks are green.
- Required review bots have finished when configured, and each material finding
  is fixed or dismissed with a written reason.
- Required human approvals are present, and no human review requests changes.
- The branch is up to date with the actual PR target branch, and GitHub reports
  it as mergeable.
- Sol approval covers the final behavior diff; repeat focused proof and review
  after meaningful fixes or conflict resolutions.

Merge with the method the repo uses. Check the allowed methods and recent merged
PRs. If the repo uses a merge queue or auto-merge, stay until GitHub reports the
PR as merged. Merge through branch protection as configured. Never use `--admin`
or other bypasses. Required approvals cannot be replaced by agent confidence.

## Asking the user

A question in a normal message goes unseen, and the thread looks done. To ask
the user something, use a question tool available in the current mode, such as
`request_user_input_async` in Codex. A required answer remains pending; silence
is not permission. Put all the context in the question:
the PR link, what blocks you, and the options with your recommendation first.

Ask only when you cannot continue alone:

- You cannot prove the change.
- The merge gate cannot pass, and you cannot fix that yourself.
- The next step is outside the grant above: deleting data, touching production,
  changing things outside the repo, closing a PR, or force-pushing any other
  branch.
- The goal is ambiguous in a way that changes the result.
- Another PR makes this one obsolete.

Decide everything else yourself with sensible defaults, and list those decisions
in the report.

If no question tool is available, or the tool returns no answer, take the safe
path: leave the PR open and unmerged, and start your final message with the
question.
