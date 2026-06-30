#!/usr/bin/env python3
"""Generate Jalview user-defined colour-scheme files from aa_palettes.json.

This is the `jalaapalette` generator: the Jalview sibling of the `aapalette`
(R) and `pyaapalette` (Python) packages. All three ship the *same* amino-acid
colour palettes, read from the single source of truth `aa_palettes.json`.

The output is one Jalview "User Defined Colours" file per scheme, in the
`JalviewUserColours` XML format (namespace ``www.jalview.org/colours``) that
Jalview reads via *Colour -> User Defined -> Load scheme*. The format and the
exact serialisation below were confirmed against Jalview's
``schemas/JalviewUserColours.xsd`` and ``ColourSchemeLoader.java``, and against
real Jalview-exported ``.jc`` files.

Dependency-light: standard library only.

Usage
-----
    python generate.py              # write schemes/<id>.jc for all 10 schemes
    python generate.py --swatches   # also write swatches.html (preview)
    python generate.py --check      # generate in memory and validate, no writes

The module also exposes a small API mirroring the R/Python packages:
    list_schemes()        -> [(id, label), ...]
    get_palette(id)       -> {residue: "#RRGGBB"} for the 20 residues
    scheme_info(id)       -> metadata dict (label, source, vision, ...)
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "aa_palettes.json")
SCHEMES_DIR = os.path.join(HERE, "schemes")

# Jalview colour-scheme file extension (Jalview itself writes `.jc`; the loader
# ignores the extension, but we match Jalview's own convention).
EXT = ".jc"

# Ambiguous/unknown one-letter codes that all map to defaults.unknown_XBZJ.
# 'J' is not in Jalview's residue index and will be ignored on load; we still
# emit it for documentation/parity and it is harmless (the loader skips
# unrecognised names).
AMBIGUOUS = ["B", "Z", "X", "J"]


# --------------------------------------------------------------------------- #
# Data loading + small public API (parallels aapalette / pyaapalette)
# --------------------------------------------------------------------------- #
def load_data(path: str = JSON_PATH) -> dict:
    """Load and return the authoritative aa_palettes.json."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def list_schemes(data: dict | None = None):
    """Return [(scheme_id, label), ...] for all schemes, JSON order."""
    data = data or load_data()
    return [(sid, s["label"]) for sid, s in data["schemes"].items()]


def get_palette(scheme_id: str, data: dict | None = None) -> dict:
    """Return {residue: '#RRGGBB'} for the 20 residues, canonical order."""
    data = data or load_data()
    residues = data["residues"]
    colors = data["schemes"][scheme_id]["colors"]
    return {r: colors[r] for r in residues}


def scheme_info(scheme_id: str, data: dict | None = None) -> dict:
    """Return the metadata for a scheme (label, source, vision, names, ...)."""
    data = data or load_data()
    info = dict(data["schemes"][scheme_id])
    info.pop("colors", None)
    info["id"] = scheme_id
    return info


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def _is_hex(value: str) -> bool:
    if not isinstance(value, str) or not value.startswith("#") or len(value) != 7:
        return False
    try:
        int(value[1:], 16)
    except ValueError:
        return False
    return True


def validate(data: dict) -> None:
    """Raise ValueError unless every scheme has 20 valid 6-digit hex colours."""
    residues = data["residues"]
    if len(residues) != 20:
        raise ValueError(f"expected 20 residues, found {len(residues)}")
    for sid, scheme in data["schemes"].items():
        colors = scheme["colors"]
        for r in residues:
            if r not in colors:
                raise ValueError(f"{sid}: missing residue {r}")
            if not _is_hex(colors[r]):
                raise ValueError(f"{sid}: bad hex for {r}: {colors[r]!r}")
    for key in ("unknown_XBZJ", "gap"):
        if not _is_hex(data["defaults"][key]):
            raise ValueError(f"defaults.{key} is not valid hex")


# --------------------------------------------------------------------------- #
# Jalview file rendering
# --------------------------------------------------------------------------- #
def _rgb(hex_str: str) -> str:
    """'#A8E4A0' -> 'A8E4A0' (strip leading '#'; Jalview wants bare hex)."""
    return hex_str.lstrip("#")


def render_scheme(scheme_id: str, data: dict) -> str:
    """Return the JalviewUserColours XML text for one scheme."""
    scheme = data["schemes"][scheme_id]
    residues = data["residues"]
    colors = scheme["colors"]
    unknown = _rgb(data["defaults"]["unknown_XBZJ"])
    gap = _rgb(data["defaults"]["gap"])

    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    lines.append(
        f'<ns2:JalviewUserColours schemeName="{scheme["label"]}" '
        f'xmlns:ns2="www.jalview.org/colours">'
    )
    # 20 standard residues, canonical order
    for r in residues:
        lines.append(f'  <colour Name="{r}" RGB="{_rgb(colors[r])}"/>')
    # ambiguous / unknown codes
    for code in AMBIGUOUS:
        lines.append(f'  <colour Name="{code}" RGB="{unknown}"/>')
    # gap (Jalview's canonical token is "Gap")
    lines.append(f'  <colour Name="Gap" RGB="{gap}"/>')
    lines.append("</ns2:JalviewUserColours>")
    return "\n".join(lines) + "\n"


def write_schemes(data: dict, out_dir: str = SCHEMES_DIR) -> list[str]:
    """Write schemes/<id>.jc for every scheme; return list of paths written."""
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for sid in data["schemes"]:
        path = os.path.join(out_dir, sid + EXT)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_scheme(sid, data))
        written.append(path)
    return written


# --------------------------------------------------------------------------- #
# Swatch preview (the "render a swatch of each scheme" example)
# --------------------------------------------------------------------------- #
def render_swatches(data: dict) -> str:
    """Return a self-contained HTML preview of every scheme."""
    residues = data["residues"]
    rec = data["recommended"]
    parts = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>AApalette - Jalview colour schemes</title>",
        "<style>body{font:14px system-ui,sans-serif;margin:2rem}"
        ".sw{display:inline-block;width:2.2em;height:2.2em;line-height:2.2em;"
        "text-align:center;font-weight:600;border:1px solid #0002}"
        "h2{margin:1.4rem 0 .3rem}.src{color:#666;font-size:.85em}</style>",
        "<h1>AApalette amino-acid colour schemes (Jalview)</h1>",
        f"<p>Recommended: <b>{rec['normal']}</b> (normal), "
        f"<b>{rec['red_green_cvd']}</b> (red-green CVD), "
        f"<b>{rec['tritan_cvd']}</b> (tritan CVD). "
        "Pair colour with the residue letter for robust figures.</p>",
    ]
    for sid, scheme in data["schemes"].items():
        colors = scheme["colors"]
        parts.append(f"<h2>{sid} &mdash; {scheme['label']}</h2>")
        parts.append(f"<div class='src'>{scheme['source']} &middot; "
                     f"vision: {scheme['vision']}</div><div>")
        for r in residues:
            hexv = colors[r]
            # readable text colour on each swatch
            ri, gi, bi = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
            fg = "#000" if (ri * 299 + gi * 587 + bi * 114) / 1000 > 140 else "#fff"
            parts.append(
                f"<span class='sw' style='background:{hexv};color:{fg}' "
                f"title='{r} {hexv}'>{r}</span>"
            )
        parts.append("</div>")
    return "\n".join(parts) + "\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str]) -> int:
    data = load_data()
    validate(data)

    if "--check" in argv:
        for sid in data["schemes"]:
            render_scheme(sid, data)  # exercises rendering
        print(f"OK: {len(data['schemes'])} schemes render and validate.")
        return 0

    written = write_schemes(data)
    for p in written:
        print(f"wrote {os.path.relpath(p, HERE)}")

    if "--swatches" in argv:
        path = os.path.join(HERE, "swatches.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_swatches(data))
        print(f"wrote {os.path.relpath(path, HERE)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
