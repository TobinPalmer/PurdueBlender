# Independent grade — Arthur G. Hansen Life Sciences Research Building

**Result: 8.00/10 — PASS**

**Frozen asset SHA-256:** `fe0bc4834a9a14f3300587fff02d75171a7a54cc25ba6a12fd99f6c44526e552`  
**Fresh-open version:** 5.2.3 LTS

## Criteria

| Criterion | Score | Evidence / limitations |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 2.00/2 | Purdue Campus GIS BuildingShapesZip4 FID 237 attributes identify HANS / Arthur G. Hansen Life Sciences Research Building at 201 S University Street. Independent fresh-open comparison of the evaluated basement slab upper perimeter against the raw FID 237 ring yields IoU 0.999998991, symmetric Hausdorff 0.0298 mm, max directed vertex distances 0.0305/0.0305 mm, and maximum bounds error 0.0264 mm. The official GIS feature is a building-shape record, not a published surveyed wall line; geometry likely shares the model source and is not an independent survey. |
| Position, orientation, and scale/dimensions | 1.80/2 | The model is stored in the expected local frame with AssetRoot at identity; its perimeter matches all 26 transformed GIS vertices and the transformed plan is 59.779 x 46.049 m. The manifest placement origin is [-288, -570] m and matches the source-register transform convention. The independent grade reopened the individual library, not the campus master; it did not freshly inspect the master Placement_hansen_life_sciences marker. The GIS CRS is geographic and uses the documented local approximation rather than survey coordinates. |
| Evidence-backed height, floors, and roof form | 1.00/2 | Purdue Archives describes a four-story building; the asset has four above-grade floor plates and a basement, which is consistent with the historical narrative and the cited 2013 emergency-plan floor list. The model has a flat roof deck, penthouse/parapet, and rooftop exhaust stacks. Purdue GIS reports six levels and vertical fields 60/67 without units/datum, conflicting with the four-story archive description and basement-plus-floors-1–4 emergency-plan list. The modeled roof deck (17.5 m), penthouse (20.572 m), and stack top (24.147 m) are unverified estimates; roof profile/mechanical elevations lack an as-built section. |
| Facade, entrances, and distinctive architecture | 1.20/2 | The saved exterior preview shows a coherent four-level research-building envelope with brick-colored wall planes, continuous horizontal glazing, pale floor bands, a stepped footprint, and a flat-roof penthouse. Purdue’s building record supports multidisciplinary laboratory use; the Purdue Events location page has a single 2022 user-posted building photo that can serve only as a visual cross-check. No authoritative multi-elevation set or as-built facade drawings were located. Window-bay rhythm, brick/precast material boundaries, exact entrance/canopy forms, and rooftop equipment placement remain weakly supported or estimated; room interiors are intentionally unmodeled/unverified. |
| Modular export, portability, and complete evidence | 2.00/2 | A separate Blender 5.2.3 process opened the exact SHA and confirmed the expected scene, collection, identity-transform root, 816 collection objects, 809 mesh objects, assigned materials, no linked libraries, and no external image dependencies. The building folder includes the raw GIS response, evidence record, source/uncertainty notes, preview, and reproducible structural-outline comparison. |

## Independent geometry measurements

- GIS/model area: 2129.129687 / 2129.129523 m².
- Intersection over union: 0.999998991.
- Symmetric Hausdorff distance: 0.0298 mm.
- Maximum axis bound difference: 0.0264 mm.
- Fresh-open asset objects: 816 total, 809 meshes; 14 assigned materials; no linked libraries or external image dependencies.

## Findings and remaining uncertainty

- PASS at 8.00/10. The plan geometry is extremely close to the cited GIS polygon, but this proves consistency with that map feature, not survey-grade wall placement.
- The four-story count has Purdue archival support; the GIS six-level/vertical-attribute fields conflict and do not document units. Roof and equipment elevations remain estimates.
- Exterior form and materials are plausible and cleanly modeled, but facade, entrance and rooftop details are not independently documented by measured elevations. No verified interior layout is included.
- Fresh-open review covered the library only; master placement-marker integration remains a coordinator-side check.

## Sources

- Purdue Campus GIS BuildingShapesZip4 FID 237: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D237&outFields=*&returnGeometry=true&outSR=4326&f=pjson
- Purdue Archives historic entity record: https://archives.lib.purdue.edu/agents/corporate_entities/692
- Purdue Events HANS location/photo page: https://events.purdue.edu/arthur_g_hansen_life_sciences_res_bldg

This review scores the frozen library only; Tobin must still validate the master placement marker during integration.
