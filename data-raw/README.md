# data-raw — regeneration

The amino-acid colour data for this package comes from **one source of truth**:

    ../aa_palettes.json

This file is shared verbatim with the sibling packages `aapalette` (R) and
`pyaapalette` (Python). The three packages must stay byte-for-byte consistent on
the hex values, scheme IDs, labels, residue order, and the unknown/gap defaults.

**Do not edit the hex values by hand**, and do not edit them only here — any
colour change must be made in `aa_palettes.json` in lockstep across all three
packages.

## Rebuilding the Jalview files

From the package root:

```sh
python generate.py                # writes ../schemes/<id>.jc for all 10 schemes
python generate.py --swatches     # also writes ../swatches.html
python -m unittest test_schemes   # verifies the output equals the JSON exactly
```

`generate.py` reads `aa_palettes.json`, validates that every scheme has 20 valid
6-digit hex colours, and emits one `JalviewUserColours` file per scheme into
`schemes/`. The test suite re-parses each generated file and asserts equality
with the JSON, so a stale or hand-edited file is caught immediately.
