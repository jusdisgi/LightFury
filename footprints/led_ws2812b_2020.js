// NeoPixel LED WS2812B-2020 ergogen footprint
// Author: Hunter Cook @huntercook https://github.com/jusdisgi
// Canonical location: https://github.com/jusdisgi/ergogen-footprints/blob/main/led_ws2812b_2020.js
//
// created with kicad2ergogen: https://kicad2ergogen.genteure.com/
//
// Component datasheet: https://www.lcsc.com/datasheet/lcsc_datasheet_2412051755_Worldsemi-WS2812B-2020_C965555.pdf
//
// Nets/Parameters
//
// side: F (default) for Front, B for Back
// 
// P1: Data output. Default net undefined
// P2: Ground pin. Default net "GND"
// P3: Data input. Default net undefined
// P4: Power input. Default net "VCC"

module.exports = {
  params: {
    designator: 'LED',
    side: 'F',
    P1: { type: 'net', value: undefined },
    P2: { type: 'net', value: 'GND' },
    P3: { type: 'net', value: undefined },
    P4: { type: 'net', value: 'VCC' },    
    p1_via: false,
    p1_via_size: 0.5, //Max fitting inside pad is 0.5mm, JLCPCB no-extra-charge minimum 0.4mm. 
    p1_via_hole: 0.3, //JLCPCB no-extra-charge minimum 0.3mm
    p2_via: false,
    p2_via_size: 0.5,
    p2_via_hole: 0.3,
    p3_via: false,
    p3_via_size: 0.5,
    p3_via_hole: 0.3,
    p4_via: false,
    p4_via_size: 0.5,
    p4_via_hole: 0.3,
  },
  body: p => {
    const fp = [];
    const flip = p.side === "B";
if (!flip && p.side !== "F") throw new Error('unsupported side: ' + p.side);

fp.push(`(footprint "LED_WS2812B-2020_PLCC4_2.0x2.0mm"`);
fp.push(p.at);
fp.push(`(layer "${(flip ? "B.Cu" : "F.Cu")}")`);
fp.push(`(property "Reference" "${p.ref}" ${p.ref_hide} (at 0 0 ${p.r}) (layer "${p.side}.SilkS") (effects (font (size 1 1) (thickness 0.15))${ p.side === "B" ? " (justify mirror)" : ""}))`);

fp.push(`(descr "2.0mm x 2.0mm Addressable RGB LED NeoPixel Nano, 12 mA, https://cdn-shop.adafruit.com/product-files/4684/4684_WS2812B-2020_V1.3_EN.pdf")`);
fp.push(`(tags "LED RGB NeoPixel Nano PLCC-4 2020")`);
fp.push(`(attr smd)`);

// Unknown to kicad2ergogen
fp.push(`(embedded_fonts no)`);

// Pads
fp.push(`(pad "1" smd rect (at ${(flip ? 0.915 : -0.915)} -0.55 ${p.r}) (size 0.7 0.7) (layers "${(flip ? "B" : "F")}.Cu" "${(flip ? "B" : "F")}.Mask" "${(flip ? "B" : "F")}.Paste")  ${p.P1})`);
fp.push(`(pad "2" smd rect (at ${(flip ? 0.915 : -0.915)} 0.55 ${p.r}) (size 0.7 0.7) (layers "${(flip ? "B" : "F")}.Cu" "${(flip ? "B" : "F")}.Mask" "${(flip ? "B" : "F")}.Paste")  ${p.P2})`);
fp.push(`(pad "3" smd rect (at ${(flip ? -0.915 : 0.915)} 0.55 ${p.r}) (size 0.7 0.7) (layers "${(flip ? "B" : "F")}.Cu" "${(flip ? "B" : "F")}.Mask" "${(flip ? "B" : "F")}.Paste")  ${p.P3})`);
fp.push(`(pad "4" smd rect (at ${(flip ? -0.915 : 0.915)} -0.55 ${p.r}) (size 0.7 0.7) (layers "${(flip ? "B" : "F")}.Cu" "${(flip ? "B" : "F")}.Mask" "${(flip ? "B" : "F")}.Paste")  ${p.P4})`);

// Pad Vias
if (p.p1_via) {
  fp.push(`(pad "1" thru_hole circle (at ${(flip ? 0.915 : -0.915)} -0.55 ${p.r}) (size ${p.p1_via_size} ${p.p1_via_size}) (layers "F.Cu" "B.Cu" "F.Paste" "B.Paste" "F.Mask" "B.Mask") (drill ${p.p1_via_hole}) (thermal_bridge_angle 45) ${p.P1})`);
}
if (p.p2_via) {
  fp.push(`(pad "2" thru_hole circle (at ${(flip ? 0.915 : -0.915)} 0.55 ${p.r}) (size ${p.p2_via_size} ${p.p2_via_size}) (layers "F.Cu" "B.Cu" "F.Paste" "B.Paste" "F.Mask" "B.Mask") (drill ${p.p2_via_hole}) (thermal_bridge_angle 45) ${p.P2})`);
}
if (p.p3_via) {
  fp.push(`(pad "3" thru_hole circle (at ${(flip ? -0.915 : 0.915)} 0.55 ${p.r}) (size ${p.p3_via_size} ${p.p3_via_size}) (layers "F.Cu" "B.Cu" "F.Paste" "B.Paste" "F.Mask" "B.Mask") (drill ${p.p3_via_hole}) (thermal_bridge_angle 45) ${p.P3})`);
}
if (p.p4_via) {
  fp.push(`(pad "4" thru_hole circle (at ${(flip ? -0.915 : 0.915)} -0.55 ${p.r}) (size ${p.p4_via_size} ${p.p4_via_size}) (layers "F.Cu" "B.Cu" "F.Paste" "B.Paste" "F.Mask" "B.Mask") (drill ${p.p4_via_hole}) (thermal_bridge_angle 45) ${p.P4})`);
}

// Drawings on F.CrtYd
fp.push(`(fp_line (start ${(flip ? 1.52 : -1.52)} -1.25) (end ${(flip ? 1.52 : -1.52)} 1.25) (stroke (width 0.05) (type solid)) (layer "${(flip ? "B.CrtYd" : "F.CrtYd")}") )`);
fp.push(`(fp_line (start ${(flip ? 1.52 : -1.52)} 1.25) (end ${(flip ? -1.52 : 1.52)} 1.25) (stroke (width 0.05) (type solid)) (layer "${(flip ? "B.CrtYd" : "F.CrtYd")}") )`);
fp.push(`(fp_line (start ${(flip ? -1.52 : 1.52)} -1.25) (end ${(flip ? 1.52 : -1.52)} -1.25) (stroke (width 0.05) (type solid)) (layer "${(flip ? "B.CrtYd" : "F.CrtYd")}") )`);
fp.push(`(fp_line (start ${(flip ? -1.52 : 1.52)} 1.25) (end ${(flip ? -1.52 : 1.52)} -1.25) (stroke (width 0.05) (type solid)) (layer "${(flip ? "B.CrtYd" : "F.CrtYd")}") )`);

// Drawings on F.Fab
fp.push(`(fp_line (start ${(flip ? 1.1 : -1.1)} -0.45) (end ${(flip ? 1.1 : -1.1)} 1) (stroke (width 0.1) (type solid)) (layer "${(flip ? "B.Fab" : "F.Fab")}") )`);
fp.push(`(fp_line (start ${(flip ? 1.1 : -1.1)} 1) (end ${(flip ? -1.1 : 1.1)} 1) (stroke (width 0.1) (type solid)) (layer "${(flip ? "B.Fab" : "F.Fab")}") )`);
fp.push(`(fp_line (start ${(flip ? 0.55 : -0.55)} -1) (end ${(flip ? 1.1 : -1.1)} -0.45) (stroke (width 0.1) (type solid)) (layer "${(flip ? "B.Fab" : "F.Fab")}") )`);
fp.push(`(fp_line (start ${(flip ? -1.1 : 1.1)} -1) (end ${(flip ? 0.55 : -0.55)} -1) (stroke (width 0.1) (type solid)) (layer "${(flip ? "B.Fab" : "F.Fab")}") )`);
fp.push(`(fp_line (start ${(flip ? -1.1 : 1.1)} -1) (end ${(flip ? -1.1 : 1.1)} 1) (stroke (width 0.1) (type solid)) (layer "${(flip ? "B.Fab" : "F.Fab")}") )`);
fp.push(`(fp_rect (start ${(flip ? 0.5 : -0.5)} -1) (end ${(flip ? 0.05 : -0.05)} -0.45) (stroke (width 0.1) (type solid)) (fill yes) (layer "${(flip ? "B.Fab" : "F.Fab")}") )`);
fp.push(`(fp_rect (start ${(flip ? 0.5 : -0.5)} 0.4) (end ${(flip ? 0.05 : -0.05)} 1) (stroke (width 0.1) (type solid)) (fill yes) (layer "${(flip ? "B.Fab" : "F.Fab")}") )`);
fp.push(`(fp_text user "\${REFERENCE}" (at 0 0 ${(p.r + 0) % 360}) (layer "${(flip ? "B.Fab" : "F.Fab")}")  (effects (font (size 0.5 0.5) (thickness 0.075)) (justify${ flip ? " mirror" : ""})))`);

// Drawings on F.SilkS
fp.push(`(fp_line (start ${(flip ? 1.6 : -1.6)} 1.15) (end ${(flip ? 1.6 : -1.6)} -0.85) (stroke (width 0.12) (type solid)) (layer "${(flip ? "B.SilkS" : "F.SilkS")}") )`);
fp.push(`(fp_line (start ${(flip ? 1.6 : -1.6)} 1.15) (end ${(flip ? -1.6 : 1.6)} 1.15) (stroke (width 0.12) (type solid)) (layer "${(flip ? "B.SilkS" : "F.SilkS")}") )`);
fp.push(`(fp_line (start ${(flip ? 1.3 : -1.3)} -1.15) (end ${(flip ? 1.6 : -1.6)} -0.85) (stroke (width 0.12) (type default)) (layer "${(flip ? "B.SilkS" : "F.SilkS")}") )`);
fp.push(`(fp_line (start ${(flip ? 1.3 : -1.3)} -1.15) (end ${(flip ? -1.6 : 1.6)} -1.15) (stroke (width 0.12) (type solid)) (layer "${(flip ? "B.SilkS" : "F.SilkS")}") )`);
fp.push(`(fp_line (start ${(flip ? -1.6 : 1.6)} -1.15) (end ${(flip ? -1.6 : 1.6)} 1.15) (stroke (width 0.12) (type solid)) (layer "${(flip ? "B.SilkS" : "F.SilkS")}") )`);

// 3D Models
fp.push(`(model "\${KICAD9_3DMODEL_DIR}/LED_SMD.3dshapes/LED_WS2812B-2020_PLCC4_2.0x2.0mm.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))`);

// Properties
// fp.push(`(property "Reference" "REF**" (at 0 -2 ${(p.r + 0) % 360}) (layer "${(flip ? "B.SilkS" : "F.SilkS")}")  (effects (font (size 1 1) (thickness 0.15)) (justify${ flip ? " mirror" : ""})))`);
// fp.push(`(property "Value" "LED_WS2812B-2020_PLCC4_2.0x2.0mm" (at 0 2.2 ${(p.r + 0) % 360}) (layer "${(flip ? "B.Fab" : "F.Fab")}")  (effects (font (size 1 1) (thickness 0.15)) (justify${ flip ? " mirror" : ""})))`);
// fp.push(`(property "Datasheet" "" (at 0 0 ${(p.r + 0) % 360}) (unlocked yes) (layer "${(flip ? "B.Fab" : "F.Fab")}") (hide yes)  (effects (font (size 1.27 1.27) (thickness 0.15)) (justify${ flip ? " mirror" : ""})))`);
// fp.push(`(property "Description" "" (at 0 0 ${(p.r + 0) % 360}) (unlocked yes) (layer "${(flip ? "B.Fab" : "F.Fab")}") (hide yes)  (effects (font (size 1.27 1.27) (thickness 0.15)) (justify${ flip ? " mirror" : ""})))`);

    fp.push(')');
    return fp.join('\n');
  }
}

