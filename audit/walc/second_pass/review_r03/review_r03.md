# WALC second pass, review r03 (quick review, exterior only, colour check)

- **Asset:** `modular/buildings/walc.blend`, SHA-256 `77980a63…8de8688` (verified)
- **Score:** **8.02 / 10**, up from 5.75 in r01. Not accepted (threshold 9.9).

| Criterion | Max | r01 | r03 |
| --- | --- | --- | --- |
| Windows | 3.0 | 1.6 | 2.45 |
| Signature architecture | 2.5 | 1.25 | 1.9 |
| Proportions / roof | 2.0 | 1.45 | 1.85 |
| Material / colour | 1.5 | 0.85 | 1.02 |
| Consistency | 1.0 | 0.6 | 0.8 |

## r01 findings

**Fixed:**
- recessed arcade
- stone heads and sills, and the transom panels
- south-face schedule
- name band
- downpipes
- pilasters
- north-face jogs
- eave brackets and gutter

**Partly fixed:**
- **Window frames:** the colour is right, but the muntin layout is wrong.
- **Diaper:** present, but drawn too bold.
- **Shell holes:** the east/courtyard white wall is still there.
- **Stone courses:** the frieze is wrong.
- **Glazed-range bays and W struts:** the bays are better, but the W struts read as letters.

**Not fixed:** the roof is still too saturated and orange-red.

## Colour check

Patches and the script are in this folder (`colour_patches_*.png/json`, `sample_colours.py`).

| Material | Photo sRGB | Render sRGB | Verdict |
| --- | --- | --- | --- |
| Brick | 144,112,90 (close-up); 136,103,84 (bsa) | 126,91,79 | Close, slightly pink and dark |
| Mortar | light buff | 166,161,156 | OK |
| Diaper headers | 112,91,69 | 101,80,73 | Colour OK; pattern too bold |
| Stone | 213,204,185 / 220,216,202 | 198,192,180 | Match |
| End-block frames | 156,150,139 (close-up); near-white in sun elsewhere | 154,154,146 | Matches the close-up |
| Glazed-range frames | 170,145,116 | 128,126,121 | Too grey; should be bronze-taupe |
| Glass | 43,49,45 to 139,169,172 | 86,100,108 flat | Acceptable, but flat |
| Roof tile | aerial 149-168,121-137,101-114 | 146,86,69 | Too saturated orange-red |
| Soffit | 37,33,34 / 103,84,58 | 55,55,55 | Should be warm, not neutral |
| Downpipes | 97,85,70 | 83,64,60 | Match |
| Lettering | 138,119,92 | 115,112,105 | Too neutral |
| Canopies | 146,155,123 verdigris | 98,102,95 | Wrong hue |

## Remaining exterior issues, by visual impact

1. **White wall on the east/courtyard side.** An untextured white wall is exposed (G_V09, G_east_side, obl_SE).
2. **Roof saturation.** The roof is too saturated (hue 13°, saturation 0.53, against 25° and 0.32 in the aerial). Target about 140,100,85.
3. **End-block muntins.** The windows use a 4×3 grid. The photos show units 2 lites wide, with short top and bottom panes and a tall middle pane, paired on wide openings.
4. **W struts.** The flat W shapes in the facade plane read as letters. The photo shows slim paired struts that project from each pier.
5. **Eave frieze.** The model has a tall plain grey frieze. The photos show a brick frieze (with diaper) and a slim stone cornice, with a warm dark-brown soffit.
6. **Diaper.** The lattice is too bold and line-like; it should be a fine net of headers with straight edges.
7. **Glazed-range colours.** The bay frames, canopies and letters need to be warmer: bronze, verdigris and bronze.
8. **Brick hue.** Shift it about 8° toward orange-brown.
9. **NW junction.** Tile shows under the eave, and a stray frame fragment sticks out.
10. **Glass.** It is flat and too light; it needs darker glass with some reflection.

Full detail is in `review_r03.json`.
