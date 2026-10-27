# Independent grade — West Lafayette Junior-Senior High School

**Result: 8.0/10 — passes the 8/10 project gate.**  
**Graded asset SHA-256:** `cdd11e34dbd8bf79d00949837642dac55d96e6e704a0171761c1c3cd6845b911`  
**Fresh open:** Blender 5.2.3 LTS, exact asset SHA above.  
**Rubric:** `AGENT.md`, five criteria worth two points each.

| Criterion | Score | Evidence |
|---|---:|---|
| Correct identity and source-backed footprint | 2.0/2 | OSM way 283537867 identifies the school and is corroborated by the district and NCES records. All 34 unique OSM points match the shell after the project coordinate conversion; maximum nearest-vertex error is 0.0000494 m. |
| Position, orientation, and scale/dimensions | 1.8/2 | Campus coordinates and footprint orientation follow the OSM outline. No independent survey or orthorectified source was available to validate absolute placement/dimensions beyond OSM. |
| Evidence-backed height, floors, and roof form | 1.4/2 | Three modeled levels match the OSM level tag; the broad flat roof and parapet fit the available aerial/architect imagery. Heights (10.0 m walls, 10.5 m parapet, 11.4 m rooftop equipment) are estimates, not surveyed measurements. |
| Facade, entrances, and distinctive architecture | 1.1/2 | Brick, precast bands, glazing and entry curtain wall are represented. The source photo shows a more distinctive large glass wall beside a prominent pale stone tower, with varied entry-level facade composition. The model currently reads mostly as repetitive small dark windows and simple bands. |
| Modular export, portability, and complete evidence | 1.7/2 | The saved named scene/collection reopened; 11 mesh objects, seven procedural materials, zero degenerate faces, no unpacked external image dependencies, and four previews. Builder script, raw GIS snapshot, source register and KJG photo evidence are present. No interior is modeled because no reliable floor plan was found. |

## Independent checks

The evaluation script reopened the exact `.blend` in a separate background Blender process. It confirmed the expected scene and collection, all 34 OSM vertices within tolerance, no zero-area mesh faces, no unpacked file textures, and four existing review renders. Script output is saved at [geometry_validation.json](geometry_validation.json); the structured score is in [result.json](result.json).

I visually compared the aerial/east/south/northwest renders with the saved KJG exterior photograph `sources/kjg_images/1ef8ff260e0c444887bfb229d99c1537.jpg` and the KJG contact sheet. The dominant remaining accuracy gap is the facade composition: better elevation-aligned reference views should guide a larger curtain wall and its adjacent pale tower, along with the brick/glazing proportions around the entrance. The building passes the numeric gate, but these details remain clear opportunities to improve the visual match.
