# LightFury panelization (KiKit)

Run on **your machine** (KiKit drives KiCad's `pcbnew` — it won't run in the sandbox). Route
first, panelize after; the frame wraps the final outline.

> ⚠ **Re-merge `both` first.** `lightfury_both.kicad_pcb` is assembled from the two halves and is
> currently **stale** — it predates the decoupling caps (C3/C4/C5) and the PWR_FLAGs added to the
> per-half boards. Propagate those into `both` (re-merge) and regenerate BOM/CPL **before** running
> the panelizer, or the panel ships without the new parts.

## Command

```bash
cd LightFury
kikit panelize -p panel/lightfury.kikit.json lightfury_both.kicad_pcb panel/lightfury_panel.kicad_pcb
```

`lightfury_both.kicad_pcb` already holds **both** routed halves (two Edge.Cuts loops), so the
preset uses a 1×1 grid — it frames the existing pair rather than tiling copies. KiKit detects both
board loops and bridges them to the rails with tabs + mouse-bites.

## What the preset does (JLC-oriented)

- **Rails** top & bottom, 5 mm, 3 mm gap to the boards (`railstb`).
- **Tabs** every 25 mm, 3 mm wide, cut as **mouse-bites** (0.5 mm drills @ 0.8 mm) — better than
  V-cuts here because the outlines are filleted/curved.
- **Tooling holes** (1.5 mm) and **fiducials** (1 mm copper / 2 mm mask) in the rail corners.
- `JLCJLCJLCJLC` order-number token in the rail text, `millradius 1 mm` for the router.

## Tune after first run

- If the two halves sit too far apart in `lightfury_both.kicad_pcb`, move one half closer in KiCad
  before panelizing — tighter nesting = smaller panel = cheaper.
- Check the generated panel against JLC's panel rules (min rail width, mouse-bite spacing) and
  bump tab count if any board edge feels under-supported for the 5 Ah / LCD weight during assembly.
- Regenerate the BOM/CPL **from the panel file** if JLC wants per-panel placement; designators are
  already `_2`-suffixed for the second half.
