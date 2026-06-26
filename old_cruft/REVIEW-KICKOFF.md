# LightFury — review & optimize: session kickoff

Goal: review the **already-routed** LightFury board (its README literally asks "let me know if you see
anything wrong"), fix only genuine functional problems, and panel it for JLCPCB. **Preserve the
routing** — regenerate from ergogen only if a real defect forces it (it wipes routing).

## Context
- 54-key ergo split — the "Swiss Army chainsaw" to xiphos's scalpel. Features: 1.69" Waveshare color
  **LCD**, **per-key WS2812B-2020 RGB** (~54/half — heat-sensitive, fine-pitch → this is exactly why
  it must be JLC PCBA, not hot-plate), **CKW12 roller encoder** integrated into the PCB, PG1316S
  switches, an absurd **5Ah battery**, nice!nano.
- Has schematics (`lightfury_left.kicad_sch` / `_right`) built via the `Schematics_and_Ergogen.md`
  workflow (the guide is present in this repo), routed `lightfury_left/right/both.kicad_pcb`, and a
  `Production_JLCPCBA/` folder.
- The workspace `../CLAUDE.md` "Schematics, combined boards & production" section applies.
- **No `CLAUDE.md` yet** — create one (model on `../zmk-config-totem/CLAUDE.md`).

## First steps
1. Read `config.yaml`, the routed PCBs, schematics, and `Production_JLCPCBA/` BOM/CPL. Write
   `LightFury/CLAUDE.md`.
2. **Design review** (what the README invites): verify the **WS2812 data chain** (DIN→DOUT order
   continuous and sane), LED/LCD/encoder power + signal nets, decoupling, and schematic ↔ PCB parity.
   Flag issues — but remember fixes needing a config regen cost the routing.
3. **BOM completeness:** every part needs an LCSC number (LCD module, WS2812B-2020, CKW12 encoder,
   EZmate, power/reset switches, PG1316S consigned `C9900170245`); nano DNP / hand-soldered. Sort out
   what's JLC-stockable vs consigned vs hand-placed.
4. **Panelize with KiKit** (multiboard — this board is large, so nesting matters more for cost): rails,
   mouse-bites, fiducials, tooling. Claude writes the config; Hunter runs it.

git: hands-off — write the commands, don't run them.
