# LightFury CPL / BOM workflow

How to produce a **correct** JLCPCB pick-and-place (CPL) + BOM for the panel — and why the
old way kept failing. Read this before touching the production files.

## What went wrong last time (so we never repeat it)

The boards, schematics, and gerbers were always fine. Every failure was in the CPL, and the
causes were:

1. **Debugging by eyeballing JLC's web preview.** You can't read an offset vector off a rotated
   2 mm part in a browser, so every "fix" was a guess tested through a slow round-trip.
2. **Four bugs tangled together:** the fractional `TILT=10.9` (→ every part on a `.9°` angle that
   JLC rounds, read as "1° off"); per-part pin-1 rotation corrections; an *origin-vs-centroid*
   position question; and **stale-generation drift** — the CPL being regenerated against a
   different panel than the gerbers that got uploaded.
3. **The pad-centroid "correction" was itself the position bug.** Verified against the board's
   F.Fab body outlines: the footprint **origin already sits at each part's body center**, which is
   exactly JLC's placement datum. The pad centroid is *skewed* on any asymmetric part
   (Molex −1.8 mm, encoder +2.4 mm, all 54 PG1316S +0.9 mm, BAV70 +0.4 mm). The old inject
   script shifted everything to the centroid and dragged good parts off their pads.
4. **Post-hoc deltas on a moving baseline.** Corrections were layered on top of toolkit output
   that itself changed between runs (auto-translate on/off, re-export), and weren't idempotent.

## The rule set we proved correct

- **Position = footprint origin**, nothing else. (Origin = body center = JLC datum for every part
  on this board. Confirmed against F.Fab outlines + the gerber Edge.Cuts bbox.)
- **CPL origin = panel Edge.Cuts top-left**, Y flipped. This is *exactly* the origin KiCad/the
  Fabrication Toolkit uses when it plots the gerbers (gerber bbox `X[0,184.313] Y[-234.012,0]`
  matches the panel bbox `X[56.343,240.657] Y[20,254.012]` — same W/H, tl origin). So CPL and
  gerbers share one frame **by construction** → no global offset.
- **Rotation = footprint orientation + a per-LCSC correction.** Keep `TILT` an **integer** so every
  part lands on a whole degree. Only oriented parts whose pin-1 differs from JLC's library need a
  nonzero correction.
- **Single source of truth.** The CPL is generated directly from `lightfury_panel.kicad_pcb` — the
  same file the gerbers come from. Never hand-patch positions again.

## The tools (pure Python, no pcbnew — run anywhere)

- `kicad_panel.py` — parses the `.kicad_pcb` (footprints, pads, F.Fab outlines, Edge.Cuts bbox).
- `gen_cpl.py` — writes `positions.csv` + `bom.csv` from the panel. Idempotent.
- `render_cpl.py` — draws the placement points over the real copper pads as PNGs for **local**
  verification, so we confirm correctness *before* uploading anything.

## Procedure

Run these on the **same** panel file, in lockstep, every time the board changes:

```bat
cd C:\Users\hunte\Documents\gittyup\LightFury

:: 1. (if layout changed) re-merge + re-panelize so panel matches the halves
python panel\merge_both.py
kikit panelize -p panel\lightfury.kikit.json lightfury_both.kicad_pcb panel\lightfury_panel.kicad_pcb

:: 2. export GERBERS from panel\lightfury_panel.kicad_pcb (Fabrication Toolkit -> panel\production\),
::    then copy the zip up into the canonical order folder:
copy panel\production\lightfury_panel.zip production-panel\

:: 3. generate the CPL + BOM from the SAME panel file, straight into production-panel\
python panel\gen_cpl.py panel\lightfury_panel.kicad_pcb production-panel

:: 4. LOCAL verification — render onto the real pads and eyeball before uploading
python panel\render_cpl.py panel\lightfury_panel.kicad_pcb production-panel\positions.csv panel\verify
start panel\verify\verify_overview.png
start panel\verify\verify_parts.png
```

Upload to JLC: the three files in **`production-panel\`** — `lightfury_panel.zip` + `positions.csv` + `bom.csv`.

## The one remaining manual step: confirm rotations (do this ONCE)

Positions are now exact. The only thing the board geometry can't tell us is how JLC's library part
is oriented on its reel vs our footprint. Resolve it in a **single clean pass** — don't nudge
iteratively:

1. Upload and open JLC's assembly preview.
2. For each **oriented** part type (LED, BAV70 diode, the two SOT-23 ICs, power/reset switches,
   Molex connector, encoder, RESW), read whether it needs 0/90/180/270°. JLC's editor gives exact
   values — read, don't guess.
3. Put each into `ROT_CORR` in `gen_cpl.py`, keyed by LCSC. `C965555` (LED) = 180 is already
   confirmed. Re-run step 3 above (positions are unaffected) and re-upload.

If a part's *body* ever looks off its pads in JLC (not just rotated), that's a datum exception —
add a `POS_OVERRIDE[lcsc] = (dx, dy)` in part-local mm. None are expected on this board.

## Hard rules

- `TILT` in `merge_both.py` stays an **integer**.
- Gerbers and CPL always come from the **same** `lightfury_panel.kicad_pcb` generation. If you
  re-panelize, you re-export both. No mixing generations.
- `inject_resw1.py` is **superseded** by `gen_cpl.py` and kept only for reference. Don't run it.
