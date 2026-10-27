# Independent AOII R2 grade

## Verdict: 8.4/10 — Pass

The revised asset is a credible, source-supported representation of the Alpha Omicron Pi Phi Upsilon house at 242 S Grant St. Its strongest evidence is the parcel-specific identity cross-check, near-exact footprint comparison, and corrected street-facing facade. Remaining differences are mainly roof silhouette and details/layout that available sources cannot establish.

## Scores

| Category | Score | Evidence and deductions |
|---|---:|---|
| Identity and footprint | 2.0 / 2.0 | Official AOII house page gives 242 S Grant; the saved Street View panorama directly faces the parcel. The slab ring independently re-parsed from the freshly opened blend has six vertices, 276.2303245 m² area, IoU 0.99999897 against OSM way 970455277, and 0.0000182 m symmetric Hausdorff distance. This is a serialization/transform recheck because the asset originated from this polygon, not independent proof of wall lines. |
| Placement and scale | 1.8 / 2.0 | Model dimensions and campus-world origin match the mapped parcel convention and source register. The footprint is exactly parcel-scale. The standalone asset was reviewed; its final alignment against the newest master scene was outside this grading pass. |
| Floors, height, and roof | 1.5 / 2.0 | Three functional levels (grade parking plus two residential levels) are supported by the 2015 city report. Overall height is plausible but estimated. The reference shows a very low, nearly flat-looking roof edge; the model's adjoining hip volumes read more prominently pitched in the previews. Exact ridge form/pitch remains undocumented. |
| Facade and entrance | 1.7 / 2.0 | Street-facing brick base, beige horizontal siding on both upper floors, dark shutters, and a centered grade entry correspond well to the saved panorama. The model regularizes the window rhythm and entry surrounds; photo details such as AC units, shrubs, signage, paired window groups, and the dark continuous eave are absent or simplified. Unseen elevations are extrapolated. |
| Interior, portability, and evidence | 1.4 / 2.0 | Fresh-open inspection found a self-contained scene/collection, 1,780 mesh objects, 14 used materials, zero linked libraries, and no unpacked image dependencies. Object inventory includes garage/parking, stair components, kitchen/dining/lounge objects, bedroom partitions and furniture for 15 bed bays. This is a plausible authored interior but not a verified floor plan. Three preview renders and source snapshots make review reproducible. |
| **Total** | **8.4 / 10** | **Pass (threshold 8.0).** |

## Independent fresh-open checks

Blender 5.2.3 LTS reopened the asset from disk. Scene `Building_massing_house_970455277_a3fb72a` and collection `Asset_massing_house_970455277_a3fb72a` were present. No probe errors were reported. Local bounds including site furniture are X −11.300…8.212 m, Y −10.012…10.012 m, Z −0.100…9.785 m. The slab's lowest ring was extracted in mesh order, then independently compared with the saved OSM way using the project's documented approximate WGS84-to-local-XY transform and recorded origin.

The actual file SHA-256 is `3ac83c2841058b6de3a7f19c587e151df6b3751589a82f03ec4f1c6460da5ec7` (64 hexadecimal characters). The requested frozen hash and `source_register.json` contain `...f03ecf1c...`, which is malformed/differs from the actual file hash (`...f03ec4f1c...`). This appears to be a transcription error in the expected hash, not an asset integrity failure; the actual SHA remained stable during the independent fresh-open pass. Correct the provenance value before treating the register as an integrity lock.

## Specific improvements that would strengthen the result

1. Lower the hip-roof pitch/visual rise to better match the nearly-flat roof edge in Street View, while retaining the low hip silhouette.
2. Match the observed facade's paired/unequal window groupings and dark continuous eave more closely; add recognizable entry sidelights and street-facing AC units if the asset's detail target warrants them.
3. Keep the interior explicitly labeled as illustrative unless an as-built floor plan becomes available.
4. Fix the malformed SHA-256 in the source register and any handoff/validation note before master integration.

## Audit artifacts

- `fresh_open_probe.json` — fresh-open Blender metadata, hash, bounds, portability, and slab ring.
- `gis_comparison.json` — independent OSM footprint comparison.
- `interior_inventory.json` — object-name inventory evidence for authored interior components.
- `preview_front_west.png`, `preview_entry_isometric.png`, `preview_terrace_aerial.png` — reviewed asset renders (source snapshots in parent audit folder).
