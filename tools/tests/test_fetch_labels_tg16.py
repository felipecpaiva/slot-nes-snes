"""tools/fetch-labels.py TurboGrafx-16 route (issue 89), offline: the shared fixtures of test_fetch_labels.py.

    python3 -m unittest tools/tests/test_fetch_labels_tg16.py
"""
import json
import os
import sys
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_fetch_labels as t  # noqa: E402

fl, PNG, JEU, crc = t.fl, t.PNG, t.JEU, t.crc

HUCARD = bytes(range(256)) * 32


class TurboGrafx(t.Base):
    ss_http = t.NesSnes.ss_http
    run_ss = t.NesSnes.run_ss

    def test_the_tg16_row_names_its_folder_extension_dat_and_screenscraper_id_31(self):
        self.assertEqual(fl.SYSTEMS["TG16"], ("pcengine", {".pce"}, ["NEC - PC Engine - TurboGrafx 16"], 31))
        self.assertNotIn("TG16", fl.ART_SYSTEMS)
        self.assertNotIn("TG16", fl.MEDIA)

    def test_a_headered_and_a_headerless_hucard_give_the_same_crc(self):
        bare = fl.Rom("Bonk", len(HUCARD), lambda: HUCARD)
        headered = fl.Rom("Bonk", len(HUCARD) + 512, lambda: bytes(512) + HUCARD)
        self.assertEqual(next(headered.crcs("TG16")), zlib.crc32(HUCARD))
        self.assertIn(bare.whole(), list(headered.crcs("TG16")))

    def test_a_hucard_whose_size_is_not_a_header_off_a_bank_is_hashed_whole_only(self):
        odd = bytes(8192 + 100)
        self.assertEqual(list(fl.Rom("Odd", len(odd), lambda: odd).crcs("TG16")), [zlib.crc32(odd)])

    def test_a_headered_hucard_on_the_card_matches_the_no_intro_dat_and_gets_its_label(self):
        self.rom("TG16", "Bonk's Adventure.pce", bytes(512) + HUCARD)
        self.rom("TG16", "Madou Monogatari.sgx", b"x" * 64)
        r = self.dat("TG16", ("Bonk's Adventure (USA)", crc(HUCARD)))
        stats = self.run_ss("TG16", r, {}, (200, json.dumps(JEU).encode(), None),
                            ["--card", self.card, "--only", "TG16"])
        self.assertEqual((stats["matched"], stats["written"], stats["unknown"]), (1, 1, 0))
        self.assertEqual(self.label("TG16", "Bonk's Adventure"), PNG)
        self.assertIsNone(self.label("TG16", "Madou Monogatari"))
        self.assertTrue(any("systemeid=31" in c for c in self.http.calls), self.http.calls)


if __name__ == "__main__":
    unittest.main()
