// BAV70 diode, designed around the BAV70 RFG from Taiwan Semiconductor
// See https://services.taiwansemi.com/storage/resources/datasheet/BAW56%20SERIES_I2001.pdf
module.exports = {
    params: {
        designator: "D",
        side: "F",
        reversible: false,
        silkscreen: true,
        pad_width: 0.85,
        pad_height: 1.25,
        swap_nets: false,
        A1: { type: "net", value: undefined },
        A2: { type: "net", value: undefined },
        C: { type: "net", value: undefined },    
        diode_3dmodel_filename: '\${KICAD9_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SOT-23.step',
        diode_3dmodel_xyz_offset: [0, 0, 0],
        diode_3dmodel_xyz_rotation: [0, 0, 90],
        diode_3dmodel_xyz_scale: [1, 1, 1],
    },

    body: (p) => {
        const justify = p.side == "B" ? "(justify mirror)" : "";

        if (p.swap_nets) {
            [p.A1, p.A2] = [p.A2, p.A1];
        }

        let padNo = 1;
        const pad = (x, y, pin) => {
            const layers = (side) => ["Cu", "Paste", "Mask"].map((layer) => `\"${side}.${layer}\"`).join(" ");

            const sides = p.reversible ? ["F", "B"] : [p.side];

            return sides
                .map(
                    (side) => `
                    (pad "${padNo++}" smd roundrect
                        (at ${x} ${y} ${p.rot})
                        (size ${p.pad_width} ${p.pad_height})
                        (layers ${layers(side)})
                        (roundrect_rratio 0.1)
                        ${pin.str}
                    )`
                )
                .join("\n");
        };

        const lines = (...coords) => {
            if (coords.length < 4 || coords.length % 2) {
                throw new Error(`Invalid coordinates: expected an even number >= 4, got ${coords.length}`);
            }

            // Determine target layers
            const layers = p.silkscreen ? (p.reversible ? ["F.SilkS", "B.SilkS"] : [`${p.side}.SilkS`]) : ["Dwgs.User"];

            // Format a single line entry
            const line = ([x1, y1, x2, y2], layer) =>
                `(fp_line 
                    (start ${x1} ${y1}) 
                    (end ${x2} ${y2}) 
                    (layer "${layer}") 
                    (stroke (width 0.12) 
                    (type solid))
                )`;

            // Build lines by slicing coords into quads and mapping layers
            return Array.from({ length: (coords.length - 2) / 2 }, (_, i) => coords.slice(i * 2, i * 2 + 4))
                .flatMap((quad) => layers.map((layer) => line(quad, layer)))
                .join("\n");
        };

        const h = 2 * p.pad_height + 1.1;
        const w = 2 * p.pad_width + 1.1;

        // Cathode
        const cx = 0;
        const cy = -(h - p.pad_height) / 2;

        // Anodes
        const a1x = -(w - p.pad_width) / 2;
        const a2x = a1x * -1;
        const ay = cy * -1;

        // Line offset from pad
        const d = p.pad_width / 2 + 0.25;

        return `
            (footprint "BAV70 SOT23" (generator pcbnew)
                (layer "${p.side}.Cu")
                ${p.at}
                (property "Reference" "${p.ref}"
                    (at 0 0 ${p.r})
                    (layer "${p.side}.SilkS")
                    ${p.ref_hide}
                    (effects (font (size 1 1) (thickness 0.15)) ${justify})
                )
                (attr smd)
                (fp_text value "BAV70" (at 0 0 ${p.rot}) (layer ${p.side}.Fab)
                    (effects (font (size 1 1) (thickness 0.15)) ${justify})
                )

                ${lines(cx - d, -0.65, -1.46, -0.65, -1.46, 0.3)}
                ${lines(cx + d, -0.65, 1.46, -0.65, 1.46, 0.3)}
                ${lines(a1x + d, 0.65, a2x - d, 0.65)}

                ${pad(a1x, ay, p.A1)}
                ${pad(a2x, ay, p.A2)}
                ${pad(cx, cy, p.C)}
                (model ${p.diode_3dmodel_filename} (offset (xyz ${p.diode_3dmodel_xyz_offset[0]} ${p.diode_3dmodel_xyz_offset[1]} ${p.diode_3dmodel_xyz_offset[2]})) (scale (xyz ${p.diode_3dmodel_xyz_scale[0]} ${p.diode_3dmodel_xyz_scale[1]} ${p.diode_3dmodel_xyz_scale[2]})) (rotate (xyz ${p.diode_3dmodel_xyz_rotation[0]} ${p.diode_3dmodel_xyz_rotation[1]} ${p.diode_3dmodel_xyz_rotation[2]})))

        )`;
    },
};
