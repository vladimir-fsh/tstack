"""Offline regression checks for reviewers that edit their progress comments."""

import contextlib
import copy
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pr-wait"
LOADER = importlib.machinery.SourceFileLoader("pr_wait", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
pr_wait = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(pr_wait)


def comment(body="Working", login="github-actions", node_id="C1"):
    return {"id": node_id, "url": "https://github.com/o/r/pull/1#" + node_id,
            "body": body, "author": {"login": login, "__typename": "Bot"}}


class ReviewActivityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        state = patch.object(pr_wait, "STATE_DIR", Path(self.temp.name))
        state.start()
        self.addCleanup(state.stop)
        self.pr = {
            "state": "OPEN", "url": "https://github.com/o/r/pull/1",
            "headRefOid": "a" * 40, "baseRefName": "main", "baseRef": None,
            "mergeStateStatus": "CLEAN", "author": {"login": "owner"},
            "viewer": "owner", "comments": {"nodes": [comment()]},
            "reviews": {"nodes": []}, "reviewThreads": {"nodes": []},
        }

    def watcher(self, authors=("github-actions",)):
        watcher = pr_wait.Watcher("o/r", 1, "any-change", 20, authors)
        watcher.required = set()
        watcher.fetch_pr = lambda: copy.deepcopy(self.pr)
        watcher.fetch_checks = lambda: {}
        return watcher

    def poll(self, watcher):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            try:
                watcher.poll()
            except SystemExit as error:
                self.assertEqual(error.code, 0)
        return output.getvalue()

    def baseline(self, watcher):
        self.assertEqual(self.poll(watcher), "")
        watcher.save()
        watcher.baseline = False

    def test_progress_edit_emits_once_and_survives_restart(self):
        watcher = self.watcher()
        self.baseline(watcher)
        self.pr["comments"]["nodes"][0]["body"] = "Done: no findings"
        self.assertIn("Done: no findings", self.poll(watcher))
        self.assertEqual(self.poll(watcher), "")
        self.assertEqual(self.poll(self.watcher()), "")
        self.pr["comments"]["nodes"][0]["body"] = "Done: one finding"
        self.assertIn("one finding", self.poll(self.watcher()))

    def test_bot_review_state_and_inline_edits(self):
        self.pr["reviews"]["nodes"] = [dict(comment(node_id="R1"), state="PENDING")]
        self.pr["reviewThreads"]["nodes"] = [{"isResolved": False,
            "path": "app.py", "line": 3, "comments": {"nodes": [comment(node_id="I1")]}}]
        watcher = self.watcher()
        self.baseline(watcher)
        self.pr["reviews"]["nodes"][0]["state"] = "COMMENTED"
        self.pr["reviewThreads"]["nodes"][0]["comments"]["nodes"][0]["body"] = "Final inline finding"
        output = self.poll(watcher)
        self.assertIn("#R1", output)
        self.assertIn("Final inline finding", output)

    def test_new_selected_comment_bypasses_status_bot_filter(self):
        watcher = self.watcher(("GitHub-Actions[bot]",))
        self.baseline(watcher)
        self.pr["comments"]["nodes"].append(comment("New review", node_id="C2"))
        self.assertIn("New review", self.poll(watcher))

    def test_html_completion_marker_is_not_discarded(self):
        watcher = self.watcher()
        self.baseline(watcher)
        self.pr["comments"]["nodes"][0]["body"] += "<!-- complete -->"
        self.assertIn("review activity", self.poll(watcher))

    def test_default_filter_and_exact_author_matching_are_preserved(self):
        for authors in ((), ("github",)):
            with self.subTest(authors=authors):
                watcher = self.watcher(authors)
                self.baseline(watcher)
                self.pr["comments"]["nodes"][0]["body"] += " updated"
                self.pr["reviews"]["nodes"] = [dict(comment(node_id="R2"), state="COMMENTED")]
                self.assertEqual(self.poll(watcher), "")


if __name__ == "__main__":
    unittest.main()
