---
name: leaving-pr-comments
description: Use whenever leaving comments on GitHub.
---

# Leaving PR Comments

Apply only to comments already authorized by the user's task or an invoked PR
workflow. This formatting skill does not itself authorize posting a comment.
In Codex prefer a connected GitHub tool when it supports the action; otherwise
use authenticated `gh` with a body file for multiline text. Follow the repository's
comment conventions when they specify a different required format.

Start directly with the substance of the comment. Do not add AI authorship
callouts, model or harness credits, or signatures.

Before posting, check the entire comment, including quoted text and
attachments, for secrets and private details.

These rules apply to top-level PR comments, inline review comments, replies to
bots or reviewers, and written explanations used before resolving or
dismissing feedback.

Write the comment itself in a direct style:

- Lead with the conclusion.
- Cite the relevant code, behavior, check, or reproduction.
- Keep it concise and avoid filler, canned thanks, or status narration.
- Distinguish verified facts from judgment.

Preview the final Markdown before posting so quoting and blank lines render
correctly. After posting, verify that GitHub returned the comment or review URL.
Resolve a review thread only after its response was posted successfully.
