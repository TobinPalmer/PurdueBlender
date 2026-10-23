# Hovde Hall — independent review, round 4

**Score: 7.0/10. Does not reach 9/10.** The saved asset reopens cleanly, has a recognizable long brick administration-building mass, and its latest portico is more deliberate than the prior round. The entrance still reads as a pale, flattened overlay that obscures the center of the facade; the boardroom and office are furnished display shells, not convincing interior spaces. Roof form and campus placement remain unverified.

## Inspection and file integrity

- Reopened `modular/buildings/hovde_hall.blend` in Blender 5.2.3. The scene and export collection are `Building_hovde_hall` and `Asset_hovde_hall`.
- Reopen report: 727 exported objects, 715 meshes, and zero mesh objects without material slots. The asset contains 25 reported used material names. This checks assignment/presence, not visual correctness of every shader.
- `HOVD_Root` is unchanged at `[-62.85, 93, 0]`, Z rotation `0.689754 rad` (about 39.52°), unit scale. These are the library root values, not proof of campus marker position.
- The reported shell walls are about 70.3 m long, 20.9 m deep and 16.5 m to the top wall band, excluding decorative/site geometry. This is a modeled dimension, not a verified survey measurement. Overall asset bounds include site objects and extend below ground to -4.85 m, so they should not be used as the wall footprint.
- The project manifest still records the pre-round-4 count (638 objects). The master needs a fresh link/build and contextual review before accepting these 727-object changes. The round-4 packet does not contain a current master/GIS overlay, so I cannot certify placement, orientation, or footprint fit.

## Reference comparison

- Compared the submitted neutral exterior and portico views with the dated, geotagged [2016 Wikimedia Commons exterior photograph](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg) and the winter view [Hovde Hall exterior 02](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_02.jpg). They support the red-brick wings and a prominent central classical entrance, but are perspective photographs rather than measured elevations or roof plans.
- The [West Lafayette visitor guide](https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf) also depicts a classical column-and-pediment front.
- Purdue Archives’ [Hovde Hall corporate record](https://archives.lib.purdue.edu/agents/corporate_entities/573) supports the building identity and administration-building context, not the modeled interior arrangements. The accessible source packet provides no verified floor plan for the modeled office or trustees room.

## Findings and prioritized corrections

1. **Rework the entrance-to-facade connection.** In `portico_detail_round4_verified.png`, the pale horizontal stone assembly is too broad and flat, its gold lettering intersects the stone face, and the supports read as narrow flat strips at this angle. In the wide render the assembly blocks several center windows and obscures the central brick facade. Model the columns with a clearly visible round section, bases/capitals and projection; reduce the stone panel to the sourced silhouette; make the entry opening and door legible; place lettering on a clean, readable surface. Supply a three-quarter close view that shows the assembly joining the facade and stairs.
2. **Verify the roof before adding detail.** The exterior reads as a large, nearly flat dark red-brown roof plane with a small raised cap. The available exterior photos can inform silhouette, but do not establish the exact roof profile, cap, or finish. Compare an overhead image or archival drawing if available; otherwise keep the roof restrained and identify its form/material as estimated. Avoid implying the small box is verified rooftop architecture.
3. **Make the interiors read as enclosed, usable rooms.** `presidential_office_round4_verified.png` shows a very large pink floor with only a desk/table-like central cluster and a few chairs. It does not read as the furnished executive office implied by its name. `trustees_boardroom_round4.png` has a stronger long table/chair arrangement, but large blank slab/wall areas and the exterior windows floating outside the cutaway weaken it. Define door openings, wall thickness and circulation, make furnishings fill a plausible room-scale plan, and present the cutaway without unrelated facade/window overlays. Keep both plans explicitly illustrative until a source plan supports dimensions and layouts.
4. **Improve facade and material legibility.** The deep red-brown brick and horizontal pale courses are recognizable, but the facade texture appears noisy/repetitive at close range. The blue-gray window panels read as flat overlays, and brick/stone relief is hard to judge. Add a neutral close facade view with recessed openings, visible frames/sills, restrained brick scale, and crisp beltcourse depth. Confirm the roof mesh’s assigned material in its rendered shader; material-slot presence alone does not prove a correct roof finish.
5. **Verify campus placement in the master.** Rebuild the linked master from the current library, compare structural walls—not decorative steps, lights or portico projections—to official Purdue GIS feature FID 618, and check facade orientation and neighbors in an overview. Keep the library root and manifest placement marker roles distinct. Record the footprint comparison method and residual before calling placement verified.

## Category assessment

| Area | Assessment |
|---|---|
| Identity and massing | Recognizable long, multi-storey red-brick administration building; modeled shell dimensions have not been verified against measured plans. |
| Entrance | Correct classical intent and six supports, but broad, flat, partly illegible, and poorly integrated with the window grid. |
| Facade/materials | Brick and pale courses are present; close-range texture, window depth and stone detailing need work. Slot check passes, shader accuracy is only partly established. |
| Roof | Dark red-brown, nearly flat plane and small cap; exact shape and finish are unverified. |
| Interior | Furnishings have been added to two cutaways, but the office reads as mostly empty and both layouts remain unsupported by plans. |
| Placement | Root transform is reported; current master marker/GIS overlay was not included, so placement and orientation remain unverified. |
| File integrity | Reopened successfully; expected export collection exists; 715 mesh objects have material slots. |

**Decision:** continue revisions; do not mark Hovde complete. Round 4 improves the entrance detail and room furnishings, but the exterior/facade relationship and interior usability remain below the requested 9/10 bar. The highest-impact correction is a proportionate, legible portico properly connected to the facade, followed by room-scale interiors and master/GIS placement verification.
