# SAMARA — building completion evidence

Asset: `modular/buildings/massing_samara_f6b8e61.blend`  
Stable collection: `Asset_massing_samara_f6b8e61`  
Stable scene: `Building_massing_samara_f6b8e61`  
Builder script: `modular/buildings/build_massing_samara_f6b8e61.py`

## Identity and sources

SAMARA is Frank Lloyd Wright's John E. and Catherine E. Christian House, 1301 Woodland Avenue, West Lafayette. HABS IN-247 identifies this address and the 1955–1956 construction. Raw measured drawings, report, LOC metadata, Foundation page/photo and the house's 2026 copper-restoration article are preserved here. `provenance.json` provides URLs, provider, source/retrieval dates, identifiers, CRS and uncertainty. The full-resolution TIFF remains a local reference; the JPEG and readable PNG plus explicit traced coordinates make the model reproducible without committing the large TIFF.

HABS fieldwork was undertaken in fall 2020, documentation compiled May 2021. The geometry represents that measured configuration with the patinated chimney cap documented by the owner in July 2026. Foundation photo is used to establish materials and distinctive fascia; no photograph-derived exact dimensions are claimed.

## Modeling and measurement

The HABS sheet 3 floor plan was manually digitized in the 1024-pixel derivative. The printed 85 ft 7-7/8 in overall dimension between x=206 and x=813 gives 0.04301157 m/pixel. Structural wall vertices are recorded independently of the roof and terrace in `build_record.json`. Wall thickness and small trim details are estimates. No global scaling was done to match OSM.

The existing roof-shaped OSM polygon (way 1096999543) supplies an approximate campus orientation of -63.5 degrees for drawing X and a translation calculated from roof bounds centers. The HABS north arrow is consistent within approximately 3 degrees. Registration remains an estimate of ±2 m, not independently geodetically verified. The red OSM and blue reconstructed roofs disagree locally, especially around overhangs; the overlay preserves that disagreement rather than hiding it. Roof-outline estimates are about ±0.5 m. The original massing's 16 m height was unsupported and has been replaced.

HABS sheets 4–6 explicitly label low roof soffit 6 ft 7-3/4 in (2.02565 m), upper roof surface 9 ft 6-1/2 in (2.9083 m), chimney 14 ft 4-1/2 in (4.3815 m), relative to entrance datum. Sheet 6 places living floor 1 ft 10 in below entrance. The model incorporates those vertical relationships. Campus Z=0 remains the inherited entrance reference; absolute terrain elevation is unverified.

The model adds the brick and mahogany/glass envelope, sunken living floor, interior hearth and service/bedroom partitions, large garden glazing, tiered flat roofs, clerestory glazing with simplified seed patterns, folded copper fascia motifs, terraces with brick parapets, pergola, open carport roof and red slab, and tool crib support. Small copper motif proportions, fascia thicknesses and unmeasured sill heights are interpretations. Interior furniture, full landscape and surveyed terrain are outside this exterior completion.

## Validation

`validate_saved_asset.py` reopens the saved asset and measures actual evaluated mesh vertices. `validation.json` reports 557 asset mesh objects, evaluated bounds, transforms, source wall outline bounds, before/after height, and zero external image dependencies. There are no modifiers requiring evaluation or missing external textures. Preview cameras/lights/ground belong to a separate `Preview_samara` collection; the exported asset contains only building geometry. The exported collection offset remains zero. All geometry stays in campus world coordinates, preserving the existing direct-link contract and identity placement.

The file was rendered from southeast, northwest, top and entry views. Preview images were visually inspected. Geometry now spans approximately 5.12 m vertically including the sunken floor and cap, with upper roof 2.9083 m above entrance. Before/after actual bounds are preserved in validation; overhangs and terraces make aggregate bounds unsuitable for wall-footprint comparisons.

The master and manifest were not changed. The coordinator must inspect its existing direct collection link read-only, run the independent grader, and integrate shared indexes. Master opening/link validation is not claimed by this builder.

## Remaining uncertainty

- Campus translation ±2 m and orientation about ±3 degrees; no independent current survey georeference.
- Detailed roof plan reconstructed from site plan, floor plan and elevations rather than separately dimensioned roof survey.
- Decorative copper seed pattern is simplified; glazing panel spacing and trim dimensions are approximate.
- Original and current photo dates differ; cap uses documented 2026 state.
- Ground levels and surrounding planting are not modeled as surveyed terrain.

## Revision 2 — independent grade corrections

The initial independent score of 7.4/10 and its original inspection are retained unchanged in `iteration1/`. Three required findings were addressed in source geometry:

1. The continuous foyer wall was removed and rebuilt as piers plus sill/head pieces around three apertures. At drawing X=620,650,680 and Y=357 each opening is 8 pixels / 0.3441 m wide, between Z=0.75 and 2.42 m. Mahogany jamb and head/sill frames now surround an actual through-opening. These heights and widths are interpretations of the HABS elevation and Foundation photograph, rather than survey dimension labels.
2. The entrance-level structural slab now has a real rectangular void over the living room, with its source exterior footprint preserved as partitioned geometry. The terrace was split into exterior strips so it cannot cover the living floor. The lowered slab is exactly 22 inches / 0.5588 m below the entrance datum. Three transition treads in the foyer and dining directions follow the plan's UP marks and section's drop; tread count and depth are interpretations of drawn stair lines. The opaque low roof plane was also cut away beneath the raised public volume. A roof-hidden proof view exposes the actual lower floor, void and treads.
3. The folded fascia is now a repeated deep sheet profile spanning 0.44 m vertically, with the upper wings projecting 0.16 m from the lower edge, central facets, raised perimeter and fold ribs. The 2017 Foundation photograph supports its folded three-dimensional form. Exact motif dimensions remain photograph-derived estimates. Close renders show the depth and angled silhouette.

Fresh reopened validation and `revision2_measurements.json` document the changed objects and measurements. `preview_foyer_apertures.png`, `preview_fascia_closeup.png` and `preview_sunken_floor_roofs_hidden.png` supplement the refreshed regular views. The previous count of 557 meshes describes iteration 1; current evaluated counts are in `validation.json`.
