# Hovde Hall — round 8 building-side pass

## Changes

- Reduced the entrance colonnade from six to four supports, removing the two inner columns that crowded the three door openings. The remaining supports are arranged as pairs flanking the entrance; this is an interpretive adjustment because the sources reviewed do not provide a measured elevation or verify the exact support count.
- Narrowed the entablature/cornice and triangular pediment by a further 9–14% from round 7. Increased the triangular face height modestly so the pediment reads less like a broad flat cap. These dimensions remain estimated; the facade is more visible but the portico still overlaps some central window bays.
- Added an explicit “INTERPRETIVE LAYOUT | PLAN NOT SOURCE-VERIFIED” label to each oblique interior evidence image. The saved room objects retain the existing walls and furniture; only the camera-side walls and ceiling are hidden in the evidence view.
- Searched for an overhead Hovde-specific roof image or plan. The Purdue engineering webcam search result is a view from the Hovde roof toward the STEM Building, not a view of Hovde’s own roof. No usable roof reference was found, so roof profile and finish remain deferred/unverified.
- No master/manifest/placement marker/shared-script edits. `HOVD_Root` remains at `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, scale `[1,1,1]`.

## Reopen and evidence

Blender 5.2.3 reopened the saved asset for round 8 exterior/interior renders and final collection check. `final_asset_check_round8.json` reports 717 exported objects, 705 mesh objects, no unmaterialed meshes, and the unchanged root transform.

- `audit/batch3_hovde/exterior_round8.png` — full exterior with entrance visible.
- `audit/batch3_hovde/portico_detail_round8.png` — lower frontal entrance view after reducing the supports and pediment. The door leaves read more clearly; some facade windows remain obscured.
- `audit/batch3_hovde/presidential_office_cutaway_round8.png` and `trustees_boardroom_cutaway_round8.png` — three-quarter room cutaways with visible perimeter walls, furniture, and explicit interpretive labels.
- `audit/batch3_hovde/final_asset_check_round8.json` — reopened export/material/root check.
- Reproducible edit: `round8_edit.py`; render/evidence setup: `render_round8.py`.

## Evidence and remaining limits

Exterior comparison sources remain Julian Herzog's geotagged 2016-09-18 photo at 40.428660, -86.913958 (EPSG:4326), https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg; the West Lafayette visitor guide's Hovde photo, https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf; and the Purdue Archives Hovde record, https://archives.lib.purdue.edu/agents/corporate_entities/573. The latter supports the four-story administration/office identity and boardroom context, not room plans or roof construction. Official GIS snapshot: `audit/official_purdue_buildings_wgs84.json` (EPSG:4326, retrieved 2026-10-22); parent is responsible for master/GIS overlay.

**Unverified:** roof plan/profile/finish; measured portico proportions and exact column count; window schedule; interior room layouts; master placement against GIS. The four-support version is a visual test to open the entrance bay, not a source-verified reconstruction. Request independent round 8 review; no 9/10 claim.
