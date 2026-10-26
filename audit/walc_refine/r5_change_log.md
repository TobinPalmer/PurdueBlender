# WALC R5 change log

**Asset:** `modular/buildings/walc.blend`  
**R4 input SHA-256:** `01f0ba7bd8fbdee2da267e85c8d35e327cf891d68a05cbeea5876b5b692b5dd4`  
**R5 SHA-256:** `71dd7f551168b9940db616c2bdde548f4df0835a8bf496037e8100e3f0f6cd5e`

## Visual evidence and method

Reviewed Purdue's official 2018 exterior photograph from its southwest-facing oblique view, along with the R4 southwest, southeast, and north renders. The photo clearly supports broad shallow roof slopes, deep dark eaves, lower roof transitions, a prominent multi-storey glazed entry pavilion, masonry piers, and varied tall window groups. It is a perspective image, not a measured elevation. A targeted search did not find a registered roof plan or roof elevation that can establish pitch, dimensions, or absolute height. Purdue's published classroom plans describe room program, not roof geometry.

Primary reference: Purdue, [Then & Now: Wilmeth Active Learning Center](https://www.purdue.edu/newsroom/archive/purduetoday/releases/2018/Q4/then-and-now-wilmeth.html), with associated [official 2018 exterior photo](https://www.purdue.edu/uns/images/2018/pt-wilmeth-6446.jpg), inspected 2026-10-25. Program reference: Purdue, [WALC Classroom Floor Plans](https://www.purdue.edu/activelearning/walcrooms1/WALC_Classroom_FloorPlans.pdf). The cached BuildingShapesZip4 FID 906 geometry remains only the footprint/plan outline source; it was not used as roof-form evidence.

## Geometry and presentation changes

- Added four shallow image-estimated hip-roof assemblies: west and east wings, plus north and south transition masses. They replace the visually dominant flat gray presentation with sloped dark roof planes, overhangs, dark eave/soffit edges, and subtler roof transitions. The dimensions and elevations are visual estimates, not survey measurements.
- Retained the unchanged 156-vertex GIS-derived roof outline object for provenance and plan reference; it is hidden in viewport and renders so it cannot be mistaken for an architectural roof surface. Its vertices and bounds were checked after reopen.
- Added a narrow raised glazed monitor over the modeled atrium roof panels. This is a visual interpretation of the central glazed roof feature; its exact position and size are unverified by roof drawings.
- Added a tall glazed entry pavilion and bronze vertical divisions at the south-frontage entry break, below a separate lower canopy. Its broad glass proportion is guided by the official image; dimensions, mullion spacing, and height are image-estimated.
- The roof and glazing use project-local material datablocks only. The foliage library remains linked by a relative path. No external image files were added.
- Interior geometry was not changed and remains explicitly schematic. No claims are made about exact as-built interior dimensions or room placement.

## Validation and renders

A fresh Blender 5.2.3 LTS background process reopened the saved asset after the R5 save. It verified the exact hash above, the `Asset_walc` collection, 969 objects / 897 meshes, identity `AssetRoot_walc` transform, all mesh material slots, the existing relative foliage-library link, and no missing external images. Full check output: [independent_reopen_r5.json](independent_reopen_r5.json).

Four Workbench review renders were produced from the reopened asset: [eye-level southwest](eye_level_r5.png), [southwest oblique](southwest_r5.png), [southeast oblique](southeast_r5.png), and [north oblique](north_r5.png). They show the main south elevation, the tall entry pavilion, roof transitions, and north elevation. These are inspection renders, not photorealistic final imagery. The eye-level render still contains the model's simplified site pad/base and trees that appear translucent under this Workbench studio setup.

## Remaining limits for independent review

- Roof pitch, eave depth, ridge positions, height, and transition locations remain image-estimated because no surveyed roof/elevation drawing was found. The GIS polygon is not evidence for those properties.
- Compare the roof silhouette and pavilion proportions directly with the linked official photograph. The added atrium monitor is an interpretation rather than a documented as-built element.
- The existing façade still has repetitive window spacing on long elevations; R5 focused on the dominant roof and entry pavilion gaps rather than reworking every bay.
- The standalone file does not verify `Placement_walc` or alignment with neighboring campus buildings in the master scene.
- Interior is a programmatic schematic based on available public context, not a registered as-built model.

No master/shared file or README was edited. No commit was created.
