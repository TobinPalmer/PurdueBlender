# Haas research rebuild r03 â€” user preview before independent review

On 2026-10-28 the user reported missing front/side detail and polygon artifacts, and explicitly requested rebuilding those parts mostly from scratch using research rather than the base model. The user then requested opening the new model before independent review. This record follows that sequence.

**State: rebuilt model opened for user inspection; independent review not started. No visual grade or second-pass completion is claimed.**

## What was rebuilt

- All exported exterior meshes, wall surfaces, opening geometry, window frames/glazing, facade stonework, roof, eaves, entrance stairs and railings are newly generated. The export contains zero inherited `HAAS_Photo_*`, `HAAS_R4_*`, `HAAS_SP_West_*`, or old GIS-wall objects.
- Metric placement and wall footprint come from the official Purdue campus-map FID 233 polygon, preserved in `../sources/haas_official_footprint_fid233.json`. They are not traced from the old model. The stable collection `Asset_felix_haas_hall`, manifest origin and source asset path are preserved.
- Exterior design uses the saved Purdue front photographs and distinct Google Maps/Street View photographs listed in the parent evidence index. The front has segmental lower openings, recessed glazing, timber double doors and fanlight, a pale limestone composition with stepped brick-panel boundaries, and a 17-tread entrance flight. Side walls have separate upper groups, narrow middle openings, a broad pale basement register, stone sills/keys, brick piers, projecting eave brackets and drainage pipes.
- Each wall is a new closed polygon extrusion with genuine apertures. Frames, glazing and trim have separate depths. The former layered shell/proxy/facade stack is discarded. Two new closed hipped volumes are united once to eliminate intersecting roof surfaces.
- The previous schematic interior is preserved only in the separate hidden `HAAS_PreRebuild_SchematicInterior_Archive`, outside the exported asset collection. It did not supply exterior geometry or visual references.

## Evidence and limitations

The footprint snapshot was obtained from the official Purdue BuildingShapesZip4 service (FID 233) on 2026-10-22 and retained with provenance. It is a campus-map polygon, not a surveyed elevation. New ground-level research includes Purdue Events, Purdue Libraries' 2017 article, the 2016 elevated west photograph, and April 2026 Google Street View at University Street. The north-corner source supplies additional side-window and eave evidence.

Window dimensions, heights, roof rise, trim depth, exact door stations, and portions of the south/return-elevation schedule remain photographic estimates. The builder records those limitations per opening in `geometry_input.json`. Source coverage is incomplete for some return elevations. This is a new detailed preview for inspection, not a claim that every architectural detail is verified or that the 9.9 threshold is met.

## Technical checks and reproducibility

The original r03 scripts are preserved in `source_scripts/`; the current dedicated builders now create r04. To reproduce r03, use these archived scripts.

1. Run `python audit/felix_haas_hall/second_pass/rebuild_r03/source_scripts/prepare_felix_haas_hall_rebuild.py` from the repository root using Shapely 2.2. It produces the explicit layout and constrained wall triangulations in `geometry_input.json` without sampling old Blender geometry.
2. Run Blender with `--background --factory-startup --disable-autoexec --python audit/felix_haas_hall/second_pass/rebuild_r03/source_scripts/build_felix_haas_hall.py`. It builds a new scene/library and writes `candidate.blend` and `mesh_validation.json`.
3. The saved export contains 936 objects and 91 modeled openings. Every exported mesh was checked: no non-manifold edges or zero-area faces were found. These checks do not establish visual fidelity or prove absence of every possible geometric intersection.
4. The candidate is reopened for the same four elevations, two obliques, roof view, window close-up and entry close-up. `render_settings.json` records the exact asset hash and verifies that the source remains unchanged while the render set is generated.
5. The previous r02 library is preserved at `../revision_r02/source_before_rebuild.blend`. r02's independent reviewer stopped before a result was issued; no r02 passing grade is inferred.

Current saved SHA-256: `418caeb81fa0f29978286e03418639a0868af6ac25830aefb7e895e69604f2f6`.

The identical source library is installed at `modular/buildings/felix_haas_hall.blend`, and a user-facing copy named `Felix_Haas_Hall_rebuilt_preview.blend` was opened in Blender. Independent review is deferred until after this requested preview. No master `.blend`, manifest acceptance status, or TODO integration handoff is changed for an unaccepted candidate.
