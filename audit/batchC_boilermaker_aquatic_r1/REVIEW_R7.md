# Morgan J. Burke Boilermaker Aquatic Center — R7 review candidate

R6 remained at **7.9/10**. The independent review called for a visible improvement to seating, overhead lighting/truss integration, and banners. R7 responds to those points using qualitative facility photos and a building-specific lighting contractor source. It does not claim measured roof heights or campus-master placement.

## R7 changes

- Rebuilt the 288 representative spectator seats from box-like blocks as joined, extruded seat pans with slanted backs and softened edges. The seat count and layout remain schematic; Purdue's published spectator capacity is 625.
- Added 18 overhead LED diffuser housings and matching area lights in the modeled pool-hall bays. Huston Electric's project page documents Lux Dynamics Wave LED fixtures installed over the competition and diving pools. The source does not provide an as-built fixture schedule. Modeled fixture count, position, size, power, and spacing are estimates. The area-light shadows are disabled in the EEVEE preview to avoid generating many competing shadow maps.
- Added two suspended black-and-gold Purdue displays with hangers reaching the modeled lower-truss zone and correctly oriented text on both faces. Their size and placement remain photo-based presentation estimates.
- Reduced the contrast of 21 existing schematic truss meshes by changing their material to a quieter neutral painted steel. The light steel character is supported by Purdue Athletics and Arsee Engineers photos; the truss sections, spacing, and height are not measured.
- Added a review camera for the integrated pool-hall lighting and a closer north-entry approach camera.

## Evidence and limits

The [Purdue Athletics gallery](https://purduesports.exposure.co/morgan-j-burke-aquatic-center) and [Arsee Engineers project page](https://www.arsee-engineers.com/project-athletic.html) provide building-specific qualitative interior views. [Huston Electric's project page](https://hustonelectric.com/project/purdue-aquatic-center/) documents a project-specific LED installation above the competition and diving pools. [Purdue RecWell](https://www.purdue.edu/recwell/sports-and-programs/aquatics/index.php) publishes a 625-person spectator capacity; its [facility fact sheet](https://purdue.edu/recwell/visit/facility/fact-sheet.php) provides facility and mezzanine context. The [Tnemec profile](https://www.tnemec.com/documents/134/Boilermaker_Aquatic_Center_Profile.pdf) supports steel roof-deck/coating context but does not provide a roof section.

The roof profile and eave/ridge heights remain unverified. The truss geometry and dimensions remain schematic. The lighting source establishes the presence of an LED installation but not the modeled count, spacing, or as-built plan. Banner location/scale, seating arrangement, and interior circulation remain estimated. The local GIS comparison validates the shell outline only; it does not establish campus-master placement or survey accuracy. The optional site collection remains approximate and un-georeferenced.

## Validation and renders

`validation_r7.json` records a fresh reopen of the saved asset in Blender 5.2.3. The FID 896 perimeter check sampled all 70 boundary edges and 70 structural-shell segments in both directions; maximum sampled mismatch was **0.000002 m** each way. It also confirms 21 truss meshes, 288 representative molded seats, 18 fixture meshes, 18 area lights, two display panels, four outward-facing banner text objects, 12 aisle treads, 24 tier-step sections, 57 glazing panes, and 21 separate approximate context objects. All meshes have materials; there are no external image dependencies.

The renders are review previews; interior renders hide the roof and approximate site-context collection and use a neutral world background, restoring those settings before saving nothing back to the asset.

- `aquatic_r7_interior_integrated_lighting.png`
- `aquatic_r7_interior_seating_detail.png`
- `aquatic_r7_north_entry_approach.png`

The final source hash is in `asset_sha256_r7.txt`. R7 is ready for a fresh independent full-building review; no independent R7 score is claimed here.
