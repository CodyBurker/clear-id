# Roman dodecahedron replica (v5, true 1:1 scale)

This is a 3D-printable replica of the **Norton Disney Roman dodecahedron**, found in 2023 in Lincolnshire, UK. Its size, hole diameters, face layout, ring counts and knob dimensions come from the specialist report on the object. The surface detail is interpreted from photographs; it is not a scan.

This folder is unrelated to the `clear-id` package. It is kept here only so the work is saved.

| Path | Contents |
|---|---|
| `models/roman_dodecahedron_v5.stl` | **Print file.** Binary STL, 475,958 triangles, already in print orientation |
| `models/roman_dodecahedron_v5.scad` | Editable parametric source. It rebuilds the STL byte-for-byte |
| `models/previous/` | v3 and v4 sources (their STLs can be rebuilt from these) |
| `renders/` | Direct renders of the v5 STL: the report's Fig. 3 six-view lineup (`v5_fig3_lineup.png`), museum-photo view, the report's front view, three-quarter, print orientation, and a cross-section. Also v3 and v4 museum views for comparison |
| `validation/` | Raw output of the checks below |
| `scripts/` | Mesh validator, printability checker, VTK renderer, Fig. 3 lineup renderer (`lineup.py`), and the face-letter mapping |
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
| Holes: A 29, B 20.3, C 13.4, D 19.4, E 20.4, F 20, G 27, H 17.6, I 17.5, J 9.9, K 16.2, L 17 mm | Placed per the report's face key (Fig. 2), corrected against its Fig. 3 photos (see below). A is the base and G the top |
| Rings: Face A one, Face J three, all others two | `ring_count` |
| Face K: "particularly crisp, deep" rings | Face K's rings raised 35% higher |
| Knobs 9–9.5 mm wide; projection 8–8.5 mm; "robust and short-necked" | 9.25 mm knobs on short necks, 3.4 mm neck radius. Knob tips sit 7.4 mm beyond the vertex (see SOURCES.md) |
| Width without knobs 7.5 cm, height without knobs 7 cm | Matches the model's vertex-to-vertex (75.7 mm) and edge-to-edge (70.7 mm) distances |

**Wall thickness:** the bronze wall is not given in the report. Working back from the 254 g weight and the alloy measured by XRF (density about 9.3 g/cm³), the original wall comes out at roughly 1.5 mm. v5 uses 2.8 mm so the wall stays at least 2.4 mm under the grooves for FDM printing. A print therefore weighs more than bronze-equivalent proportions would suggest. Lower `wall` for resin printing.

### Check against the report's Fig. 3 photographs

`scripts/lineup.py` renders the STL from the six viewpoints of the report's Fig. 3 (top, left, front, right, back, bottom), with the object resting on Face A. The side views each look at a corner where one base-tier face (below) meets two top-tier faces (above). I measured the hole openings in each photo against the report's 8 cm scale bar:

| View | Upper-left | Upper-right | Lower |
|---|---|---|---|
| Front | 17.9 mm (I = 17.5) | 18.6 mm (H = 17.6) | 21.0 mm (B = 20.3) |
| Left | 9.8 mm (J = 9.9) | 17.6 mm (I = 17.5) | **20.9 mm** (key says C = 13.4) |
| Right | 17.0 mm (H = 17.6) | 17.7 mm (L = 17) | **13.1 mm** (key says F = 20) |
| Back | | 16.3 mm (K = 16.2) on top | |

**Does the model match the table?** It contains exactly the twelve diameters from Table 1, one per face. Faces A, B and G–L sit where the key (Fig. 2) puts them. The two base-tier pairs C/F and D/E are placed the other way round from the key, because that is what the report's own photographs show:

- The key puts the smallest base-tier hole (C, 13.4) at the corner shared with the smallest top-tier hole (J, 9.9). In the photos the 9.9 mm hole sits above a ~21 mm hole, and the 13 mm hole sits below two ~17 mm holes. The two smallest holes never share a corner. Adjacency doesn't change when you rotate the object, so no orientation of the literal key fixes this.
- I also checked by brute force: for every one of the 60 ways to orient the model, the key read literally fits the three side photos no better than 3.4 mm RMS (the lower holes come out 13.4 and 20 where 20.9 and 13.1 were photographed). With the base tier reversed the best orientation fits to 0.6 mm, and it is the orientation the key describes (resting on A, B in front).
- A full mirror image, and reversing only the top tier, were also tested. Neither fits.
- This is consistent with the report's own convention that the smallest base-tier hole is "usually Face F, positioned to the right".
- The top and bottom photos can't settle it: the in-plane rotation of those shots is unknown, and either labelling can be rotated to put the small hole where the photo has it. Those two views in `lineup.py` use the rotation and slight camera lean that fit each photo best (top: J at left; bottom: 13.4 at upper-left, camera leaning toward the upper-right).

`bottom_tier_reversed = true` in the `.scad` applies the swap; set it to `false` for a literal reading of Fig. 2.

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
| Local thickness (40k surface samples) | 1st percentile 2.48 mm. 50 samples read under 1.2 mm, all explained: 28 on rounded hole lips and 22 on the flanks of raised rings, where the test ray crosses the ring sideways on top of the full wall. **0 unexplained** |
| Bed contact | 5 separate flats on the knob tips around Face A, 107 mm² in total |
| Overhangs > 45° from vertical | 2,437 mm² (9% of the surface) |
| Real slicer | PrusaSlicer 2.7.2 CLI at 0.12 mm layers, 4 perimeters, organic supports from the build plate: sliced without errors. 611 layers, 48.4 cm³ of filament including supports, about 11.9 h at generic speeds |

**Not tested:** a physical print, and slicing with a specific printer's profile.

## Printing

- **Orientation:** use the STL as exported. It rests on the five knobs around Face A, the largest opening, so the bottom face needs the least support. The report calls Face A the base.
- **Supports:** tree or organic, **from the build plate only**.
- **Brim:** 3–4 mm.
- **Layer height:** 0.12 mm.
- **Walls:** 0.4 mm nozzle with 4 perimeters.
- **Smaller print:** you can scale it down in the slicer, but the walls and relief scale with it. At 87% (about 79 mm), the minimum wall is about 2.1 mm.

## Version history

- **v5:** true scale; the report's hole sizes, face letters, ring counts and knob dimensions; shorter knob necks. Base-tier hole placement was then corrected against the report's Fig. 3 photos.
- **v4:** raised ring relief and hole sizes estimated from photos.
- **v3:** first version with every hole verified open.
- **v2:** not included; every hole was sealed by a ~0.5 mm membrane.

## Known tradeoffs

- The rings are perfectly circular revolved shapes. The original's are slightly irregular.
- The small dent on Face L described in the report is not modelled.
- Five knobs have small flats so the print sits stably. Set `print_orientation=false` if you want a model without them.
