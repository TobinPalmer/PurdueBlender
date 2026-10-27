# Independent Exact-Hash Grade — Islamic Society of Greater Lafayette

**Result: 8.2/10 — meets the 8.0 threshold.** This review applies only to SHA-256 `57d4bdacd2dde6759bbc4892e153266ea0f4856368fa792179a002f5fe9f24fe`. I reopened that exact file in Blender 5.2.3 LTS; the fresh-open probe passed. See [fresh_open_probe.json](fresh_open_probe.json).

## Category scores

| Criterion | Score | Weight | Evidence and limits |
| --- | ---: | ---: | --- |
| Identity and source attribution | 7.8 | 10% | The physical-site match is supported by the labeled exterior photo and Purdue event evidence. FID 771 says “Muslim Student Association / 1021 FIRST ST.” while the current ISGL page says “1022 1st St.” The audit correctly leaves the formal crosswalk unresolved. |
| Structural footprint and placement | 9.8 | 22% | The preserved 11-point GIS wall ring matches within 0.00001437 m under the documented transform. Stable scene, collection, and building object names remain unchanged; the original campus-coordinate frame is retained. |
| Roof silhouette, floors, and height | 7.0 | 15% | The saved exterior view retains the supported intersecting hipped-roof masses. Height and roof form remain estimates. No unsupported roof-edge or opening edits were added. |
| Facade and entrance character | 7.7 | 18% | The red-brown brick, pale bands, blue-gray openings, entry surround, and small canopy remain readable. The close exterior preview now shows finer brick courses; some facade areas still look like broad modeled panels rather than a verified facade survey. |
| Materials and texturing | 8.2 | 12% | Both brick and roof use portable procedural course patterns, roughness variation, and subtle bump. The roof pattern reads as restrained slate courses in the preview. The textures are physical-scale approximations; their exact color and course dimensions are not established by the limited imagery. |
| Interior representation | 6.0 | 8% | A modest 8 m × 6 m open floor patch is clearly marked “SCHEMATIC OPEN SPACE,” and its custom properties state that it is not a verified floor plan. No partitions or named room functions are claimed. This is an honest schematic cue, not a documented interior. |
| Geometry detail and visual finish | 7.7 | 5% | The exterior render is clean and legible, and the roof-open view clearly exposes the labeled schematic patch. Overall roof shape remains broad and simple because the evidence does not justify more detail. |
| Portability, reopen, and evidence | 9.5 | 10% | Exact-hash reopen passed. No missing external images, linked libraries, or temporary preview objects were found. The parent coordinator will still need to account for the two additional schematic objects when integrating an asset currently classified as massing. |

Weighted total: **8.171/10**, reported as **8.2/10**.

## Review notes

- The audit is careful about the 1021 vs. 1022 address discrepancy and does not claim an exact formal FID crosswalk.
- The original stable structural mesh remains 982 vertices / 747 faces. The FID 771 GIS wall ring is unchanged.
- The schematic patch and its label are part of the saved asset. The roof-open image is a preview cutaway; the saved roof geometry remains present and unchanged.
- The texture nodes are procedural and the clean reopen found no external-image or linked-library dependency.

The 8.2 score passes this round's threshold. Continue to identify roof heights and detailed roof edges as estimated until stronger imagery or measured sources are available.
