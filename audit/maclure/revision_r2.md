# Maclure Cooperative revision r2

Candidate asset: `modular/buildings/maclure_cooperative.blend`

Final asset SHA-256: `1215BA68BCB8E2CD466B2EFB7E498FA64A5C484ADA087A1E2FE51317F2C2CCCE`

## Changes

- Moved the west-facade entry to the right-hand/negative-Y end beside the porch stairs, added a recessed-entry surround and canopy, and cut a doorway into the west wall above the raised deck. The opening and detail dimensions are photo-informed estimates.
- Moved the porch stairs to the same end and split the porch rail to leave an access gap.
- Removed the lower-story window that occupied the entry bay; the upper window rhythm remains photo-informed.
- Corrected the garden boulder lettering to the legible `MACLURE / est. 1966` treatment and moved it next to the stair end.
- Made the estimated ground-floor, second-floor, and basement floor slabs render-visible in the saved asset. The exterior preview hides the slabs temporarily; the separate plan preview reveals the ground-floor slab, room partitions with circulation gaps, and furniture proxies.
- Preserved the official GIS FID 822 ground-level wall outline: fresh-open validation found 12 wall vertices at Z=0 and the placement origin remains `(588.724845, -56.856275)` m.

## Fresh-open checks

Opened the saved library in Blender 5.2.3 LTS and ran `audit/maclure/fresh_open_validate.py`. Passed checks: expected scene/collection and stable IDs; 12 GIS wall base vertices; recessed entry and stair objects present; all three estimated interior floors render-visible; no linked libraries; no external image dependencies. The validation captured the final asset SHA above.

Rendered fresh-open previews: `audit/maclure/maclure_exterior_preview.png` and `audit/maclure/maclure_interior_preview.png`.

## Remaining uncertainty

The GIS outline supports horizontal footprint only. The photo does not verify measured entry dimensions, facade spacing, wall/roof heights, or roof construction. Interior partitions, room layout, furniture, and all Z dimensions remain estimates; no architectural plan or measured elevation was found. This is a new candidate for an independent exact-SHA review; no revised grade is claimed here.
