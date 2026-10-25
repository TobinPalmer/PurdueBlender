# Independent grade — Niswonger Aviation Technology R3

**Score: 7.8/10** (minimum pass: 8/10).
**Asset SHA-256:** `8f2bcfe7b8e6026b75d15d72185a3c01687a6df8be20a37b2f08d81b8f8159e1`

## Rubric

| Criterion | Score | Evidence and finding |
|---|---:|---|
| Identity and source-backed footprint | 1.7/2 | R3 render shows a coherent airport classroom/hangar complex with brick wings, glazed connector and attached hangar volumes. The submitted Esri z20 overhead tile shows the matching roof-zone arrangement and separate hangar mass; no source-date or georegistration metadata is provided, so this verifies qualitative identity more than metric footprint. Mesh envelope is [-50,50] x [-65.5,65.5] m, but the manifest exact-bound comparison is not an independent polygon trace. **Finding:** Identity is convincing. Exact wall footprint and roof perimeter are not independently registered to a current survey or as-built plan. |
| Position, orientation and scale | 1.9/2 | The master links Asset_niswonger_aviation_tech through Placement_niswonger_aviation_tech at (-1325,-1229.5,0), zero rotation, unit scale, matching the manifest placement origin. Local XY envelope and building origin are consistent across the asset and master record. **Finding:** Placement is internally consistent; this review lacks a survey control point proving the building's geospatial registration to sub-meter accuracy. |
| Evidence-backed height, floors and roof form | 1.3/2 | R3 now renders the previously hidden sloping connector roof and hangar roof, and adds narrow roof edges and lap cues on the two added wing tops. The orthophoto supports multiple roof zones and a service-equipment cluster, while the model still uses broad, simple planes and omits that cluster. No as-built roof plan was found; exact elevations, slope, plate perimeters and mechanical layout remain explicitly unverified. **Finding:** The major roof forms are present and legible, but the added plates remain approximate and the roof silhouette/detailing is less articulated than the aerial reference. |
| Facade, entrances and distinctive architecture | 1.6/2 | The R3 render shows long brick classroom wings, repeated glazed bays, a glazed entrance/connector and a distinctive pitched glazed volume. MSKTD photographs support the brick, metal frame, extensive glazing and visible aircraft/hangar interior, but are mostly interior views and do not validate the current exterior camera side directly. **Finding:** The signature materials and volumes are represented; exterior window/door rhythm, entrance placement and full elevations are not directly photo-matched in the submitted review views. |
| Modular export, portability and complete evidence | 1.3/2 | Fresh Blender 5.2 reopen record reports 2,313 collection objects / 2,227 meshes, no unmaterialed meshes, no missing external image dependencies, origin at zero and visible roof shells. The checked-in manifest still lists 2,300 objects and 2,300 expected names, so 13 R3 objects are not yet indexed; the master reopen record also predates the R3 2,313-object file. Evidence includes six MSKTD project photos and a local Esri imagery mosaic; the mosaic's acquisition date is unavailable. **Finding:** The asset itself is portable and material-complete, but shared manifest/master integration records are stale for this revision, and source metadata for the aerial is incomplete. |

## Required follow-up

- Score is below the 8/10 minimum.
- Manifest and master evidence are stale relative to the 2,313-object saved R3 asset.
- Roof plates need better evidence-backed articulation, and source dates/registration should be recorded if available.
- A close exterior comparison view should be added against MSKTD imagery where the facade side is identifiable.

## Primary evidence

- [MSKTD project page](https://msktd.com/project/purdue-university-niswonger-aviation-technology/) shows architect photographs and summarizes the classroom, collaborative and office program.
- [Purdue Board of Trustees Airport project PDF](https://www.purdue.edu/bot/meetings/past-meetings/2019/06.%20aug/pfc/508_Airport-HVAC-Window-Overhead-Door.pdf) confirms HVAC/window work but not roof geometry.
- Esri World Imagery tile mosaic is saved locally; tile service exposes no acquisition date in the recorded retrieval.
