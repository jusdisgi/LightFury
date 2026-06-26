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
from pcbnew import VECTOR2I, FromMM, EDA_ANGLE, DEGREES_T
from kikit.panelize import Panel, Origin

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # LightFury/
LEFT  = os.path.join(ROOT, "lightfury_left.kicad_pcb")
RIGHT = os.path.join(ROOT, "lightfury_right.kicad_pcb")
OUT   = os.path.join(ROOT, "lightfury_both.kicad_pcb")

# Stack the halves VERTICALLY using CENTER-anchored placement. Center anchoring is
# rotation-invariant, so flipping the bottom half 180 deg behaves predictably (TopLeft does
# not — the corner moves when you rotate). Each outline is ~156 x ~116.4 mm.
# PITCH_MM = vertical center-to-center spacing; gap between facing edges = PITCH - 116.4.
BOARD_W = 156.1
BOARD_H = 116.4
PITCH_MM = 94.0          # vertical center-to-center; tune for the gap you want
CX = BOARD_W / 2.0
# Rotate each half by TILT so the flat bottoms sit (near) level. The per-half parts are all at
# WHOLE-degree orientations, so TILT must be an INTEGER — otherwise every part lands on a
# fractional angle (e.g. 280.9 deg) that JLC's preview rounds, which reads as a ~1 deg error on
# the whole board. The bottom edge measured -10.9 deg, so 11 levels it to within 0.1 deg while
# keeping every part on a whole degree. (Flip TILT's sign if a half tilts the wrong way.)
TILT = 11

panel = Panel(OUT)

# Top half: centered, no rotation. nets -> L_<name>, refs unchanged.
panel.appendBoard(
    LEFT,
    VECTOR2I(FromMM(CX), FromMM(BOARD_H / 2.0)),
    origin=Origin.Center,
    rotationAngle=EDA_ANGLE(TILT, DEGREES_T),
    netRenamer=lambda seq, name: f"L_{name}",
    refRenamer=lambda seq, ref: ref,
    inheritDrc=False,
)

# Bottom half: centered below, rotated 180 deg about its own center so the straight bottom
# edges face each other. nets -> R_<name>, refs -> <ref>_2 (C1->C1_2, S1->S1_2, RE1->RE1_2).
panel.appendBoard(
    RIGHT,
    VECTOR2I(FromMM(CX), FromMM(BOARD_H / 2.0 + PITCH_MM)),
    origin=Origin.Center,
    rotationAngle=EDA_ANGLE(180 - TILT, DEGREES_T),
    netRenamer=lambda seq, name: f"R_{name}",
    refRenamer=lambda seq, ref: f"{ref}_2",
    inheritDrc=False,
)

panel.save()
print(f"Wrote {OUT}")
print("Next: kikit panelize -p panel/lightfury.kikit.json "
      "lightfury_both.kicad_pcb panel/lightfury_panel.kicad_pcb")
