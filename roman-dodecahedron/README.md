# Roman dodecahedron replica (v4)

A 3D-printable replica of the **Norton Disney Roman dodecahedron** (found 2023, Lincolnshire, UK). It was modelled from photographs, so it is an interpretation, not a scan. This folder is unrelated to the `clear-id` package; it is kept here only so the work is saved.

| Path | Contents |
|---|---|
| `models/roman_dodecahedron_v4.stl` | **Print file.** Binary STL, 485,918 triangles, already in print orientation |
| `models/roman_dodecahedron_v4.scad` | Editable parametric source. It rebuilds the STL byte-for-byte |
| `models/previous/roman_dodecahedron_v3.scad` | The previous version (its STL can be rebuilt from this) |
| `renders/` | Direct renders of the v4 STL: museum-photo view, dig-photo view, three-quarter, print orientation, and a centre cross-section. Also the v3 museum view for comparison |
| `validation/` | Raw output of the checks below |
| `scripts/` | The mesh validator, printability checker and VTK renderer |
| `references/SOURCES.md` | Links and credits for the reference photos, and the measurements taken from them |

Rebuild with OpenSCAD 2024 or later:

```
openscad --backend=manifold -o roman_dodecahedron_v4.stl models/roman_dodecahedron_v4.scad
```

It takes about 8 s. Add `-D print_orientation=false` for an upright model with no flats on the knobs.

## What v4 changed

V4 was driven by seven reference photos. The proportions were measured using the knob balls as a scale, because they look circular from any angle.

- **Raised ring relief.** Each hole has a broad collar, then concentric rounded ridges separated by narrow grooves. The ring set is laid out from the face edge inward at a fixed 2.75 mm pitch. That puts the outer ring close to the edges, and gives small holes three grooves and the biggest only one, as on the original. Ridges rise 0.38 mm above the face; grooves cut 0.36 mm below it.
- **Knobs:** 7.6 mm, almost round balls on a short neck narrower than the ball, with a small fillet into the corner. (v3 had thick, flared roots.)
- **Crisper edges:** 1.2 mm rounding instead of v3's 2.8 mm.
- **Hole sizes re-measured:** 8.5–22 mm. Ten faces were measured from the photos; faces 1 and 3 aren't clearly visible in any photo, so their sizes are guesses. See `references/SOURCES.md`.
- **Unchanged from v3:** each face's opening is made by one revolved cutter that runs from inside the cavity to outside the face. That cutter is what keeps every hole open; v2 failed here, leaving a membrane across every hole.

## Validation (run on the exported `models/roman_dodecahedron_v4.stl`)

| Check | Result |
|---|---|
| Size | Largest dimension 78.6 mm, knob tip to knob tip. Bounding box 75.3 × 76.9 × 63.4 mm in print orientation |
| Watertight / consistent winding / positive volume | yes / yes / yes (29.3 cm³) |
| Non-manifold edges / degenerate faces / duplicate faces | 0 / 0 / 0 |
| Connected bodies | 1 |
| Topology | Euler number −20, so genus 11: one hollow shell with 12 through-holes |
| Holes open | 444 rays along the 12 hole axes: 0 blocked |
| Face wall under the grooves | Minimum 2.65 mm (target ≥ 2.4); nominal wall 3.0 mm |
| Local thickness (40k surface samples) | 1st percentile 2.66 mm. 4 samples read under 1.2 mm. All 4 are on the low (~0.2 mm) bead along the face borders: the test ray crosses the bead sideways. That is a surface ridge sitting on the full 3 mm wall, not a thin wall |
| Bed contact | 5 separate flats on the knob tips, 81 mm² in total |
| Overhangs > 45° from vertical | 2,602 mm² (12% of the surface) |
| Real slicer | PrusaSlicer 2.7.2 CLI at 0.12 mm layers, 4 perimeters, organic supports from the build plate: sliced without errors. 528 layers, 37.0 cm³ of filament including supports, about 9.9 h at generic speeds |

**Not tested:** a physical print, and slicing with a specific printer's profile.

## Printing

- **Orientation:** use the STL as exported. It rests on the five flattened knob tips around face 3.
- **Supports:** tree or organic, **from the build plate only**. They hold up the bottom face, which sits about 5 mm above the bed, and the undersides of the lower knobs.
- **Brim:** 3–4 mm, because the five contact pads are small.
- **Layer height:** 0.12 mm keeps the 0.35 mm ridges and grooves crisp.
- **Walls:** 0.4 mm nozzle with 4 perimeters, which makes the walls effectively solid.

## Known tradeoffs

- The rings are perfectly circular revolved shapes. The original's are slightly irregular and pitted.
- Five knobs have small flats so the print sits stably. Set `print_orientation=false` if you want a model without them.
- Surface texture and patina are left to painting.
