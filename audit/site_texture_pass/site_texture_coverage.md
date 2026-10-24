# Campus site texture pass

- Site blend: `C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend`
- Updated materials: 14
- Object material assignments: 71
- Method: world-position coordinates in meters; restrained low-frequency color variation, fine grain, low-strength relief, and roughness variation. Base hues, meshes, UV maps, and layout retained.
- Added shader-only paver/brick courses and restrained concrete slab joints to corresponding surfaces; these patterns do not alter mesh geometry.
- `Manicured_Campus_Lawn` has no assigned mesh object; its source color/roughness and procedural texture are retained for future use.
- Corrected downward face winding on road asphalt, elevated sidewalks, crosswalk stripes, yellow striping, and portions of the bike-lane mesh. Targeted faces now point upward; vertex positions and layout are unchanged.
- Flat geometry proxies remain flat; no new slab, joint, or vegetation geometry was introduced.

## Material coverage

- `Purdue_Landscape_Green` (turf): 1 object(s)
- `Manicured_Campus_Lawn` (turf): 0 object(s)
- `Street_Asphalt_Dark` (asphalt): 1 object(s)
- `Plaza_Architectural_Concrete` (concrete): 2 object(s)
- `Campus_Walkway_Concrete` (concrete): 3 object(s)
- `Street_Curb_Concrete` (concrete): 1 object(s)
- `Purdue_Bike_Lane_KellyGreen` (coated asphalt): 2 object(s)
- `Plaza_Purdue_Red_Brick_Pavers` (brick paving): 2 object(s)
- `Sidewalk_Purdue_Brick_Accent` (brick paving): 1 object(s)
- `SouthHall_Purdue_Red_Brick` (brick): 1 object(s)
- `Indiana_Bedford_Limestone` (limestone): 10 object(s)
- `Beering_Bedford_Limestone` (limestone): 2 object(s)
- `Loeb_Thermal_Barre_Granite` (thermal granite): 15 object(s)
- `Loeb_Polished_Black_Granite` (polished granite): 30 object(s)

## QA renders

- `C:\Users\Tobin\Documents\Blender\PurdueMap\audit\site_texture_pass\01_turf_context.png`
- `C:\Users\Tobin\Documents\Blender\PurdueMap\audit\site_texture_pass\02_roads_sidewalk_cycletrack_context.png`
- `C:\Users\Tobin\Documents\Blender\PurdueMap\audit\site_texture_pass\03_walc_plaza_hardscape_context.png`
- `C:\Users\Tobin\Documents\Blender\PurdueMap\audit\site_texture_pass\04_engineering_fountain_paving_context.png`
