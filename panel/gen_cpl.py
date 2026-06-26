#!/usr/bin/env python3
"""
gen_cpl.py - generate the JLCPCB CPL (positions) + BOM directly from the panel board.

Replaces the Fabrication-Toolkit-then-patch chain. Reads lightfury_panel.kicad_pcb,
takes each placed part's FOOTPRINT ORIGIN (= the body center the designer placed it on,
which is exactly JLC's placement datum) in the gerbers' own top-left origin frame, applies a
clean per-LCSC rotation correction, injects RESW1, and writes positions.csv + bom.csv fresh.

Idempotent: always reads the board fresh, never edits prior output. No pcbnew needed.

    python gen_cpl.py <panel.kicad_pcb> <out_dir>

WHY ORIGIN, NOT PAD CENTROID: verified against the board's F.Fab body outlines - for every
part the footprint origin sits at the body center, while the pad centroid is skewed on any part
with asymmetric pads (Molex -1.8mm, encoder +2.4mm, all 54 PG1316S +0.9mm, BAV70 +0.4mm).
JLC places the part so ITS library origin (body center) lands on our point, so origin is correct.
The prior "centroid correction" was the position bug - it moved good parts off their pads.

Coordinate frame (verified against the prior shipped CPL's global offset):
    Ox, Oy = panel Edge.Cuts top-left (matches KiKit `post.origin: tl` used for the gerbers)
    CPL_X  = origin_x - Ox
    CPL_Y  = Oy - origin_y            (CPL Y axis is up; board Y is down)
    CPL_R  = footprint_orientation + ROT_CORR[lcsc]   (mod 360)
"""
import sys, os, csv, re
from collections import OrderedDict, Counter
from kicad_panel import load_panel

# per-LCSC rotation correction (deg, CCW+). Only oriented parts whose pin-1 datum differs from
# JLC's library need a nonzero value. CONFIRM each once in JLC's preview (read the exact delta,
# do not nudge). Prior values measured while the 0.9deg tilt bug was live are noted but NOT
# trusted - re-confirm on the integer-tilt board.
ROT_CORR = {
    "C965555":  180.0,   # WS2812B-2020 LED   - confirmed
    "C68978":   270.0,   # BAV70 SOT-23       - confirmed JLC pass 1
    "C79174":    90.0,   # reset switch       - confirmed JLC pass 1
    "C2911519":  90.0,   # power switch       - confirmed JLC pass 1
    "C202421":  270.0,   # CKW12 encoder      - confirmed JLC pass 2
    "C262417":   90.0,   # RESW (encoder switch, on top of the +180 switch offset) - confirmed pass 2
    # still to confirm: "C293349" Molex, "C2440228" U2 SOT23-5, "C6881375" U1 SOT23-6
}

# optional per-LCSC position datum override, in part-LOCAL mm (applied before rotation).
# Use only if the JLC preview shows a part's body off its pads. Empty = footprint origin.
POS_OVERRIDE = {
    # part-LOCAL mm (pre-rotation). Applies to BOTH halves automatically.
    # NOTE: specify these by giving me a board-frame move in mm; clicks proved unreliable.
    "C2911519": (-0.295, +0.142),    # PWR1  - +0.1E (mm pass)
    "C293349":  (-0.268, -0.661),    # CONN1 - fine: +0.02W (mm pass)
    "C202421":  (-5.587, -0.761),    # RE1   - fine: +0.2E +0.05N (mm pass)
}

# RESW: the CKW12 click switch shares the encoder footprint, so it must be injected.
RESW_LCSC = "C262417"
RESW_VALUE = "CKW12 Switch"
RESW_FOOTPRINT = "CKW12"
RESW_ROT_OFFSET = 180.0          # switch vs encoder
RESW_OFFSET_LOCAL = (13.966, 0.976)   # encoder-local mm; net 20S then 6N = 14mm south (board).
                                       # S1/S2 midpoint is the natural anchor; this shifts off it.

# never place these (no JLC part / DNP / mechanical), even if they carry a stray field.
EXCLUDE_LIB = ("mcu_nice_nano", "mounting_hole", "Fiducial", "LCD_1.69",
               "battery_connector", "NPTH")


def _prefix(ref):
    m = re.match(r"[A-Za-z]+", ref)
    return m.group(0) if m else ""


def excluded(fp):
    return any(k in fp.lib for k in EXCLUDE_LIB)


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: gen_cpl.py <panel.kicad_pcb> <out_dir>")
    board, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    panel = load_panel(board)
    Ox, Oy = panel.edge_bbox[0], panel.edge_bbox[1]
    print("panel: %d footprints; gerber tl-origin = (%.3f, %.3f)"
          % (len(panel.footprints), Ox, Oy))

    placed, skipped = [], []
    for fp in panel.footprints:
        (skipped if (not fp.lcsc or excluded(fp)) else placed).append(fp)

    def cpl_xy(x, y):
        return round(x - Ox, 4), round(Oy - y, 4)

    cpl_rows = []
    encoders = []
    for fp in placed:
        ov = POS_OVERRIDE.get(fp.lcsc)
        if ov:
            px, py = fp._rot_local(ov[0], ov[1])
        else:
            px, py = fp.x, fp.y          # footprint origin = body center = JLC datum
        X, Y = cpl_xy(px, py)
        R = round((fp.rot + ROT_CORR.get(fp.lcsc, 0.0)) % 360, 2)
        side = "bottom" if fp.layer == "B.Cu" else "top"
        cpl_rows.append([fp.ref, X, Y, R, side])
        if "CKW12" in fp.value or fp.lib.endswith("CKW12"):
            encoders.append(fp)

    resw_refs = []
    for fp in encoders:
        s1, s2 = fp.pad_by_name("S1"), fp.pad_by_name("S2")
        if not (s1 and s2):
            print("  ! %s: no S1/S2 pads; cannot place its RESW" % fp.ref)
            continue
        mx0, my0 = (s1.gx + s2.gx) / 2.0, (s1.gy + s2.gy) / 2.0
        rx, ry = fp._rot_local(*RESW_OFFSET_LOCAL)   # rotate offset by encoder orientation
        mx = mx0 + (rx - fp.x)
        my = my0 + (ry - fp.y)
        X, Y = cpl_xy(mx, my)
        R = round((fp.rot + RESW_ROT_OFFSET + ROT_CORR.get(RESW_LCSC, 0.0)) % 360, 2)
        ref = fp.ref.replace("RE", "RESW", 1)
        side = "bottom" if fp.layer == "B.Cu" else "top"
        cpl_rows.append([ref, X, Y, R, side])
        resw_refs.append(ref)
        print("  + %s -> %s @ (%s,%s) rot %s" % (fp.ref, ref, X, Y, R))

    cpl_rows.sort(key=lambda r: (_prefix(r[0]), r[0]))
    cpl_path = os.path.join(out, "positions.csv")
    with open(cpl_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Rotation", "Layer"])
        w.writerows(cpl_rows)
    print("  -> %s  (%d parts)" % (cpl_path, len(cpl_rows)))

    groups = OrderedDict()
    for fp in placed:
        g = groups.setdefault(fp.lcsc, {"refs": [], "fp": fp.lib, "val": fp.value})
        g["refs"].append(fp.ref)
    if resw_refs:
        groups[RESW_LCSC] = {"refs": resw_refs, "fp": RESW_FOOTPRINT, "val": RESW_VALUE}

    bom_path = os.path.join(out, "bom.csv")
    with open(bom_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Footprint", "Quantity", "Value", "LCSC Part #"])
        for lcsc, g in groups.items():
            refs = sorted(g["refs"], key=lambda r: (_prefix(r), r))
            w.writerow([", ".join(refs), g["fp"], len(refs), g["val"], lcsc])
    print("  -> %s  (%d unique parts)" % (bom_path, len(groups)))

    sk = Counter(fp.lib.split(":")[-1] for fp in skipped)
    print("  skipped (no LCSC / mechanical / DNP): "
          + ", ".join("%sx%d" % (k, v) for k, v in sk.items()))


if __name__ == "__main__":
    main()
