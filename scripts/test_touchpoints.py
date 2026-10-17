#!/usr/bin/env python3
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import touchpoints  # noqa: E402

CTX = "impl App {"


def diff(*starts, bodies=None, ctx=CTX, path="crates/slot/src/app.rs"):
    out = [f"diff --git a/{path} b/{path}", f"--- a/{path}", f"+++ b/{path}"]
    for i, s in enumerate(starts):
        body = bodies[i] if bodies else "x"
        out += [f"@@ -{s},0 +{s + 1},1 @@ {ctx}", f"+    {body}();"]
    return "\n".join(out) + "\n"


def regenerate(old_map, new_diff):
    rows = touchpoints.assign(touchpoints.hunks(new_diff), touchpoints.old_rows(old_map))
    return touchpoints.render(rows, {})


def reasons(text):
    return {(r["start"], r["why"]) for r in touchpoints.old_rows(text)}


def why_at(text, start):
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) == 6 and cells[2] == str(start):
            return cells[5]
    return None


def seeded(*starts, bodies=None):
    text = regenerate("", diff(*starts, bodies=bodies))
    for i, s in enumerate(starts):
        text = re.sub(
            rf"(#L{s}#[0-9a-f]{{8}} \| {s} \| \+1/-0 \| {re.escape(CTX)} \| ){re.escape(touchpoints.TODO)} \|",
            rf"\g<1>reason {i} |",
            text,
        )
    return text


class TouchPoints(unittest.TestCase):
    def test_a_hunk_inserted_mid_file_leaves_every_other_reason_on_its_row(self):
        old = seeded(100, 110, 200)
        new = regenerate(old, diff(100, 105, 110, 200))
        self.assertEqual(why_at(new, 100), "reason 0")
        self.assertEqual(why_at(new, 105), touchpoints.TODO)
        self.assertEqual(why_at(new, 110), "reason 1")
        self.assertEqual(why_at(new, 200), "reason 2")

    def test_a_rebase_that_moves_every_line_further_than_the_gap_keeps_the_reasons(self):
        old = seeded(100, 110, 200)
        new = regenerate(old, diff(120, 130, 220))
        self.assertEqual([why_at(new, s) for s in (120, 130, 220)], ["reason 0", "reason 1", "reason 2"])

    def test_a_rebase_plus_a_new_hunk_keeps_the_reasons_on_one_shared_offset(self):
        old = seeded(100, 110, 200)
        new = regenerate(old, diff(120, 125, 130, 220))
        self.assertEqual([why_at(new, s) for s in (120, 130, 220)], ["reason 0", "reason 1", "reason 2"])
        self.assertEqual(why_at(new, 125), touchpoints.TODO)

    def test_an_ambiguous_move_is_flagged_and_never_reassigned(self):
        old = seeded(100, 110)
        new = regenerate(old, diff(103, 117, 140))
        for s in (103, 117, 140):
            self.assertTrue(why_at(new, s).startswith(touchpoints.TODO + " (ambiguous"), why_at(new, s))
        self.assertNotIn("reason", "".join(r for _, r in reasons(new)))

    def test_a_hunk_dropped_and_another_added_in_the_same_context_is_never_paired(self):
        old = seeded(100, 110, 200, bodies=["a", "b", "dropped"])
        new = regenerate(old, diff(100, 110, 300, bodies=["a", "b", "added"]))
        self.assertEqual([why_at(new, s) for s in (100, 110)], ["reason 0", "reason 1"])
        self.assertTrue(why_at(new, 300).startswith(touchpoints.TODO), why_at(new, 300))
        self.assertNotIn("reason 2 |", new)

    def test_unchanged_hunks_moved_unevenly_keep_their_reasons_by_their_content(self):
        bodies = ["alpha", "beta", "gamma"]
        old = seeded(100, 110, 200, bodies=bodies)
        new = regenerate(old, diff(105, 140, 230, bodies=bodies))
        self.assertEqual([why_at(new, s) for s in (105, 140, 230)], ["reason 0", "reason 1", "reason 2"])

    def test_regenerating_an_unchanged_diff_changes_nothing(self):
        old = seeded(100, 110, 200)
        self.assertEqual(regenerate(old, diff(100, 110, 200)), old)

    def test_a_row_in_the_old_ordinal_key_format_keeps_its_reason(self):
        legacy = re.sub(r"#L100#[0-9a-f]{8}", "#1", re.sub(r"#L110#[0-9a-f]{8}", "#2", seeded(100, 110)))
        new = regenerate(legacy, diff(100, 105, 110))
        self.assertEqual([why_at(new, s) for s in (100, 105, 110)], ["reason 0", touchpoints.TODO, "reason 1"])


if __name__ == "__main__":
    unittest.main()
