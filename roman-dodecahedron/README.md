# Roman dodecahedron replica (v5, true 1:1 scale)

This is a 3D-printable replica of the **Norton Disney Roman dodecahedron**, found in 2023 in Lincolnshire, UK. Its size, hole diameters, face layout, ring counts and knob dimensions come from the specialist report on the object. The surface detail is interpreted from photographs; it is not a scan.

This folder is unrelated to the `clear-id` package. It is kept here only so the work is saved.

| Path | Contents |
|---|---|
| `models/roman_dodecahedron_v5.stl` | **Print file.** Binary STL, 475,646 triangles, already in print orientation |
| `models/roman_dodecahedron_v5.scad` | Editable parametric source. It rebuilds the STL byte-for-byte |
| `models/previous/` | v3 and v4 sources (their STLs can be rebuilt from these) |
| `renders/` | Direct renders of the v5 STL: museum-photo view, the report's front view, three-quarter, print orientation, and a cross-section. Also v3 and v4 museum views for comparison |
| `validation/` | Raw output of the checks below |
| `scripts/` | Mesh validator, printability checker, VTK renderer, and the face-letter mapping |
| `references/SOURCES.md` | Sources, the measurements used, and how faces were matched to the photos |

Rebuild with OpenSCAD 2024 or later:

```
openscad --backend=manifold -o roman_dodecahedron_v5.stl models/roman_dodecahedron_v5.scad
```

It takes about 8 s. Add `-D print_orientation=false` for an upright model with no flats on the knobs.

## Source data

Primary source: L. Hitchens (2023), *Roman Dodecahedron*, Appendix 7 of the Allen Archaeology report on the Norton Disney community excavation, held by the Archaeology Data Service.

| From the report | Used in v5 |
|---|---|
| All faces 27 mm per side | `edge_length = 27` |
| Holes: A 29, B 20.3, C 13.4, D 19.4, E 20.4, F 20, G 27, H 17.6, I 17.5, J 9.9, K 16.2, L 17 mm | Placed per the report's face key (Fig. 2). A is the base and G the top |
| Rings: Face A one, Face J three, all others two | `ring_count` |
| Face K: "particularly crisp, deep" rings | Face K's rings raised 35% higher |
| Knobs 9–9.5 mm wide; projection 8–8.5 mm; "robust and short-necked" | 9.25 mm knobs on short necks, 3.4 mm neck radius. Knob tips sit 7.4 mm beyond the vertex (see SOURCES.md) |
| Width without knobs 7.5 cm, height without knobs 7 cm | Matches the model's vertex-to-vertex (75.7 mm) and edge-to-edge (70.7 mm) distances |

**Wall thickness:** the bronze wall is not given in the report. Working back from the 254 g weight and the alloy measured by XRF (density about 9.3 g/cm³), the original wall comes out at roughly 1.5 mm. v5 uses 2.8 mm so the wall stays at least 2.4 mm under the grooves for FDM printing. A print therefore weighs more than bronze-equivalent proportions would suggest. Lower `wall` for resin printing.

## Validation (run on the exported `models/roman_dodecahedron_v5.stl`)

| Check | Result |
|---|---|
| Size | Largest dimension 90.8 mm, knob tip to knob tip. Bounding box 89.4 × 85.3 × 73.4 mm in print orientation (resting on Face A) |
| Watertight / consistent winding / positive volume | yes / yes / yes (39.0 cm³) |
| Non-manifold edges / degenerate faces / duplicate faces | 0 / 0 / 0 |
| Connected bodies | 1 |
| Topology | Euler number −20, so genus 11: one hollow shell with 12 through-holes |
| Holes open | 444 rays along the 12 hole axes: 0 blocked |
| Face wall under the grooves | Minimum 2.45 mm (target ≥ 2.4) |
| Local thickness (40k surface samples) | 1st percentile 2.48 mm. 44 samples read under 1.2 mm, all explained: 18 on rounded hole lips, 7 on the face-border bead, and 19 on the flanks of raised rings. In the last two cases the test ray crosses the relief sideways, on top of the full wall. **0 unexplained** |
| Bed contact | 5 separate flats on the knob tips around Face A, 107 mm² in total |
| Overhangs > 45° from vertical | 2,443 mm² (9% of the surface) |
| Real slicer | PrusaSlicer 2.7.2 CLI at 0.12 mm layers, 4 perimeters, organic supports from the build plate: sliced without errors. 611 layers, 48.3 cm³ of filament including supports, about 11.8 h at generic speeds |

**Not tested:** a physical print, and slicing with a specific printer's profile.

## Printing

- **Orientation:** use the STL as exported. It rests on the five knobs around Face A, the largest opening, so the bottom face needs the least support. The report calls Face A the base.
- **Supports:** tree or organic, **from the build plate only**.
- **Brim:** 3–4 mm.
- **Layer height:** 0.12 mm.
- **Walls:** 0.4 mm nozzle with 4 perimeters.
- **Smaller print:** you can scale it down in the slicer, but the walls and relief scale with it. At 87% (about 79 mm), the minimum wall is about 2.1 mm.

## Version history

- **v5:** true scale; the report's hole sizes, face letters, ring counts and knob dimensions; shorter knob necks.
- **v4:** raised ring relief and hole sizes estimated from photos.
- **v3:** first version with every hole verified open.
- **v2:** not included; every hole was sealed by a ~0.5 mm membrane.

## Known tradeoffs

- The rings are perfectly circular revolved shapes. The original's are slightly irregular.
- The small dent on Face L described in the report is not modelled.
- Five knobs have small flats so the print sits stably. Set `print_orientation=false` if you want a model without them.
