#!/usr/bin/env python3
"""
Fold the CKW12 tactile switch (RESW1 / C262417) into the JLC BOM + CPL.

The CKW12 is two parts on one footprint: the ALPS encoder (RE1, C202421) and a separate
tactile click switch (C262417). KiCad's BOM is one-part-per-footprint, so `kikit fab` only
emits the encoder. This script adds the switch automatically by reading the switch pads
(S1/S2) straight out of the panel, so the placement always matches the real board and you
never hand-patch it again.

Run AFTER `kikit fab jlcpcb`:
    python panel/inject_resw1.py panel/lightfury_panel.kicad_pcb panel/jlc

Args:
    1) the panelized board (.kicad_pcb)
    2) the kikit fab output dir (containing the bom + pos CSVs)

Assumes encoder footprints have Value containing "CKW12" and pads named S1/S2 are the
switch. Maps RE1->RESW1, RE1_2->RESW1_2. LCSC for the switch:
"""
import sys, os, csv, math, glob
import pcbnew

SWITCH_LCSC = "C262417"
SWITCH_COMMENT = "CKW12 Switch"
SWITCH_FOOTPRINT = "CKW12"

def find_switches(board_path):
    board = pcbnew.LoadBoard(board_path)
    out = []
    for fp in board.GetFootprints():
        if "CKW12" not in fp.GetValue():
            continue
        ref = fp.GetReference()                       # RE1, RE1_2
        pads = {p.GetName(): p for p in fp.Pads()}
        if "S1" not in pads or "S2" not in pads:
            print(f"  ! {ref}: no S1/S2 pads, skipping"); continue
        p1, p2 = pads["S1"].GetPosition(), pads["S2"].GetPosition()
        midx = pcbnew.ToMM((p1.x + p2.x) / 2.0)
        midy = pcbnew.ToMM((p1.y + p2.y) / 2.0)
        # rotation along the S1->S2 axis (KiCad y is +down; JLC wants CCW from +x).
        rot = (-math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))) % 360
        sw_ref = ref.replace("RE", "RESW", 1)         # RE1->RESW1, RE1_2->RESW1_2
        out.append((sw_ref, round(midx, 4), round(midy, 4), round(rot, 2)))
        print(f"  {ref} -> {sw_ref} @ ({midx:.3f}, {midy:.3f}) rot {rot:.1f}")
    return out

def find_csv(d, *keys):
    for f in glob.glob(os.path.join(d, "*.csv")):
        if any(k in os.path.basename(f).lower() for k in keys):
            return f
    return None

def col(header, *names):
    for i, h in enumerate(header):
        hl = h.lower()
        if any(n in hl for n in names):
            return i
    return None

def patch_cpl(path, switches):
    rows = list(csv.reader(open(path, newline="")))
    header = rows[0]
    ci = {k: col(header, *v) for k, v in {
        "des": ["designator", "ref"], "x": ["mid x", "midx", "pos x"],
        "y": ["mid y", "midy", "pos y"], "rot": ["rotation", "rotate"],
        "layer": ["layer", "side"]}.items()}
    for ref, x, y, rot in switches:
        row = [""] * len(header)
        row[ci["des"]] = ref; row[ci["x"]] = x; row[ci["y"]] = y
        row[ci["rot"]] = rot; row[ci["layer"]] = "top"
        rows.append(row)
    csv.writer(open(path, "w", newline="")).writerows(rows)
    print(f"  + {len(switches)} rows -> {os.path.basename(path)}")

def patch_bom(path, switches):
    rows = list(csv.reader(open(path, newline="")))
    header = rows[0]
    di = col(header, "designator", "ref")
    li = col(header, "lcsc", "jlcpcb part", "supplier")
    ci = col(header, "comment", "designation", "value")
    fi = col(header, "footprint", "package")
    row = [""] * len(header)
    refs = ",".join(s[0] for s in switches)
    if di is not None: row[di] = refs
    if li is not None: row[li] = SWITCH_LCSC
    if ci is not None: row[ci] = SWITCH_COMMENT
    if fi is not None: row[fi] = SWITCH_FOOTPRINT
    rows.append(row)
    csv.writer(open(path, "w", newline="")).writerows(rows)
    print(f"  + RESW switch line ({refs}, {SWITCH_LCSC}) -> {os.path.basename(path)}")

def main():
    if len(sys.argv) != 3:
        sys.exit("usage: inject_resw1.py <panel.kicad_pcb> <fab_output_dir>")
    board_path, fab_dir = sys.argv[1], sys.argv[2]
    print("Reading switch positions from panel:")
    switches = find_switches(board_path)
    if not switches:
        sys.exit("No CKW12 encoders found — nothing to inject.")
    cpl = find_csv(fab_dir, "pos", "cpl")
    bom = find_csv(fab_dir, "bom")
    if not cpl or not bom:
        sys.exit(f"Could not find bom/pos CSVs in {fab_dir} (found pos={cpl} bom={bom})")
    print("Patching CPL:");  patch_cpl(cpl, switches)
    print("Patching BOM:");  patch_bom(bom, switches)
    print("Done. Verify RESW1 placement/rotation in JLC's preview before ordering.")

if __name__ == "__main__":
    main()
