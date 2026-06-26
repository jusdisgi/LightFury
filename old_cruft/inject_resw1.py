#!/usr/bin/env python3
"""
Post-process the Fabrication Toolkit's JLC fab files for the LightFury panel.

Run AFTER a fresh Fabrication Toolkit export (rotation/position mods below are NOT idempotent,
so always re-export first, then run this ONCE):
    python panel/inject_resw1.py panel/lightfury_panel.kicad_pcb panel/production

What it does:
  CPL
    1. Strip non-component rows (KiKit fiducials/tooling, LCD module mount, mounting holes).
    2. POSITION: shift every part's placement point from the footprint ORIGIN (what the toolkit
       writes) to the part's true PAD CENTROID. The toolkit writes the origin; JLC places the part
       there and rotates it ABOUT that point, so when origin != centroid the body swings off the
       pads as soon as it's rotated (classic on the SOT-23 BAV70, the connector, the encoder).
       No-op for symmetric parts (LEDs, R, C) whose origin already is the centroid.
    3. ROTATION: add a per-part-type correction (deg) for footprints whose pin-1 datum doesn't
       match JLC's library part. Confirmed from JLC's assembly preview:
         LED (WS2812B-2020, C965555) -> 180     D (BAV70 SOT-23) -> 270
       Applied on top of the raw rotation; because we now place at the centroid, this no longer
       drags the part off its pads. Add new entries to ROT_FIX as the preview turns up more.
    4. Add RESW1 (the CKW12 click switch, C262417 — shares the encoder footprint so the toolkit
       can't emit it) at the encoder's S1/S2 midpoint, rotation = encoder + 180.
  BOM
    Merge rows that share an LCSC into one line, drop rows with no LCSC (LCD / mounting holes),
    add the RESW line.
"""
import sys, os, csv, glob, re
from collections import OrderedDict
import pcbnew

SWITCH_LCSC = "C262417"
SWITCH_COMMENT = "CKW12 Switch"
SWITCH_FOOTPRINT = "CKW12"
SWITCH_ROT_OFFSET = 180.0   # switch vs encoder, per the footprint

# Per-part-type CPL rotation correction (deg), keyed by alpha designator prefix. These are JLC
# library pin-1 mismatches, confirmed in JLC's assembly preview. Flip a sign / tweak a value here
# if the preview still shows a part turned wrong; nothing else needs to change.
ROT_FIX = {"LED": 180.0, "D": 270.0}

def _prefix(des):
    m = re.match(r"[A-Za-z]+", des)
    return m.group(0) if m else ""

def col(header, *names):
    for i, h in enumerate(header):
        if any(n in h.lower() for n in names):
            return i
    return None

def find_csv(d, *keys):
    for f in glob.glob(os.path.join(d, "*.csv")):
        if any(k in os.path.basename(f).lower() for k in keys):
            return f
    return None

def geometry(board_path):
    """Read the panel once (pcbnew gives absolute, already-rotated pad positions). Returns:
       centroid[ref]   = (dx_mm, dy_mm)            pad-centroid minus footprint origin (board frame)
       switch[enc_ref] = (sdx_mm, sdy_mm, sw_ref)  S1/S2 midpoint minus origin, for placing RESW"""
    board = pcbnew.LoadBoard(board_path)
    centroid = {}; switch = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        o = fp.GetPosition()
        pads = list(fp.Pads())
        if pads:
            cx = sum(p.GetPosition().x for p in pads) / len(pads)
            cy = sum(p.GetPosition().y for p in pads) / len(pads)
            centroid[ref] = (pcbnew.ToMM(cx - o.x), pcbnew.ToMM(cy - o.y))
        if "CKW12" in fp.GetValue():
            pd = {p.GetName(): p for p in pads}
            if "S1" in pd and "S2" in pd:
                mx = (pd["S1"].GetPosition().x + pd["S2"].GetPosition().x) / 2.0
                my = (pd["S1"].GetPosition().y + pd["S2"].GetPosition().y) / 2.0
                switch[ref] = (pcbnew.ToMM(mx - o.x), pcbnew.ToMM(my - o.y), ref.replace("RE", "RESW", 1))
            else:
                print(f"  ! {ref}: no S1/S2 pads, can't place its switch")
    return centroid, switch

def patch_cpl(path, centroid, switch):
    rows = list(csv.reader(open(path, newline="")))
    header = rows[0]
    di = col(header, "designator", "ref"); xi = col(header, "mid x", "midx", "pos x")
    yi = col(header, "mid y", "midy", "pos y"); ri = col(header, "rotation", "rotate")
    li = col(header, "layer", "side")
    def des(r): return r[di] if di is not None and len(r) > di else ""
    def feature(d): return bool(re.match(r"(KIKIT_|LCD\d|MH\d|RESW)", d))
    body = [r for r in rows[1:] if not feature(des(r))]
    dropped = (len(rows) - 1) - len(body)

    # Build RESW rows from the ORIGINAL (pre-shift) encoder rows: the switch midpoint IS its own
    # centroid, so anchoring to the encoder's raw origin + the S1/S2 offset lands it correctly.
    encmap = {des(r): r for r in body if des(r) in switch}
    sw_rows = []
    for enc_ref, (sdx, sdy, sw_ref) in switch.items():
        er = encmap.get(enc_ref)
        if er is None:
            print(f"  ! encoder {enc_ref} not in CPL; can't place {sw_ref}"); continue
        ex, ey, erot = float(er[xi]), float(er[yi]), float(er[ri])
        row = [""] * len(header)
        row[di] = sw_ref; row[xi] = round(ex + sdx, 4); row[yi] = round(ey - sdy, 4)
        row[ri] = round((erot + SWITCH_ROT_OFFSET) % 360, 2)
        row[li] = er[li] if li is not None else "top"
        sw_rows.append(row); print(f"  {enc_ref} -> {sw_ref} @ ({row[xi]},{row[yi]}) rot {row[ri]}")

    # Apply rotation correction + centroid position shift to the real rows.
    nrot = npos = 0
    for r in body:
        d = des(r)
        rf = ROT_FIX.get(_prefix(d))
        if rf and ri is not None and len(r) > ri:
            r[ri] = round((float(r[ri]) + rf) % 360, 2); nrot += 1
        c = centroid.get(d)
        if c and xi is not None and yi is not None and len(r) > max(xi, yi):
            cdx, cdy = c
            if abs(cdx) > 1e-4 or abs(cdy) > 1e-4:
                r[xi] = round(float(r[xi]) + cdx, 4)
                r[yi] = round(float(r[yi]) - cdy, 4)   # CPL Y is flipped vs board Y
                npos += 1

    csv.writer(open(path, "w", newline="")).writerows([header] + body + sw_rows)
    print(f"  - dropped {dropped} fiducial/tooling/LCD/MH/old-RESW rows")
    print(f"  ~ rotation-corrected {nrot} parts ({ROT_FIX}); centroid-shifted {npos} parts")
    print(f"  + {len(sw_rows)} RESW rows -> {os.path.basename(path)}")

def patch_bom(path, switch):
    rows = list(csv.reader(open(path, newline="")))
    header = rows[0]
    di = col(header, "designator", "ref"); li = col(header, "lcsc", "jlcpcb part", "supplier")
    ci = col(header, "comment", "designation", "value"); fi = col(header, "footprint", "package")
    data = [r for r in rows[1:]
            if li is not None and len(r) > li and r[li].strip() and r[li] != SWITCH_LCSC]
    dropped = (len(rows) - 1) - len(data)
    groups = OrderedDict()
    for r in data:
        k = r[li]
        if k in groups:
            groups[k][di] = groups[k][di] + "," + r[di]
        else:
            groups[k] = r[:]
    merged = len(data) - len(groups)
    sw = [""] * len(header); refs = ",".join(s for _, _, s in switch.values())
    if di is not None: sw[di] = refs
    if li is not None: sw[li] = SWITCH_LCSC
    if ci is not None: sw[ci] = SWITCH_COMMENT
    if fi is not None: sw[fi] = SWITCH_FOOTPRINT
    csv.writer(open(path, "w", newline="")).writerows([header] + list(groups.values()) + [sw])
    print(f"  - dropped {dropped} no-LCSC rows (LCD/MH); merged {merged} same-LCSC rows")
    print(f"  + RESW line ({refs}, {SWITCH_LCSC}) -> {os.path.basename(path)}")

def main():
    if len(sys.argv) != 3:
        sys.exit("usage: inject_resw1.py <panel.kicad_pcb> <fab_output_dir>")
    board_path, fab_dir = sys.argv[1], sys.argv[2]
    centroid, switch = geometry(board_path)
    if not switch:
        sys.exit("No CKW12 encoders found — nothing to inject.")
    cpl = find_csv(fab_dir, "pos", "cpl"); bom = find_csv(fab_dir, "bom")
    if not cpl or not bom:
        sys.exit(f"Could not find bom/pos CSVs in {fab_dir} (pos={cpl} bom={bom})")
    print("CPL:"); patch_cpl(cpl, centroid, switch)
    print("BOM:"); patch_bom(bom, switch)
    print("Done. Centroid positions + per-part rotation corrections + RESW.")

if __name__ == "__main__":
    main()
