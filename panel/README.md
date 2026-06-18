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

# 3. Generate JLC fab files from the panel. DON'T use `kikit fab jlcpcb --assembly` — it
#    requires a schematic, and the panel's _2-suffixed refs won't match a single half
#    schematic (and it skips JLC rotation corrections). Instead, open the panel in pcbnew
#    and run the **Fabrication Toolkit** plugin (the one that made the original
#    Production_JLCPCBA files). It reads the LCSC footprint fields + applies JLC rotation
#    corrections, straight from the board. Outputs gerbers + BOM + CPL into panel/production/.

# 4. Fold in the CKW12 click switch (RESW1 / C262417) — not a footprint of its own, so it's
#    injected into the toolkit's BOM + CPL from the encoder's switch pads.
python panel/inject_resw1.py panel/lightfury_panel.kicad_pcb panel/production
```

## Notes / gotchas

- **`merge_both.py`** is the script that replaces your old hand-merge. Right-half refs become
  `*_2` (uniform — simpler than the old mixed RS/RLED/_2 scheme; JLC only cares that refs are
  unique and that BOM ↔ CPL agree, which they will since both come from this pipeline).
  `appendBoard`'s signature is the line most likely to need a tweak for your KiKit version.
- **Prereq:** the per-half schematics need their `LCSC` fields filled and pushed to the PCBs
  (Update PCB from Schematic / F8) *before* step 1, or the BOM comes out without part numbers.
- **`inject_resw1.py`** reads S1/S2 pad positions from the panel, so RESW1 placement always
  matches the real board. The **rotation** is derived from the pad axis — eyeball it in JLC's
  assembly preview and tweak if the switch looks turned the wrong way.
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
