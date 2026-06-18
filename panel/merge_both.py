#!/usr/bin/env python3
"""
Merge the two routed LightFury halves into one combined board, lightfury_both.kicad_pcb.

Why a script: the two per-half boards use IDENTICAL reference designators (both have
C1-C5, S1-S27, U1-U2, LED1-LED27, ...). A plain copy/paste or File>Append Board would
produce duplicate refs, which JLC's BOM/CPL can't use. KiKit's appendBoard lets us rename
on the way in: right-half refs get a "_2" suffix and nets get L_/R_ prefixes so the two
halves stay electrically distinct in the combined file.

Run on YOUR machine (needs KiCad's pcbnew + KiKit):
    python panel/merge_both.py
Then panelize the result with the existing CLI preset (see panel/README.md).

NOTE: appendBoard's signature is the part most likely to vary by KiKit version. If it
errors, that's the line to check first.
"""
import os
from pcbnew import VECTOR2I, FromMM
from kikit.panelize import Panel
from kikit.defs import Origin

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # LightFury/
LEFT  = os.path.join(ROOT, "lightfury_left.kicad_pcb")
RIGHT = os.path.join(ROOT, "lightfury_right.kicad_pcb")
OUT   = os.path.join(ROOT, "lightfury_both.kicad_pcb")

# Each half's outline is ~156 mm wide. Place the right half this far to the right of the
# left so there's a small gap (tune if you want them tighter for a cheaper panel).
GAP_MM = 165

panel = Panel(OUT)

# Left half: nets -> L_<name>, refs unchanged.
panel.appendBoard(
    LEFT,
    VECTOR2I(0, 0),
    origin=Origin.TopLeft,
    netRenamer=lambda seq, name: f"L_{name}",
    refRenamer=lambda seq, ref: ref,
    inheritDrc=False,
)

# Right half: nets -> R_<name>, refs -> <ref>_2  (C1->C1_2, S1->S1_2, RE1->RE1_2, ...).
panel.appendBoard(
    RIGHT,
    VECTOR2I(FromMM(GAP_MM), 0),
    origin=Origin.TopLeft,
    netRenamer=lambda seq, name: f"R_{name}",
    refRenamer=lambda seq, ref: f"{ref}_2",
    inheritDrc=False,
)

panel.save()
print(f"Wrote {OUT}")
print("Next: kikit panelize -p panel/lightfury.kikit.json "
      "lightfury_both.kicad_pcb panel/lightfury_panel.kicad_pcb")
