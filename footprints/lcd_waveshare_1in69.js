// 1.69in LCD Mounting Holes ergogen footprint
//
// Author: Hunter Cook @huntercook https://github.com/jusdisgi
// Canonical location: https://github.com/jusdisgi/ergogen-footprints/blob/main/conn_molex_picoblade_smd_1x08_1mm25_horiz.js
//
// created with kicad2ergogen: https://kicad2ergogen.genteure.com/
//
// To be clear, this is just silkscreen and 4 M2 mounting holes. The device has a Molex PicoBlade connector on it for connection
// to the board. Suggest using the conn_molex_picoblade_* footprints if you want the same connection on the board side.
//
// Nets/Parameters
//
// side: F (default) for Front, B for Back

module.exports = {
  params: {
    designator: 'LCD',
    side: 'F',    
    lcd_3dmodel_filename: '\${MODELS}/waveshare_LCD_1in69.stp',
    lcd_3dmodel_xyz_offset: [0, 0, 0],
    lcd_3dmodel_xyz_rotation: [0, 0, 0],
    lcd_3dmodel_xyz_scale: [1, 1, 1],
  },
  body: p => {
    const fp = [];
    const flip = p.side === "B";
if (!flip && p.side !== "F") throw new Error('unsupported side: ' + p.side);

fp.push(`(footprint "LCD_1.69_Waveshare"`);
fp.push(p.at);
fp.push(`(layer "${(flip ? "B.Cu" : "F.Cu")}")`);
fp.push(`(property "Reference" "${p.ref}" ${p.ref_hide} (at 0 0 ${p.r}) (layer "${p.side}.SilkS") (effects (font (size 1 1) (thickness 0.15))${ p.side === "B" ? " (justify mirror)" : ""}))`);
fp.push(`(attr board_only)`); //Do not include in schematic
fp.push(`(attr smd)`);

// Unknown to kicad2ergogen
fp.push(`(embedded_fonts no)`);

// Pads
fp.push(`(pad "" np_thru_hole circle (at ${(flip ? 12.2 : -12.2)} -15.9 ${p.r}) (size 2.2 2.2) (drill 2.2) (layers "F&B.Cu" "*.Mask") )`);
fp.push(`(pad "" np_thru_hole circle (at ${(flip ? 12.2 : -12.2)} 15.9 ${p.r}) (size 2.2 2.2) (drill 2.2) (layers "F&B.Cu" "*.Mask") )`);
fp.push(`(pad "" np_thru_hole circle (at ${(flip ? -12.2 : 12.2)} -15.9 ${p.r}) (size 2.2 2.2) (drill 2.2) (layers "F&B.Cu" "*.Mask") )`);
fp.push(`(pad "" np_thru_hole circle (at ${(flip ? -12.2 : 12.2)} 15.9 ${p.r}) (size 2.2 2.2) (drill 2.2) (layers "F&B.Cu" "*.Mask") )`);

// Drawings on F.Fab
fp.push(`(fp_text user "\${REFERENCE}" (at 0 2.5 ${(p.r + 0) % 360}) (unlocked yes) (layer "${(flip ? "B.Fab" : "F.Fab")}")  (effects (font (size 1 1) (thickness 0.15)) (justify${ flip ? " mirror" : ""})))`);

// Drawings on F.SilkS
fp.push(`(fp_rect (start ${(flip ? 15.75 : -15.75)} -19.5) (end ${(flip ? -15.75 : 15.75)} 19.5) (stroke (width 0.1) (type solid)) (fill no) (layer "${(flip ? "B.SilkS" : "F.SilkS")}") )`);
fp.push(`(fp_rect (start ${(flip ? 7.375 : -7.375)} -7.03) (end ${(flip ? -7.375 : 7.375)} -2.83) (stroke (width 0.1) (type solid)) (fill no) (layer "${(flip ? "B.SilkS" : "F.SilkS")}") )`);

// Properties
// fp.push(`(property "Reference" "REF**" (at 0 -0.5 ${(p.r + 0) % 360}) (unlocked yes) (layer "${(flip ? "B.SilkS" : "F.SilkS")}")  (effects (font (size 1 1) (thickness 0.1)) (justify${ flip ? " mirror" : ""})))`);
// fp.push(`(property "Value" "1.69\\" LCD" (at 0 1 ${(p.r + 0) % 360}) (unlocked yes) (layer "${(flip ? "B.Fab" : "F.Fab")}")  (effects (font (size 1 1) (thickness 0.15)) (justify${ flip ? " mirror" : ""})))`);
// fp.push(`(property "Datasheet" "" (at 0 0 ${(p.r + 0) % 360}) (unlocked yes) (layer "${(flip ? "B.Fab" : "F.Fab")}") (hide yes)  (effects (font (size 1 1) (thickness 0.15)) (justify${ flip ? " mirror" : ""})))`);
// fp.push(`(property "Description" "" (at 0 0 ${(p.r + 0) % 360}) (unlocked yes) (layer "${(flip ? "B.Fab" : "F.Fab")}") (hide yes)  (effects (font (size 1 1) (thickness 0.15)) (justify${ flip ? " mirror" : ""})))`);

//3D Model
fp.push(`(model ${p.lcd_3dmodel_filename} (offset (xyz ${p.lcd_3dmodel_xyz_offset[0]} ${p.lcd_3dmodel_xyz_offset[1]} ${p.lcd_3dmodel_xyz_offset[2]})) (scale (xyz ${p.lcd_3dmodel_xyz_scale[0]} ${p.lcd_3dmodel_xyz_scale[1]} ${p.lcd_3dmodel_xyz_scale[2]})) (rotate (xyz ${p.lcd_3dmodel_xyz_rotation[0]} ${p.lcd_3dmodel_xyz_rotation[1]} ${p.lcd_3dmodel_xyz_rotation[2]})))`);

    fp.push(')');
    return fp.join('\n');
  }
}

