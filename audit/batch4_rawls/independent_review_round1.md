# Rawls Hall independent review — round 1

## Result

**Independent rating: 6.1/10.** This is a useful saved improvement pass, but the available evidence and visible detail do not support a 9/10 completion rating.

**Architectural/textural quality: 5.5/10. Placement and technical checks: 7.4/10.** I keep these separate because passing the asset and centroid checks does not make the modeled architecture or finish level complete.

| Category | Score | Review |
|---|---:|---|
| Exterior form and detail | 6.8/10 | Recognizable stepped massing, repeated floors, curved glazed bay, entrance, and roof features. The windows read mostly as flat dark panels; facade framing and roof equipment remain simplified or unverified. |
| Textures and materials | 5.5/10 | The saved brick material has a live X/Z–Y/Z projection blend controlled by absolute surface-normal X, with 0.215 m brick width and 0.075 m course height. The exterior image shows brick color, but is too wide to judge course scale and mortar. Interior walls and floor read as broad, blank white/gray surfaces, with no visible finish variation; the desk grain is subtle to the point of being hard to read. |
| Interior completeness | 5.2/10 | One eye-level classroom view shows desks, chair backs, and legs reaching the floor. The 42 desk/chair pairs appear broadly plausible for the plan's 1086 classroom group, but the render has little else to establish a finished learning space: no visible room graphics, equipment, ceiling treatment, or distinct floor finish. The 2024 first-floor plan has meaningful room boundaries and circulation beyond that room; the cutaway remains hard to compare directly and the core lacks visible fixtures. There is no reviewed upper-floor interior or atrium view. |
| Placement and technical health | 7.4/10 | Reopened the saved standalone blend in Blender 5.2.3: 721 collection objects, including 713 meshes; 42 desks and 42 chairs; identity asset root; no missing image dependencies reported. The furniture-centroid test passes 84/84, but that test alone does not establish full containment or survey accuracy. |
| Evidence and source fit | 6.7/10 | The 2024 plan is suitable for first-floor layout; the 2003 archive photo supports historical atrium context only. Maps notes disclose a nearby May 2026 Street View view and undated Airbus/Maxar satellite imagery, but no screenshot is saved, and the panorama is not a facade survey. Upper floors and many exterior details remain weakly sourced. |

Overall score is the weighted mean used for this review: exterior 30%, textures 20%, interior 30%, technical 10%, evidence 10% = **6.11/10**, rounded to **6.1/10**.

The 2003 archived atrium photo shows a strong interior palette and spatial character: ochre curved wall, pale opposing surfaces, dark flooring, wood-clad volumes, glazed rails, and bridges. The classroom render's blank white walls and light floor do not carry that visible richness. The plan supports room layout and the desk grouping, but it says little about finishes; the old photo is only historical context, so it should guide targeted verification rather than be copied as if it depicted the current classroom.

## Prioritized findings

1. **Resolve the first-floor wall-to-shell relationship.** I independently reopened the blend and screened the 196 mesh objects named `RAWL_2026_Plan...` against the ground slab polygon used in the validation. Eleven wall-object centroids fall outside that polygon. Examples include `RAWL_2026_Plan1086_02_00` at (33.76, -7.14), `RAWL_2026_Plan1054_00_00` at (14.89, -12.18), and `RAWL_2026_Plan1098_00_00` at (49.54, 6.96). Some segments may intentionally sit on the perimeter and the stated 1–2 m registration uncertainty is material; inspect these segments against the actual shell and correct any true leaks or misregistration. Centroid checks also do not test the entire wall volume.
2. **Show and complete the interior beyond room 1086.** The supplied interior render covers a single furniture room. The published plan depicts additional rooms, curved boundaries, stair/core circulation, and toilet areas; the cutaway render does not make their completeness or door connectivity easy to verify. Add source-backed core details and capture useful eye-level views through the core and other first-floor rooms. Do not infer unshown upper-floor room layouts from the first-floor plan.
3. **Establish the atrium and upper-floor interior from suitable references.** The archived 2003 image visibly shows a multi-story glazed atrium, bridges/railings, a stair, and a warm ochre wall. It is a useful historical visual reference, but it cannot certify the current configuration. Provide current or floor-specific references, then verify void shape, bridge edges, glazing, stairs, railings, and interior finishes in the model.
4. **Improve facade readability and verify roof details.** The exterior render has no obvious black apron triangles, but most windows read as dark, opaque rectangles without clear mullions or reflections. Roof blocks and the arched roof feature are visible but lack a directly comparable source image. Add facade frame/glazing detail and validate distinctive roof forms against dated imagery.
5. **Make material scale legible in close views.** The active brick graph is correctly connected to the Principled base color and bump, and its perpendicular projection logic is sound. Still, the current exterior render is not a close-up test: show both perpendicular faces near the same scale and inspect brick course continuity, mortar width, and bump strength. Give the classroom floor and walls enough source-backed material variation to read as finished interior surfaces.
6. **Strengthen placement validation.** The current checks confirm desk/chair centroids inside the GIS shell, not exact site alignment, complete object containment, or wall/door clearances. Preserve the stated approximate 1–2 m plan-registration uncertainty and use the registration overlay to audit the flagged edge segments. The saved Google Maps note is an access record rather than reproducible imagery evidence.

## Evidence inspected

- Reopened `modular/buildings/rawls_hall.blend` in background Blender 5.2.3 and inspected its saved collection/material state.
- Visually inspected `exterior_round1.png`, `interior_1086_round1.png`, and `first_floor_cutaway_round1.png`.
- Compared `plan.png` and `registration_overlay.png` to the stated layout changes.
- Inspected `checks.json`, `round1_validation.json`, `round1_model_check.json`, `round1_notes.md`, the brick graph log, and the archived image metadata.
- Source references recorded by the owner: [2024 Purdue Road School Rawls Hall first-floor plan](https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf) and [Purdue eArchives interior photograph PPBUC03065](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/3050/).

## Limits

This review does not certify exact GIS placement, current finishes, upper-floor plans, roof construction, or a current street-facing facade match. The Maps observation in the notes has no preserved screenshot, and the 2003 interior photograph should be treated as historical context. The 11 outside wall centroids are flags for review under approximate registration, not proof that all 11 walls are wrong.
