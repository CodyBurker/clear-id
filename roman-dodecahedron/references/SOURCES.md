# Reference photos: Norton Disney dodecahedron

All of these photos show the same object: the copper-alloy dodecahedron found in June 2023 at Norton Disney, Lincolnshire, by the Norton Disney History and Archaeology Group (NDHAG). Published figures: about 8 cm, 245–254 g.

Only the Geograph photo is included in this repo, because it is openly licensed. The others are copyrighted press photos, so they are linked rather than copied here.

| # | What it shows | Credit / source | Licence |
|---|---|---|---|
| 1 | Museum, front view (1920×1080) | NDHAG, via [Lincolnshire County Council](https://www.lincolnshire.gov.uk/news/article/1853/mysterious-roman-dodecahedron-found-in-norton-disney-to-go-on-display-in-lincolnshire-for-the-first-time) | © NDHAG |
| 2 | Museum, front view (4029×3022), the main reference for v4 | NDHAG, via [NPR/WHRO](https://www.whro.org/2024-01-24/amateur-archaeologists-uncover-a-mysterious-ancient-roman-artifact-in-england) | © NDHAG |
| 3 | At the dig, looking almost straight at one face (3024×3024) | NDHAG, via [NPR/WHRO](https://www.whro.org/2024-01-24/amateur-archaeologists-uncover-a-mysterious-ancient-roman-artifact-in-england) | © NDHAG |
| 4 | At the dig, another side | [Archaeology Magazine](https://archaeologymag.com/2024/01/roman-dodecahedron-uncovered-in-england/) | © the publisher |
| 5 | At the dig, looking down on top | NDHAG, via [ScienceAlert](https://www.sciencealert.com/rare-roman-dodecahedron-found-in-england-baffles-archaeologists) | © NDHAG |
| 6 | Studio shot, dark background | Phil Crow / Alamy, via [Scientific American](https://www.scientificamerican.com/article/why-did-ancient-romans-make-this-baffling-metal-dodecahedron) | © Alamy |
| 7 | Museum case, smallest hole facing the camera: `geograph_7766991_RichardCroft_CC-BY-SA-2.0.jpg` | Richard Croft, [Geograph SK9771](https://www.geograph.org.uk/photo/7766991) | [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) |

## Measurements used for v4

**Scale:** the knob balls look circular from any viewing angle, so I used them as the ruler. In #2 the distance between knob centres along a face edge is 309 px, and in the model it is 26.0 mm. That gives about 0.084 mm/px. The knob diameter comes out at 0.29–0.30 × that edge, about 7.6 mm.

**Holes:** for tilted faces I measured the long axis of the elliptical opening, because that axis isn't shortened by the tilt.

| Face (in the `.scad`) | Where it appears | Estimate |
|---|---|---|
| 4 | #2, front | 18.3 mm, used as 18.5 |
| 8 | #2, top | ~18 mm, used as 17.5 |
| 7 | #2, upper-left | 22–24 mm, used as 22 so a ring still fits |
| 6 | #2, upper-right | ~8.5 mm |
| 2 / 5 | #2, lower-left / lower-right | ~17 mm, used as 17 and 16 |
| 9 | #3, front (opposite face 4) | ~14 mm |
| 11 / 10 / 0 | #3, top / upper-left / lower-left | ~15.5 / ~12.5 / ~19 mm |
| 1, 3 | not clearly visible in any photo | guesses: 10 and 11 mm |

Matching faces between photos #2 and #3 assumes #3 shows the side opposite #2. The vertex-down orientation of both photos and the hole sizes are consistent with that, but it isn't proven.

**Rings:**
- In #2, grooves sit about 11.1 mm and 13.7 mm from the hole centre, and the outer ring reaches about 16 mm.
- In #7, around the small hole, grooves sit about 7.5, 10.4 and 13.2 mm from the centre.
- So the grooves are at a roughly fixed pitch measured in from the face edge, and the raised collar fills whatever space is left around the hole.
