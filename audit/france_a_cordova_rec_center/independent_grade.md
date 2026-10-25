# Independent CREC asset review

**Score: 6.3/10 — does not meet the 8/10 pass threshold.**

| Category | Score | Review |
|---|---:|---|
| Location, footprint, and scale | 1.8/2 | The model uses Purdue GIS feature 315 and keeps the campus-world coordinate frame. Reopen validation reports an approximately 100.6 m × 192.8 m envelope and a 16 m maximum height, broadly consistent with the GIS polygon and documented multi-level facility. The source GIS bounds and modeled bounds differ by only a few metres. |
| Architectural and photo match | 1.1/2 | The long glazed east frontage, pale horizontal entry eyebrow, and adjacent brick portions refer to the available photographs. The distinctive two-to-three-storey atrium corner and pronounced high roof canopy are not clearly represented in the exterior render; the broad roof reads as a single low, uninterrupted plane and dominates the view. |
| Facade materials and detail | 0.8/2 | There are distinct glass, stone, and brick materials, window bays, mullions, and floor bands. In the supplied render, stone and roof are nearly featureless white, the brick treatment is a small pale sliver, and the glass reads as repeated opaque blue panels rather than reflective curtain wall. The photo shows stronger material contrast, finer mullions, and a much more legible atrium. |
| Supported interior and program | 0.8/2 | Courts, a pool, climbing wall, stairs, and interior floors are present in the build script and fit official descriptions of the facility. Their precise locations and floor heights are not verified by the sources, and the saved renders do not show any of them through the solid roof and perimeter walls. Treat the interior layout as schematic. |
| Modular integrity and evidence | 1.8/2 | Stable asset ID and collection are retained. Blender 5.2.3 reopened the saved file successfully; validation reports 141 collection objects, 3,852 faces, 15 assigned material names, hidden GIS reference geometry, and two saved renders. The coordinate and height uncertainty are disclosed. |
| **Total** | **6.3/10** | **Needs another revision before passing.** |

## Highest-value fixes

1. Rebuild the east atrium as the photo's dominant three-storey glazed corner, with a tall, legible projecting roof eyebrow over that zone; avoid applying the same roof expression to the full footprint.
2. Rework the roof into clearly separated GIS/orthophoto-informed wings and connectors. The current roof render is almost entirely white and does not communicate those massing steps.
3. Improve the east facade material response and contrast: warm limestone surrounds, dark bronze mullions, reflective blue-gray glass, and visibly red-brown brick wing. Re-render with a wider, lower street-level view that includes the entry, atrium, and brick transition.
4. Provide a separate cutaway or interior view showing the documented activity zones. Keep specific court, pool, climbing-wall, and stair placement labeled as schematic unless an interior plan is found.
5. Identify the Indiana imagery capture date and keep the official GIS polygon distinct from a surveyed wall line. Current evidence supports footprint better than exact facade registration.

## Evidence inspected

- Source blend: `modular/buildings/massing_france_a_c_rdova_recreational_sports_center_ae69df0.blend` (SHA-256 `ce2414aa2410bc3bccfd05d334e3fb1756dcd6a6b504cbeaad23b776b2c8df9c`).
- Builder: `modular/buildings/build_massing_france_a_c_rdova_recreational_sports_center_ae69df0.py`.
- Reopen validation: `audit/france_a_cordova_rec_center/validation.json`.
- Render evidence: `crec_east_entry.png` and `crec_roof_overview.png`.
- Source record and assets: `source_record.json`, Purdue GIS feature 315 JSON, Purdue campus imagery overlay/orthophoto, Purdue Historic Building Database and RecWell source URLs, Moody Nolan project URL, the licensed geotagged Julian Herzog photograph and metadata, and the architect east-entry photograph.

This evaluation reviewed the saved asset and supplied evidence only; it did not edit the model.
