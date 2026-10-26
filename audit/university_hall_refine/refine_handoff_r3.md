# University Hall — R3 grade handoff

**Candidate:** `modular/buildings/university_hall.blend`  
**SHA-256:** `3784451714a60a04b482c12031ac413ac5ed2c69d4b268d79f05e4816cf07f3b`  
**Fresh reopen:** passed in Blender 5.2.3 LTS. Scene `Building_university_hall`; all 1,111 objects in `Asset_university_hall`; 1,098 meshes, one curve, one empty, and 11 lights. Root `AssetRoot_university_hall` remains identity. No materialless meshes, invalid slots, linked libraries, or missing external images were found. See [independent_reopen_r3.json](independent_reopen_r3.json).

## R3 changes

- Rebuilt the roof in two pitches: steep lower mansard rise of 1.82 m and shallower upper roof rise of 2.35 m, with a visible stone break course, slate eaves, and an upper deck kept around the tower. The eave-to-break and break-to-deck runs are geometry estimates from the existing wall envelope and public photos, not measured survey dimensions.
- Replaced the prior box dormers with ten embedded east/west dormers. Their brick cheeks sink into the steep roof, front glazing stands just outside the roof face, and limestone gables and slate caps integrate into the roof silhouette.
- Reworked the belfry cap as four hipped slate planes bearing on the four brick piers, set an octagonal slate lantern and narrower spire on a stone collar, and retained the total tower elevation within the previous asset extent. Improved clock and lantern details remain schematic.
- Replaced the illustrative overlapping staircase blocks with two connected stepped flights and two landings. Column bases and capitals now meet the ground/first- and second-floor gallery slabs. Added railings on all four edges of each gallery/overlook opening.
- Strengthened the east entrance with round stone portico columns, a triangular pediment, framed double doors, and a transom. Improved slate darkness/relief and added warm limestone grain using portable procedural materials.
- Kept the existing main wall shell and manifest placement untouched. No master blend or shared file was changed.

## Fresh renders

- [Ground-level oblique](ground_oblique_r3.png)
- [East elevation](east_elevation_r3.png)
- [Entry detail](entry_ground_r3.png)
- [Architectural gallery cutaway](interior_cutaway_r3.png)

The cutaway hides the east and south viewing façades, roof, tower, portal, and exterior glazing while retaining the north and west shell, gallery floors, columns, stairs, and furnishings. It is a view aid; it does not imply that the actual building has open façades.

## Full GIS polygon comparison

Downloaded the raw `FID=213` feature as [gis_fid213_20261025.geojson](gis_fid213_20261025.geojson) on 2026-10-25. It identifies `UNIV`, University Hall, and contains a 20-vertex ring in EPSG:4326. The service does not state a survey date; its polygon is campus-map geometry, not a certified wall survey. The model side uses the four-corner outer wall ring reconstructed from the existing east/west/north/south structural wall extents, plus the manifest placement origin. This excludes roof overhangs, steps, landscaping, and decorative features.

Both rings were converted to the project's approximate local-meter frame from EPSG:4326 using `X=(longitude+86.9137) * 111412.84 * cos(radians(40.4274))` and `Y=(latitude-40.4274) * 111040`. This is a project-local approximation, not a certified projected CRS.

| Full-ring metric | Result |
| --- | ---: |
| Structural model ring area | 947.388 m² |
| GIS ring area in project approximation | 844.421 m² |
| Intersection area | 835.093 m² |
| Intersection over union | 0.872874 |
| Symmetric difference area | 121.623 m² |
| Mean symmetric boundary residual, 0.25 m sampling | 0.916 m |
| 95th percentile symmetric residual | 2.292 m |
| Maximum sampled symmetric residual | 2.470 m |

Full values and transformed vertices: [fid213_polygon_comparison_r3.json](fid213_polygon_comparison_r3.json). Visual overlay: [fid213_polygon_overlay_r3.svg](fid213_polygon_overlay_r3.svg). The GIS AABB remains close to the model shell AABB, while the ring shows longitudinal setbacks/projections that the current rectangular shell does not follow. I kept the shell unchanged because the campus-map polygon is not a surveyed wall line and the available public sources do not independently confirm those plan jogs. The model is therefore bounds-close with a measured full-ring discrepancy; it is not a verified perimeter fit.

## References and limits

- Purdue's current restoration account supports the revived two-story central gallery, recovered historic columns, and student-hub use: [Purdue Stories, June 30, 2025](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/).
- The completion account supports the two-story gallery, second-floor academy overlook, and current collaboration/classroom program: [Purdue CLA rededication, October 25, 2025](https://cla.purdue.edu/academic/history/events/stories/2025/university-hall-rededication-ceremony.html).
- Exterior silhouette and trim were compared to [Purdue CLA's University Hall steeple photograph](https://www.cla.purdue.edu/about/images/university-hall-steeple.jpg) and [Purdue Stories' 2025 exterior photograph](https://stories.purdue.edu/app/uploads/2025/06/Purdue-UniversityHall-2025_KAL_6593-NewHero.jpg).
- The Trustees' [September 28, 2022 renovation packet](https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/University%20Hall%20Related%20Renovations.pdf) predates completion; it was used only as program/design context, not as an as-built dimension source.

Gallery opening dimensions (7.6 × 12.0 m at the first gallery ring and 6.6 × 10.8 m at the overlook), room arrangement, dormer sizes/count, window spacing, interior stairs, and tower articulation remain schematic or visually estimated. Public descriptions establish a two-story gallery and recovered columns but do not publish as-built dimensions or exact column coordinates. The GIS feature's height-like attributes were not used as measured height evidence. No new independent grade is claimed; this SHA is ready for the R3 reviewer.
