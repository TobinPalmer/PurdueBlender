# Herrick Acoustics r2 builder checkpoint

Stable ID: `massing_herrick_laboratories_2138103` (historic Herrick Acoustics / HERL / FID 246; distinct from 2013 Ray W. Herrick Labs / HLAB / FID 878).

## Updates

- Retained all 66 cleaned structural vertices from Purdue BuildingShapesZip4 FID 246 in the project local campus approximation. The floor shell remains based on the source ring; no area-based scaling or smoothing was applied.
- Corrected the barn roof orientation so the broad gable faces the courtyard, matching the archival Purdue newsletter / Lab Manager exterior photos. Kept the roof pitch and elevations explicitly estimated.
- Increased wing window bay frequency to approximately 3 m, added visible mullions, pale horizontal window bands and repeated light facade piers. Expanded the entry glazing/canopy and added door mullions, threshold, and four supports.
- Reduced the qualitative wing estimate from 5.2 m to 5.0 m; eave/ridge estimates now 6.9/9.25 m. No dimensioned elevation was found. GIS `Extrution=36` is still only a possible feet value (~10.97 m), and is not treated as verified measurement.

## Area conflict assessment

The raw service response contains one closed outer ring with 67 coordinates, which cleans to 66 unique structural vertices. Its transformed local shoelace area is 2993.8066 m²; Shapely reports the polygon is valid and simple. The layer metadata labels spatial units as meters but does not explain the `Shape__Area` field semantics; its stored value is 5174.7930, 1.7285 times the transformed ring area. The discrepancy cannot be reconciled from the retained service response. The asset therefore follows the authoritative returned FID 246 ring exactly and records the attribute conflict as unresolved, rather than using the inconsistent area to resize the footprint.

## Review artifacts

- `herrick_acoustics_courtyard_preview_r2.png`: facade view for comparison with the retained photo.
- `herrick_acoustics_plan_preview_r2.png`: top-down footprint/roof view.
- `reopen_validation_r2.json`: direct reopen check of the saved asset and GIS ring.
- `reopen_validate_herrick_r2.py`: reproducible Blender inspection script.
