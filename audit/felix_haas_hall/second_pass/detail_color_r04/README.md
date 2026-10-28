# Haas detail and color revision r04

User-directed refinement of the research-built r03 exterior. This is a preview awaiting user inspection and independent review, not an accepted second pass. The 9.9 target is unchanged. The stable collection, GIS footprint and manifest origin are preserved; the campus master is untouched.

## Evidence checked before editing

Retrieved/inspected 2026-10-28. `../sources/user_front_detail_2026-10-28.png` is the user's supplied front photograph, capture date/photographer unknown. Cross-checked with the official [Purdue Events photograph](https://events.purdue.edu/felix_haas_hall) and the [Purdue Libraries exterior](https://blogs.lib.purdue.edu/news/2017/10/08/from-the-archives-student-recreation/). The user image gives the clearest small front details. Current Google Street View provides a separate check of side/rear material appearance and service features. Screenshots retain the provider/copyright overlays.

| Snapshot in `../sources/` | Provider/date and reproducible viewpoint | Observations / limits |
| --- | --- | --- |
| `color_west_entry_apr2026.png` | Google Street View, April 2026; [pano F4m7ya0MXAz0LkjEAIJB5g](https://www.google.com/maps/@?api=1&map_action=pano&pano=F4m7ya0MXAz0LkjEAIJB5g&heading=87&pitch=2), position 40.4269451,-86.9166441 | West rear entry, dark glazed double doors and transom, low light, retaining cheeks, white security camera, brick and stone in overcast light. Panorama stitching blurs the far right. Several views of this pano are one source, not independent photographs. |
| `color_northwest_apr2026.png` | Google Street View, April 2026; [pano 3nTpGii0zoohPRMn2y4bgA](https://www.google.com/maps/@?api=1&map_action=pano&pano=3nTpGii0zoohPRMn2y4bgA&heading=125&pitch=5), position 40.4272174,-86.9166466 | North and west corner, gray service door near north wall's west end, red alarm box, limestone belt and sill profiles. Branches screen part of the north windows. |
| `color_southwest_apr2026.png` | Google Street View, April 2026; [pano 48sbvbmDTdVRWPxu-TN8cw](https://www.google.com/maps/@?api=1&map_action=pano&pano=48sbvbmDTdVRWPxu-TN8cw&heading=65&pitch=8), position 40.4264808,-86.9166429 | Southwest corner, west and partly visible south wall, dark eaves, muted brick and pale basement. Evergreen foliage substantially hides the south wall; it does not establish a complete opening schedule. |

All photographic measurements are proportional estimates, not surveyed elevations. CRS is not applicable to ground-photo dimensions; Google coordinates specify the camera location. GIS footprint provenance remains in `../sources/haas_official_footprint_fid233.json`.

## Discrepancies addressed

- Front upper windows: change the horizontal split from the side-window pattern to approximately equal upper/lower lights visible in the supplied front photo.
- Entrance: replace portal-width timber leaves with a narrower oak door set substantially behind the arch. Add deep stone reveals, layered arch moldings, slim jamb pilasters/flutes and capitals, a shallow plaque border, and projecting flank-arch crown keys.
- Add the paired dark wall lanterns, including mounting scrolls, framed glazing, rims, hipped caps and finials.
- Add sloping solid front stair cheeks and caps, and the double molding at the basement belt.
- West rear entry: add the photographed retaining cheeks/approach, entry light, door crossbars/transom, and small security camera. Extend the triple upper-window grouping to the door bay supported by the close panorama.
- North: replace the western basement proxy with a gray service doorway and add the adjacent red alarm box.
- Materials: reduce the orange cast of brick and roof, use warmer pale limestone, more neutral olive/bronze frames and green-neutral dark glazing, and a honey-brown oak door. Reduce exaggerated masonry bump/mortar.

## Color method and limitations

Compare the front photo's sunlit and shaded stone with the overcast west and northwest panoramas, rather than copying one pixel value. Camera white balance, exposure, reflections, age, weather and shade differ. These are visually estimated material colors, not calibrated reflectance measurements or a claim of exact colorimetry. The saved library uses portable procedural shaders in scene-linear RGB; it has no downloaded texture dependencies. `material_palette.json` records the actual shader values.

The r04 render set adds a documented neutral daylight variant (white world strength 0.8, exposure +0.7) to inspect color without burying details in shadow. The r03 daylight comparison uses the same lighting/cameras. The older r03 renders used world 0.4/exposure 0, so their brightness alone must not be presented as evidence of material improvement. Render settings identify the exact asset hash and whether the source file was saved (the renderer never saves it).

## Coverage and remaining uncertainty

| Area | Supported | Still estimated/unverified |
| --- | --- | --- |
| Front | Stone/brick distribution, opening character, six-light upper groups, shallow lower arches, recessed oak door, paired lanterns and stair cheeks | Metric dimensions; exact ornamental relief and inscription. No invented readable lettering or speculative relief figure was added. |
| West | Bay rhythm, narrow middle lights, grouped uppers, rear glazed door and retaining approach, drainage and small fixtures | Metric dimensions, fine hardware and concealed lower masonry |
| North | Northwest corner, service door/alarm, window and belt character | Branch-screened windows, exact service-door width and farther-east details |
| South / pavilion returns / east wings | Oblique evidence and partial windows | Substantial vegetation and perspective conceal details; the full schedule remains incompletely verified |
| Roof | Oblique outline, dark eaves, clay-color family | Ridge heights, exact tile profile and concealed intersections |

The exact saved SHA-256 is `7c608ff383548bfb2159fba7734d4cf461813f06ab024117a7d3201d4ba045fb`. The candidate and user preview are identical and the user preview has been opened in Blender. The export has 1,035 objects and 91 modeled openings. Technical mesh validation and saved-file reopen are recorded alongside the candidate. They do not constitute independent visual scoring. The prior r01 independent score was 5.2/10, r02 review was interrupted, and neither r03 nor this changed r04 has a current independent score. The user requested opening the new model before review; independent review is deferred until after that preview.

Reproduce with the dedicated `modular/buildings/prepare_felix_haas_hall_rebuild.py` (Shapely 2.2) and then Blender `--background --python modular/buildings/build_felix_haas_hall.py`. Exact r04 source copies are retained in `source_scripts/`. Reopen the candidate using `inspect_saved.py`; use the parent `render_review.py` with tags `detail_color_r04_standard` and `detail_color_r04 --daylight` for the two render sets. Neither the renderer nor inspection script saves the library.
