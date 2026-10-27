# R1 facade and roof revision

## Feedback addressed
Independent R1 score was 7.6/10. The grader reported that a March 2026 Street View panorama near 40.4209197,-86.9103025 (about 21 m west of 242 S Grant) appeared to show brick at grade, beige horizontal siding on the two upper residential levels, dark shutters, and a low-pitched/hip roof, unlike the prior all-brick upper facade and broad flat roof.

## Independent visual cross-check
- Saved panorama thumbnail: aoii_streetview_reference.jpg, direct Google Maps Street View thumbnail from pano 7sss79LqLjoubGgmBPYxng, yaw 90°, camera pin approximately 40.4209197,-86.9103025.
- The pano is on the Grant Street west side, about 22 m from the parcel footprint center. Its central house is the parcel-aligned 242 S Grant structure: official AOII house page provides the address; the OSM way footprint is at that location; and the 2015 Z-2618 report places the AOII project at Grant/Harrison and describes two residential stories atop ground-level parking.
- The pano visibly shows a dark low-pitch roof, beige horizontal siding on both upper levels, dark maroon shutters, and a brick ground-level facade with a centered street entry.
- Current official AOII house-page photos were also retrieved. They show current interior/common spaces only, not an exterior elevation; they corroborate the house identity and interior use, not exterior color.
- The city report corroborates the raised two-story residence over parking, grade-facing pedestrian access, terrace, and planter walls. It does not prescribe facade materials or roof form.

## Revisions made
- Changed both residential upper levels from red brick to warm beige horizontal lap siding; horizontal course seams are now explicit and stop at window openings.
- Added dark burgundy louvered shutters to four evenly spaced windows per floor on the Grant-facing elevation.
- Changed the grade-level street elevation to brick, added the centered entrance and three flanking windows, and removed the incorrect elevated stair/landing and upper-front entry.
- Replaced the flat roof fan with two shallow hip-roof volumes following the L-shaped building wings. The northeast terrace notch stays open.
- Fixed normalized facade opening positions being interpreted as meters, which previously clustered windows and the entry near a wall end.
- Kept the stable asset ID/path, GIS footprint, local origin, exterior placement origin, scene and collection. Left FID 756 source asset untouched.
- No shared files, master blend, or git history were modified.

## Validation
The revised blend was freshly opened in Blender 5.2.3 LTS. Three new preview renders are preview_front_west.png, preview_entry_isometric.png, and preview_terrace_aerial.png. Validation JSON and source register are alongside this note. This is an updated candidate pending a fresh independent R2 grade; do not treat it as passed until that grade is returned.
