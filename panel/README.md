# LightFury panelization (KiKit)

Run on **your machine** (KiKit drives KiCad's `pcbnew` — it won't run in the sandbox). The
per-half boards (`lightfury_left/right.kicad_pcb`) are the source of truth; everything below
rebuilds the combined board and panel from them, so re-run it any time a half changes.

**Environment:** use the **KiCad Command Prompt** (so `python` = KiCad's Python with `pcbnew`).
KiKit's `kikit.exe` installs to `...KiCad\9.0\3rdparty\Python311\Scripts`, which isn't on PATH by
default — add it for the session before the `kikit` commands:

```bat
set PATH=%PATH%;C:\Users\hunte\Documents\KiCad\9.0\3rdparty\Python311\Scripts
```

## Full workflow (in order)

```bash
cd LightFury

# 1. Merge the two halves -> lightfury_both.kicad_pcb (right-half refs get a _2 suffix,
#    nets get L_/R_ prefixes so the halves stay electrically distinct). Replaces the old
#    by-hand merge.
python panel/merge_both.py

# 2. Frame it into a panel.
kikit panelize -p panel/lightfury.kikit.json lightfury_both.kicad_pcb panel/lightfury_panel.kicad_pcb

# 3. GERBERS ONLY from the panel: open it in pcbnew and run the **Fabrication Toolkit** plugin
#    (NOT `kikit fab jlcpcb` — needs a schematic the _2 refs can't match). It writes to the
#    transient panel/production/ ; copy the gerber zip up to the canonical order folder:
copy panel\production\lightfury_panel.zip production-panel\

# 4. BOM + CPL straight from the panel (origin datum, integer rotations, RESW1 injected,
#    per-part offsets) -> the canonical production-panel/ . Then render to verify locally.
python panel/gen_cpl.py panel/lightfury_panel.kicad_pcb production-panel
python panel/render_cpl.py panel/lightfury_panel.kicad_pcb production-panel/positions.csv panel/verify
```

The three files you upload to JLC live in **production-panel/**. Full detail + the one-time JLC
rotation-confirmation step: **CPL_WORKFLOW.md**.

## Notes / gotchas

- **`post.millradius` eats the RE1 foot cutouts.** The CKW12 encoder has two ~2 mm diamond
  (45°-square) Edge.Cuts cutouts per half for RE1's feet. `millradius` simulates a 1 mm-radius
  (2 mm Ø) router bit across the *whole* substrate — including internal holes — so a sub-bit-size
  cutout gets erased. Result: the diamonds are in `lightfury_both` but vanish from the panel.
  Fix is in the preset: use **`millradiusouter`** (mills only the outer ring, leaves internal
  cutouts intact) instead of `millradius`. If your KiKit predates `millradiusouter`, set
  `millradius` to `0mm` and re-inject the 4 diamonds afterward (translate the both-board loops by
  the panel placement offset — footprint-only, so BOM/CPL are untouched). **Always eyeball the
  encoder cutouts in the panel before ordering.**
- **`merge_both.py`** is the script that replaces your old hand-merge. Right-half refs become
  `*_2` (uniform — simpler than the old mixed RS/RLED/_2 scheme; JLC only cares that refs are
  unique and that BOM ↔ CPL agree, which they will since both come from this pipeline).
  `appendBoard`'s signature is the line most likely to need a tweak for your KiKit version.
- **Prereq:** the per-half schematics need their `LCSC` fields filled and pushed to the PCBs
  (Update PCB from Schematic / F8) *before* step 1, or the BOM comes out without part numbers.
- **`gen_cpl.py`** (pure Python, no pcbnew) builds the BOM + CPL directly from the panel: position
  = footprint origin, per-LCSC `ROT_CORR`/`POS_OVERRIDE` tables, and RESW1 (C262417) injected from
  the encoder's S1/S2 pads. It supersedes the old `inject_resw1.py` (now in `old_cruft/`).
  `render_cpl.py` overlays the result on the real pads for local verification before uploading.
- The preset's 1×1 grid frames the merged pair (two outlines) as one unit, bridging each half
  to the rails with mouse-bite tabs. If KiKit complains about the two outlines, the fallback is
  to move framing into `merge_both.py` (KiKit Python API) — ping me and I'll extend it.

## Preset details (lightfury.kikit.json)

- **Rails** top & bottom, 5 mm, 3 mm gap (`railstb`).
- **Tabs** every 25 mm, 3 mm wide, **mouse-bites** (0.5 mm drills @ 0.8 mm) — better than V-cuts
  for the filleted/curved outlines.
- **Tooling holes** (1.5 mm) and **fiducials** (1 mm copper / 2 mm mask) in the rail corners.
- `JLCJLCJLCJLC` order token in the rail, `millradius 1 mm` for the router.

## Tune after first run

- Tighten `GAP_MM` in `merge_both.py` if the halves sit too far apart (tighter = cheaper panel).
- Check the panel against JLC's rules (min rail width, mouse-bite spacing); bump tab count if any
  edge feels under-supported for the 5 Ah / LCD weight during assembly.
- Verify RESW1 (and any consigned/extended parts) in JLC's BOM/assembly preview before ordering.
