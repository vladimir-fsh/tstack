# Claude review cycle

An actionable `babysit-pr` invocation authorizes posting the Claude request,
fixing and pushing the first round's valid findings, and deleting only that
round's request and Claude feedback after handling it. Later fix rounds require
the user's yes. Keep the PR open at each decision point; do not merge while
feedback or a repeat-round decision remains pending.

## Start and wait

1. Identify the PR, checkout, and current head. Inspect repository instructions,
   the Claude integration, and previous invocations to confirm the trigger and
   responding account(s). If Claude is unavailable, report the missing setup;
   do not silently substitute another reviewer or install an integration.
   Disable existing auto-merge and remove the PR from a merge queue before
   making changes, so it stays open for the decision. Report that change; if
   automatic merging cannot be prevented, stop and report the blocker.
2. Keep a round record in the task context: PR, round number, reviewed head,
   request ID/URL/time, baseline feedback IDs, linked run ID, and Claude response
   IDs/URLs/bodies. This record survives the user decision and identifies exactly
   what may be deleted. On resume, reconcile it with live state before acting.
3. Start the single `pr-wait` watcher with `--until any-change` and
   `--review-author LOGIN` for each confirmed account. With no saved watcher state,
   wait for `baseline recorded` before posting, so a fast reply is not silently
   baselined. With saved state, wait for startup and inspect live feedback again.
   Use `leaving-pr-comments` to post one request, using the configured trigger
   (normally `@claude`), for example:

   ```text
   @claude Review this pull request at head <full SHA> for actionable bugs in
   scope. Report findings and a final verdict in this PR; do not modify code or
   push commits. Include the reviewed SHA in your final response.
   ```

   Record the returned comment ID and URL immediately. If posting times out,
   inspect live comments for that request before retrying; avoid duplicate runs.
4. Wait for the response to this request. Match the request/run link, author,
   time, and reviewed head; a later comment by the same bot alone is insufficient.
   Fetch full comment/review bodies, including inline comments and pagination,
   whenever activity arrives and before restarting the watcher. The watcher only
   observes the last 100 top-level comments/reviews and can baseline a response
   on a fresh run, so inspect live feedback again after starting it on resume.
   Ignore unrelated events for completion and continue waiting.
5. A progress comment or green CI is not a completed review. Follow the linked
   Claude run when available; `gh run watch <run-id> --repo <owner/name>
   --exit-status` can wait on that exact run instead of `pr-wait` (stop the owned
   `pr-wait` first). After success, fetch the final response and verify its verdict
   covers the recorded head. Without a linked run, require an explicit final
   result attributable to this request. A failed/cancelled run or absent result
   is a blocker, not a clean review. If no response starts within 10 minutes,
   inspect the integration/run once and report the blocker rather than reposting.
   Collect process output in waits of at most 60 seconds and remain active.

If the head changes during review or while awaiting the user, reconcile the
findings against the new diff and report the stale coverage. Do not claim the
old result reviewed the new head or silently reset the automatic-round allowance.

## One fix, cleanup, and re-review step

Run this once after the initial completed review, then only after each user yes.

1. Evaluate every finding against the current source. Fix valid in-scope issues,
   verify the changes, commit, and push to the PR branch. Record evidence for
   dismissed findings and the outcome in the chat before deleting feedback;
   follow `babysit-pr`'s review guidance for any required replies. If there are no
   valid fixes, record that outcome and continue through cleanup and re-review
   once without an empty commit. Failed verification or push leaves the comments
   intact and stops the step until resolved.
2. After the fixes are verified and pushed (or the no-fix outcome is recorded),
   delete the recorded trigger comment and Claude's feedback from this round.
   Re-fetch each object before deletion and confirm its author, PR, and round.
   Keep unrelated comments, earlier rounds not owned by this task, and human
   replies. If a thread contains human discussion, preserve it and report why.
   Use a connected GitHub tool when it supports deletion; otherwise use `gh api`
   with the object's actual type:

   - Top-level PR comments: `DELETE repos/{owner}/{repo}/issues/comments/{id}`.
   - Inline review comments: `DELETE repos/{owner}/{repo}/pulls/comments/{id}`.

   Verify each deletion. Treat an already absent object as complete only after
   confirming access to the PR. GitHub's submitted review object cannot be deleted
   by the pending-review endpoint; do not substitute dismissal or blanking.
   If permissions or object type prevent cleanup, report the exact remaining
   URLs and stop before reposting. Resume at incomplete cleanup after resolution,
   without reapplying fixes or spending another round.
3. Record the new head, post one fresh Claude request, and wait for its completed
   review using **Start and wait**. Keep the new request and response visible.
4. Inspect the new findings without editing code. Summarize the previous fixes,
   which findings are new, repeated, dismissed, or still valid, and the proposed
   next fixes with their impact. Stop the owned watcher and ask the user whether
   to apply those fixes and run another round. Include the PR/review links and
   make clear that yes includes cleanup and a fresh Claude request.

## Decision and resumption

Use an available question tool, with yes/no choices, and keep the answer pending.
Explain that this skill requires the decision after each re-review, and link to
this file. If a question tool is unavailable, end with the question. Silence is
not yes. Do not fix the next findings, delete this round's comments, or post a new
request while waiting. Read-only inspection can continue.

- **Yes:** run **One fix, cleanup, and re-review step** once, then ask again.
- **No:** leave the latest review and request visible, report remaining findings
  and CI state, and stop. Do not treat declined fixes as resolved or merge.
- **No actionable findings:** report the clean Claude result and CI state, keep
  the final comments, and finish without asking for an empty fix round. A calling
  workflow may continue to its merge gate only if all other requirements pass.

## API references

- [Claude updates one comment with progress and results](https://github.com/anthropics/claude-code-action/blob/main/docs/faq.md).
- [GitHub only deletes pending review objects](https://docs.github.com/en/rest/pulls/reviews#delete-a-pending-review-for-a-pull-request).
