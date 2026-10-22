import bpy
import json
import math
from mathutils import Vector
import bmesh

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend"
gis_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\target_buildings_gis.json"

with open(gis_path, "r") as f:
    gis_data = json.load(f)["RAWL"]

gis_poly = [Vector((p[0], p[1])) for p in gis_data["world_polygon"]]
unique_gis = gis_poly[:-1] if gis_poly[0] == gis_poly[-1] else gis_poly

print("="*60)
print("ATTEMPT 2 VERIFICATION: JERRY S. RAWLS HALL (RAWL)")
print("="*60)

# 1. SCENE PROPERTIES & TEXT BLOCKS
print("\n--- 1. EMBEDDED EVIDENCE & PROVENANCE ---")
print("Scene Custom Properties:")
for k in bpy.context.scene.keys():
    if not k.startswith("_"):
        print(f"  {k} = {repr(bpy.context.scene[k])}")

print("\nText Blocks in bpy.data.texts:")
for t in bpy.data.texts:
    print(f"  Found text block: '{t.name}' (lines: {len(t.lines)})")
    print("  Content preview:")
    for line in t.lines[:25]:
        print(f"    {line.body}")

# 2. BASEMENT FOUNDATION LEVEL
print("\n--- 2. BASEMENT FOUNDATION LEVEL ---")
bsmt_wall = bpy.data.objects.get("RAWL_Basement_Foundation_Walls")
bsmt_slab = bpy.data.objects.get("RAWL_FloorSlab_Basement")

if bsmt_wall:
    coords = [bsmt_wall.matrix_world @ v.co for v in bsmt_wall.data.vertices]
    z_min = min(c.z for c in coords)
    z_max = max(c.z for c in coords)
    print(f"RAWL_Basement_Foundation_Walls: Z min = {z_min:.4f} m, Z max = {z_max:.4f} m, height = {z_max - z_min:.4f} m")
    print(f"  Target: Z min = -5.486 m (-18 ft), Z max = 0.000 m. Diff Z min = {z_min - (-5.4864):.4f} m")
else:
    print("WARNING: RAWL_Basement_Foundation_Walls not found!")

if bsmt_slab:
    coords = [bsmt_slab.matrix_world @ v.co for v in bsmt_slab.data.vertices]
    z_min = min(c.z for c in coords)
    z_max = max(c.z for c in coords)
    print(f"RAWL_FloorSlab_Basement: Z min = {z_min:.4f} m, Z max = {z_max:.4f} m, thickness = {z_max - z_min:.4f} m")
    print(f"  Target top of basement slab: -5.486 m")
else:
    print("WARNING: RAWL_FloorSlab_Basement not found!")

# 3. ATRIUM SLAB OPENINGS & BALUSTRADES
print("\n--- 3. ATRIUM SLAB OPENINGS & BALUSTRADES ---")
balustrades = bpy.data.objects.get("RAWL_Atrium_Mezzanine_Balustrades")
if balustrades:
    coords = [balustrades.matrix_world @ v.co for v in balustrades.data.vertices]
    x_min, x_max = min(c.x for c in coords), max(c.x for c in coords)
    y_min, y_max = min(c.y for c in coords), max(c.y for c in coords)
    z_min, z_max = min(c.z for c in coords), max(c.z for c in coords)
    print(f"RAWL_Atrium_Mezzanine_Balustrades: verts={len(balustrades.data.vertices)}, faces={len(balustrades.data.polygons)}")
    print(f"  Bounds: X=[{x_min:.2f}, {x_max:.2f}], Y=[{y_min:.2f}, {y_max:.2f}], Z=[{z_min:.2f}, {z_max:.2f}]")
else:
    print("WARNING: RAWL_Atrium_Mezzanine_Balustrades not found!")

# Raycast down through center of atrium at (334.0, -411.0)
target_pt = Vector((334.0, -411.0, 50.0))
ray_dir = Vector((0.0, 0.0, -1.0))
print("\nVertical Raycast from (334, -411, 50) straight down through Atrium:")
for name in [
    "RAWL_Arched_Skylight_Barrel_Vault",
    "RAWL_Roof_Main_Deck",
    "RAWL_FloorSlab_L5",
    "RAWL_FloorSlab_L4",
    "RAWL_FloorSlab_L3",
    "RAWL_FloorSlab_L2",
    "RAWL_FloorSlab_L1_Ground",
    "RAWL_FloorSlab_Basement"
]:
    obj = bpy.data.objects.get(name)
    if obj:
        succ, loc, norm, idx = obj.ray_cast(target_pt, ray_dir)
        print(f"  {name:<35}: hit={succ:<5} | hit_z={loc.z if succ else 'VOID (OPEN)'}")

# 4. OVERALL BOUNDING BOX & TOTAL OBJECTS
print("\n--- 4. SCENE METRICS & MASTER COMPATIBILITY ---")
print(f"Total Objects in Asset_rawls_hall: {len(bpy.data.collections['Asset_rawls_hall'].objects)}")
all_coords = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for v in obj.data.vertices:
            w_coord = obj.matrix_world @ v.co
            all_coords.append(w_coord)

min_x = min(c.x for c in all_coords)
max_x = max(c.x for c in all_coords)
min_y = min(c.y for c in all_coords)
max_y = max(c.y for c in all_coords)
min_z = min(c.z for c in all_coords)
max_z = max(c.z for c in all_coords)
print(f"Overall BBox X: [{min_x:.3f}, {max_x:.3f}] (width: {max_x - min_x:.3f} m)")
print(f"Overall BBox Y: [{min_y:.3f}, {max_y:.3f}] (depth: {max_y - min_y:.3f} m)")
print(f"Overall BBox Z: [{min_z:.3f}, {max_z:.3f}] (total height: {max_z - min_z:.3f} m)")

# Check mesh transforms
non_id = [o.name for o in bpy.data.objects if o.type == 'MESH' and (o.location.length > 0.001 or any(abs(r) > 0.001 for r in o.rotation_euler) or any(abs(s - 1.0) > 0.001 for s in o.scale))]
print(f"Mesh objects with non-identity transform: {len(non_id)}")

# Check mesh integrity
mesh_issues = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        loose_verts = [v for v in bm.verts if len(v.link_edges) == 0]
        zero_area = [f for f in bm.faces if f.calc_area() < 1e-6]
        if loose_verts:
            mesh_issues.append((obj.name, f"{len(loose_verts)} loose verts"))
        if zero_area:
            mesh_issues.append((obj.name, f"{len(zero_area)} zero area faces"))
        bm.free()
print(f"Mesh integrity issues (loose verts / zero area faces): {len(mesh_issues)}")
for iss in mesh_issues:
    print(f"  {iss[0]}: {iss[1]}")
