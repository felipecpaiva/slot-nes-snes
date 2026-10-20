"""The card tools on a mounted main card whose Config/expansion.txt moves PS1 to the Expansion Card (ADR 0098).

    python3 -m unittest tools/tests/test_expansion_tools.py
"""
import contextlib
import importlib.util
import io
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, "..", file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fl = load("fetch_labels", "fetch-labels.py")
hk = load("hacks", "hacks.py")


class Cards(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.card, self.exp = os.path.join(t.name, "card"), os.path.join(t.name, "exp")
        for d in ("card/Config", "card/Games/PS1", "card/Games/GBA", "exp/Games/PS1"):
            os.makedirs(os.path.join(t.name, d))
        fl.spit(os.path.join(self.card, "Config", "expansion.txt"), "# moved\n PS1  # discs\r\n../x\n", "w")
        fl.spit(os.path.join(self.exp, "Games", "PS1", "Game (USA).chd"), b"chd")
        fl.spit(os.path.join(self.card, "Games", "GBA", "Pokemon.gba"), b"gba")

    def test_expansion_txt_is_read_like_the_launcher_reads_it(self):
        self.assertEqual(fl.expansion_systems(self.card), {"PS1"})
        self.assertEqual(fl.expansion_systems(self.exp), set())

    def test_fetch_labels_reads_ps1_from_the_expansion_card(self):
        roms, _ = fl.scan_card(self.card, "PS1", self.exp)
        self.assertEqual([r.stem for r in roms], ["Game (USA)"])

    def test_fetch_labels_says_why_it_skips_ps1_without_the_expansion_card(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            roms, _ = fl.scan_card(self.card, "PS1")
        self.assertEqual(roms, [])
        self.assertIn("is on the Expansion Card", out.getvalue())

    def test_fetch_labels_reads_other_systems_from_the_main_card(self):
        roms, _ = fl.scan_card(self.card, "GBA", self.exp)
        self.assertEqual([r.stem for r in roms], ["Pokemon"])

    def test_hacks_maps_ps1_to_the_expansion_card_and_nothing_else(self):
        card = hk.LocalCard(self.card, self.exp)
        self.assertEqual(card.names("Games/PS1"), ["Game (USA).chd"])
        self.assertEqual(card.p("Saves/PS1/Game (USA).srm"), os.path.join(self.card, "Saves", "PS1", "Game (USA).srm"))
        self.assertEqual(card.p("Games/GBA"), os.path.join(self.card, "Games", "GBA"))

    def test_hacks_refuses_ps1_on_the_main_card_alone(self):
        with self.assertRaisesRegex(hk.Refuse, "is on the Expansion Card"):
            hk.LocalCard(self.card).names("Games/PS1")


if __name__ == "__main__":
    unittest.main()
