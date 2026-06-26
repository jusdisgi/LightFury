# LightFury — JLCPCB order set

**These three files are what you upload to JLCPCB. Nothing else.**

| file | what it is | upload as |
|---|---|---|
| `lightfury_panel.zip` | Gerbers + drill for the full panel (both halves, frame, mouse-bites) | Gerber |
| `bom.csv` | Bill of materials (one line per LCSC part, RESW1 included) | BOM |
| `positions.csv` | Pick-and-place / CPL (origin datum, integer rotations, per-part offsets applied) | CPL |

The gerber is uploaded once at the **start** of the JLC order (before PCBA). The BOM/CPL are
uploaded in the PCBA step and can be re-uploaded freely. **You only need a fresh gerber when the
copper changes** (re-panelize or a half edit) — pure rotation/position tweaks ride on the CPL alone.

## Regenerating these

Full procedure and the hard rules live in [`../panel/CPL_WORKFLOW.md`](../panel/CPL_WORKFLOW.md).
Short version, run from the repo root, all from the **same** panel generation:

```bat
:: gerbers: open panel\lightfury_panel.kicad_pcb in KiCad, run the Fabrication Toolkit,
:: then copy its output zip up here:
copy panel\production\lightfury_panel.zip production-panel\

:: BOM + CPL straight from the same panel file:
python panel\gen_cpl.py panel\lightfury_panel.kicad_pcb production-panel

:: optional local sanity render (writes PNGs to panel\verify\):
python panel\render_cpl.py panel\lightfury_panel.kicad_pcb production-panel\positions.csv panel\verify
```

Gerbers and CPL **must** come from the same panel generation or parts land on stale copper — that
was the multi-hour failure of 18 Jun (a frozen gerber under a changing CPL).

## Part-specific notes baked into `gen_cpl.py`

- Rotations and position offsets for the oddball parts (PWR1, CONN1, RE1, RESW1, the SOT-23s,
  LEDs, diodes, switches) are in the `ROT_CORR` / `POS_OVERRIDE` tables at the top of `gen_cpl.py`.
- **PG1316S** switches are consigned (`C9900170245`); the **nice!nano**, **Waveshare LCD**, JST
  battery connector and M2 mounting holes are hand-assembled — none appear in this BOM/CPL by design.
