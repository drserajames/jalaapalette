#!/usr/bin/env python3
"""Tests for the jalaapalette Jalview colour-scheme generator.

Run with either:
    python -m unittest test_schemes
    python test_schemes.py

The tests prove that:
  (a) the bundled aa_palettes.json loads and every scheme has 20 valid hex
      colours (shared invariant with aapalette / pyaapalette);
  (b) the generated .jc files parse as JalviewUserColours XML and contain all
      20 residues, the ambiguous codes, and a gap entry, all with valid hex;
  (c) every colour in every generated file equals the JSON exactly -- the
      cross-package consistency guarantee.
"""

import os
import unittest
import xml.etree.ElementTree as ET

import generate

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMES_DIR = os.path.join(HERE, "schemes")
NS = "www.jalview.org/colours"

EXPECTED_SCHEMES = [
    "hue", "redgreen", "tritan",            # this work (new)
    "clustal", "zappo", "taylor", "lesk",   # classical
    "cinema", "rasmol", "shapely",
]


def _parse_colours(xml_text):
    """Return {Name: RGB} from JalviewUserColours XML text."""
    root = ET.fromstring(xml_text)
    assert root.tag == f"{{{NS}}}JalviewUserColours", root.tag
    out = {}
    for el in root:
        if el.tag.endswith("colour"):
            out[el.attrib["Name"]] = el.attrib["RGB"]
    return root, out


class TestData(unittest.TestCase):
    def setUp(self):
        self.data = generate.load_data()

    def test_validate_passes(self):
        generate.validate(self.data)  # raises on failure

    def test_ten_schemes_expected_ids(self):
        self.assertEqual(list(self.data["schemes"].keys()), EXPECTED_SCHEMES)

    def test_residue_order_canonical(self):
        self.assertEqual(
            self.data["residues"],
            list("ACDEFGHIKLMNPQRSTVWY"),
        )

    def test_every_scheme_20_valid_hex(self):
        residues = self.data["residues"]
        for sid, scheme in self.data["schemes"].items():
            colors = scheme["colors"]
            self.assertEqual(len(set(residues) & set(colors)), 20, sid)
            for r in residues:
                self.assertTrue(generate._is_hex(colors[r]), f"{sid}:{r}")


class TestRendering(unittest.TestCase):
    def setUp(self):
        self.data = generate.load_data()

    def test_render_parses_and_matches_json(self):
        residues = self.data["residues"]
        unknown = self.data["defaults"]["unknown_XBZJ"].lstrip("#")
        gap = self.data["defaults"]["gap"].lstrip("#")
        for sid, scheme in self.data["schemes"].items():
            xml_text = generate.render_scheme(sid, self.data)
            root, colours = _parse_colours(xml_text)

            # schemeName == JSON label (identical label across packages)
            self.assertEqual(root.attrib.get("schemeName"), scheme["label"])

            # all 20 residues present, equal to JSON (hex without '#')
            for r in residues:
                self.assertIn(r, colours, f"{sid} missing {r}")
                self.assertEqual(
                    colours[r].upper(),
                    scheme["colors"][r].lstrip("#"),
                    f"{sid}:{r} colour mismatch vs JSON",
                )
                # valid 6-digit hex
                int(colours[r], 16)
                self.assertEqual(len(colours[r]), 6)

            # ambiguous + gap handled via defaults
            for code in ("B", "Z", "X", "J"):
                self.assertEqual(colours[code].upper(), unknown.upper(), sid)
            self.assertEqual(colours["Gap"].upper(), gap.upper(), sid)


class TestGeneratedFiles(unittest.TestCase):
    """Validate the on-disk schemes/*.jc (run generate.py first)."""

    def setUp(self):
        self.data = generate.load_data()
        if not os.path.isdir(SCHEMES_DIR):
            self.skipTest("schemes/ not generated; run `python generate.py`")

    def test_one_file_per_scheme(self):
        for sid in EXPECTED_SCHEMES:
            path = os.path.join(SCHEMES_DIR, sid + generate.EXT)
            self.assertTrue(os.path.isfile(path), path)

    def test_files_match_json(self):
        residues = self.data["residues"]
        for sid, scheme in self.data["schemes"].items():
            path = os.path.join(SCHEMES_DIR, sid + generate.EXT)
            if not os.path.isfile(path):
                self.skipTest(f"{path} not generated")
            with open(path, encoding="utf-8") as fh:
                _, colours = _parse_colours(fh.read())
            for r in residues:
                self.assertEqual(
                    colours[r].upper(),
                    scheme["colors"][r].lstrip("#"),
                    f"{sid}:{r} on-disk colour mismatch vs JSON",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
