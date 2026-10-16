# Sources: Norton Disney dodecahedron

## Primary source: specialist report

L. Hitchens (2023), *Roman Dodecahedron*, Appendix 7 of the Allen Archaeology report on the 2023 Norton Disney community excavation for the Norton Disney History and Archaeology Group (NDHAG). It is held by the Archaeology Data Service, record `allenarc1-521355`:
<https://archaeologydataservice.ac.uk/archiveDS/archiveDownload?t=arch-805-1/dissemination/allenarc1-521355_222037.pdf>
(see PDF pages 39–42).

Used from it:
- Table 1: the 27 mm sides, all twelve hole diameters, knob width and projection, and overall sizes.
- Fig. 2: the face key (letters A–L).
- The text: ring counts (A one, J three, others two), Face K's especially crisp rings, "robust and short-necked" knobs, and the alloy (Cu 63%, Pb 26%, Sn 8%).
- Fig. 3: a composite photo with an 8 cm scale bar.

The report's figures are © Lorena Hitchens 2023 and are not copied into this repo.

## Mapping face letters onto the model

`scripts/faces_letters.py` builds the report's lettering on the model's geometry:
- A is the base, and B is a neighbouring face of A, facing the viewer.
- Going around the base tier: C is to the left of B, then D and E, and F is to the right of B.
- G is opposite A.
- Going around the top tier: H is above-right of B, I above-left, then J, K, L.

It checks the result against Fig. 2's adjacencies (C touches I and J, F touches H and L, K touches D and E).

**Which way up the museum photo is.** The museum photo shows the top face nearly edge-on, so the object is resting with a big-hole face (A or G) on top or bottom. Of the ten orientations this allows, only one puts the tiny 9.9 mm hole (J) at upper-right, as the photo shows:

| Position in the museum photo | Face |
|---|---|
| Front | K |
| Top | G |
| Upper-left | L |
| Upper-right | J |
| Lower-left | E |
| Lower-right | D |

The report's remark that Face K's rings are especially crisp matches the very crisp front face in that photo.

**Check against Fig. 3.** I re-rendered the STL from Fig. 3's six viewpoints (`scripts/lineup.py`) and measured the dark openings in the photos against the scale bar. To do this I thresholded the dark pixels and fitted ellipses with the same spread to get each hole's long axis. In each side view the camera looks at a corner where one base-tier face (below) meets two top-tier faces (above):

| View | Upper-left | Upper-right | Lower |
|---|---|---|---|
| Front | 17.9 mm (I = 17.5) | 18.6 mm (H = 17.6) | 21.0 mm (B = 20.3) |
| Left | 9.8 mm (J = 9.9) | 17.6 mm (I = 17.5) | 20.9 mm (key says C = 13.4) |
| Right | 17.0 mm (H = 17.6) | 17.7 mm (L = 17) | 13.1 mm (key says F = 20) |
| Back | | 16.3 mm (K = 16.2) on top | |

- The front view and the whole upper tier match Fig. 2 exactly.
- The base tier runs the other way round from Fig. 2: the 13.4 mm hole is to the right of B. The orientation-independent form of this: in the key, C (13.4) and J (9.9) share a corner; in the photos they don't.
- Brute force over all 60 orientations of the model: literal key, best 3.4 mm RMS on the side views; base tier reversed, best 0.6 mm (at the key's own orientation). A full mirror and a top-tier-only reversal were tested too; neither fits.
- So `bottom_tier_reversed = true` in the `.scad` places the base-tier sizes as photographed.
- Top and bottom photos: their in-plane rotation is unknown, so they can't distinguish the two labellings. `lineup.py` renders them at the rotation that fits each photo (top: roll 0, J at left; bottom: roll 288, 13.4 at upper-left), with an 8° camera lean (top: toward the bottom of the frame; bottom: toward the upper-right), judged from how open each surrounding hole appears.

In the `.scad`, `face_letter = [C, A, E, F, K, D, J, L, G, B, I, H]` gives the key position of each face index (0–11); with the reversal, hole sizes come from `[F, A, D, C, K, E, J, L, G, B, I, H]`.

## Knob height

The report gives the knob projection as 8–8.5 mm without saying where it was measured from.

**Measuring from the scale bar.** In the Fig. 3 front view (6.4 px/mm at 400 dpi):
- The knobs measure 9.0 mm and the overall width 85.3 mm. The report gives 9–9.5 mm and 86 mm, so that view's scale is reliable.
- The horizontal spacing of the outermost knob centres (76.9 mm) puts the knob centres about 41 mm from the body centre.
- That means the tip is about 7.4 mm beyond the sharp vertex.

So the report's 8–8.5 mm was most likely measured from the neck base, and v5 uses a 7.4 mm tip beyond the vertex. The vertical spacing gives 44 mm, but that is inflated by perspective because the lower knobs are closer to the camera.

## Wall thickness (estimate)

- **Alloy density:** about 9.3 g/cm³, from the XRF result (Cu 63%, Pb 26%, Sn 8%).
- **Volume of the original:** 254 g ÷ 9.3 g/cm³ ≈ 27.3 cm³.
- **Model volume:** v5 with a 2.8 mm wall is 39.0 cm³.
- **Working back:** the cavity surface is about 87.5 cm². Removing the 11.7 cm³ difference over that area means the original wall is about 1.5 mm.

This is an estimate: it assumes the same relief and knobs as the model.

## Photographs (reference only, not in this repo except #7)

| # | What it shows | Credit / source | Licence |
|---|---|---|---|
| 1 | Museum, front view (1920×1080) | NDHAG, via [Lincolnshire County Council](https://www.lincolnshire.gov.uk/news/article/1853/mysterious-roman-dodecahedron-found-in-norton-disney-to-go-on-display-in-lincolnshire-for-the-first-time) | © NDHAG |
| 2 | Museum, front view (4029×3022) | NDHAG, via [NPR/WHRO](https://www.whro.org/2024-01-24/amateur-archaeologists-uncover-a-mysterious-ancient-roman-artifact-in-england) | © NDHAG |
| 3 | At the dig, looking almost straight at one face | NDHAG, via [NPR/WHRO](https://www.whro.org/2024-01-24/amateur-archaeologists-uncover-a-mysterious-ancient-roman-artifact-in-england) | © NDHAG |
| 4 | At the dig, another side | [Archaeology Magazine](https://archaeologymag.com/2024/01/roman-dodecahedron-uncovered-in-england/) | © the publisher |
| 5 | At the dig, looking down on top | NDHAG, via [ScienceAlert](https://www.sciencealert.com/rare-roman-dodecahedron-found-in-england-baffles-archaeologists) | © NDHAG |
| 6 | Studio shot, dark background | Phil Crow / Alamy, via [Scientific American](https://www.scientificamerican.com/article/why-did-ancient-romans-make-this-baffling-metal-dodecahedron) | © Alamy |
| 7 | Museum case, small-hole side: `geograph_7766991_RichardCroft_CC-BY-SA-2.0.jpg` | Richard Croft, [Geograph SK9771](https://www.geograph.org.uk/photo/7766991) | [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) |

The v4 hole sizes were estimates from these photos. Measured against the report, they came out about 15% small.
