# jalaapalette — amino-acid colour schemes for Jalview

Importable [Jalview](https://www.jalview.org/) colour-scheme files for **10
amino-acid colour palettes**, generated from a single source of truth
(`aa_palettes.json`).

This is the **Jalview** sibling of two companion packages that ship the *same*
palettes — identical scheme IDs, identical hex values, identical residue
handling:

| Package        | Ecosystem | Deliverable                       |
| -------------- | --------- | --------------------------------- |
| `aapalette`    | R         | R package                         |
| `pyaapalette`  | Python    | Python package                    |
| **`jalaapalette`** | **Jalview** | **`JalviewUserColours` `.jc` files** (this repo) |

The headline value is the **3 new schemes** — `hue`, `redgreen`, `tritan` —
since Jalview already ships clustal/zappo/taylor/rasmol built in. All 10 are
included anyway for parity with the R/Python packages.

## The 10 schemes

New (this project, **CC-BY-4.0**):

| ID         | Label                          | For                                   |
| ---------- | ------------------------------ | ------------------------------------- |
| `hue`      | AApalette hue (normal vision)  | **normal vision** (recommended default) |
| `redgreen` | AApalette red-green CVD safe   | **red-green CVD** (deuteranopia & protanopia) |
| `tritan`   | AApalette tritan CVD safe      | **tritanopia**                        |

Classical (community-standard, attributed — see below):

| ID        | Label                | Source                                  |
| --------- | -------------------- | --------------------------------------- |
| `clustal` | Clustal X            | Clustal X / Jalview                     |
| `zappo`   | Zappo                | Zappo / Jalview                         |
| `taylor`  | Taylor               | Taylor (1997) / Jalview                 |
| `lesk`    | Lesk                 | Lesk, *Introduction to Protein Architecture* |
| `cinema`  | Cinema               | CINEMA (Parry-Smith et al. 1998)        |
| `rasmol`  | RasMol amino         | RasMol amino colour scheme              |
| `shapely` | RasMol shapely       | RasMol/Jmol shapely (Fletterick models) |

**Recommended:** `hue` for normal vision · `redgreen` for red-green colour-vision
deficiency · `tritan` for tritan deficiency.

## What's in this repo

```
aa_palettes.json     # SINGLE SOURCE OF TRUTH — never edit the hex values
generate.py          # generator (stdlib only): reads the JSON, writes the .jc files
test_schemes.py      # tests: files parse + equal the JSON exactly
schemes/<id>.jc      # 10 generated Jalview colour-scheme files
swatches.html        # optional preview (generate.py --swatches)
LICENSE              # MIT (code)
LICENSE-DATA         # CC-BY-4.0 (data)
```

## The file format

Each `schemes/<id>.jc` is a Jalview **User Defined Colours** file in the
`JalviewUserColours` XML format (namespace `www.jalview.org/colours`). This is
the exact format Jalview reads via *Colour → User Defined → Load scheme* and
writes via *Save scheme*. Confirmed against Jalview's
`schemas/JalviewUserColours.xsd` and `ColourSchemeLoader.java`.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ns2:JalviewUserColours schemeName="AApalette hue (normal vision)" xmlns:ns2="www.jalview.org/colours">
  <colour Name="A" RGB="769214"/>
  ...
  <colour Name="X" RGB="BEBEBE"/>
  <colour Name="Gap" RGB="FFFFFF"/>
</ns2:JalviewUserColours>
```

- `RGB` is a **6-digit hex string with no `#`** (Jalview parses it as
  base-16).
- `Name` is the one-letter residue code.
- **Residue / symbol handling** (identical across the three packages):
  - the 20 standard residues `A C D E F G H I K L M N P Q R S T V W Y`;
  - ambiguous/unknown codes `B`, `Z`, `X`, `J` → `#BEBEBE` (grey);
  - gap → `Name="Gap"`, `#FFFFFF` (white).
- **Case:** we emit **uppercase entries only.** Jalview then colours residues
  case-insensitively, so lower-case residue letters automatically receive the
  same colour. (Adding lower-case entries would flip the scheme into
  case-sensitive mode — which Jalview's own exports avoid — so we don't.)

## Loading a scheme in Jalview

**GUI (any platform):**

1. Open an alignment in Jalview.
2. Menu **Colour → User Defined…** — the *User Defined Colours* dialog opens.
3. Click **Load scheme** and choose a file from `schemes/`, e.g.
   `schemes/hue.jc`.
4. The scheme name (e.g. *AApalette hue (normal vision)*) appears; click
   **Apply** then **Close**. The scheme is now applied and is remembered for
   future sessions (it also appears directly under the **Colour** menu).

The file extension does not matter to Jalview's loader (`.jc` is Jalview's own
convention); the content is what's parsed.

**Reuse across sessions / projects:** once loaded, a user-defined scheme is
saved in your Jalview preferences and offered in the **Colour** menu of every
new alignment window. To bake a colouring into a shareable Jalview project,
apply the scheme and then **File → Save Project** (`.jvp`) — the colours travel
with the project.

**Verifying the files load:** open each file via *Colour → User Defined → Load
scheme* in a current Jalview release and confirm the 20 residues colour as
expected (compare against `swatches.html`). The bundled test suite additionally
parses every file and checks it against the JSON.

## Example — render a swatch of each scheme

```sh
python generate.py --swatches      # writes swatches.html
# then open swatches.html in a browser
```

`swatches.html` shows every scheme as a row of coloured residue tiles (each
tile labelled with its one-letter code — redundant coding, see the caveat
below).

## Attribution

The **`hue`, `redgreen`, and `tritan`** schemes are from this project — the
**AApalette** amino-acid colour alphabet — and are released **CC-BY-4.0**.
Please cite the forthcoming methods write-up:

> *AApalette: amino-acid colour alphabets for normal and colour-vision-deficient
> viewers.* The AApalette Authors, 2026. (Citation forthcoming — placeholder.)

The **classical** schemes are reproduced for interoperability and attributed to
their original sources:

- **clustal** — Clustal X / Jalview
- **zappo** — Zappo / Jalview
- **taylor** — Taylor (1997) / Jalview
- **lesk** — Lesk, *Introduction to Protein Architecture*
- **cinema** — CINEMA (Parry-Smith et al. 1998)
- **rasmol** — RasMol amino colour scheme
- **shapely** — RasMol / Jmol shapely (Fletterick "Shapely" models)

### Deliberate exclusions

Polychrome, Green-Armytage, and Biotite/Gecos (flower/blossom/sunset) palettes,
and any personal/agent palettes, are **intentionally not included**.

## Colour-vision (CVD) caveat

**No 20-colour palette is safe for every deficiency at once.** For robust
figures, **pair colour with the residue letter** (redundant coding) rather than
relying on colour alone. The `redgreen` scheme is optimised for red-green
deficiency (not tritan); the `tritan` scheme is optimised for tritanopia (not
red-green). The ΔE values recorded in `aa_palettes.json` are **CIEDE2000
minima** (the smallest perceptual distance between any two residues under each
simulated vision type).

## Regenerating the scheme files

`aa_palettes.json` is the **single source of truth** and is shared verbatim with
the `aapalette` (R) and `pyaapalette` (Python) packages. **Never edit the hex
values by hand.** To rebuild every `schemes/*.jc` from it:

```sh
python generate.py            # regenerate all 10 .jc files
python generate.py --check    # validate without writing
python -m unittest test_schemes   # run the test suite
```

If a colour ever needs to change, edit it in `aa_palettes.json` (in lockstep
with the sibling packages) and regenerate — the test suite enforces that the
generated files equal the JSON exactly.

## Licensing

- **Code** (`generate.py`, `test_schemes.py`, tooling): **MIT** — see `LICENSE`.
- **Data** (the new schemes and `aa_palettes.json` values): **CC-BY-4.0** — see
  `LICENSE-DATA`.
