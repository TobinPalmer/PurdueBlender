import bpy
import json
import math
from mathutils import Vector

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend"
gis_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\target_buildings_gis.json"

with open(gis_path, "r") as f:
    gis_data = json.load(f)["RAWL"]

gis_poly = gis_data["world_polygon"]

print("=== SCENE & COLLECTIONS ===")
for s in bpy.data.scenes:
    print(f"Scene: {s.name}")
for c in bpy.data.collections:
    print(f"Collection: {c.name}, objects: {len(c.objects)}")

print("\n=== OBJECT SUMMARY ===")
objects = bpy.data.objects
print(f"Total objects: {len(objects)}")
types = {}
for obj in objects:
    types[obj.type] = types.get(obj.type, 0) + 1
print(f"Object types: {types}")

print("\n=== OBJECT LIST & TRANSFORMS ===")
for obj in sorted(objects, key=lambda o: o.name):
    loc = obj.matrix_world.translation
    rot = obj.matrix_world.to_euler()
    scale = obj.matrix_world.to_scale()
    parent = obj.parent.name if obj.parent else "None"
    print(f"{obj.name:<35} | Type: {obj.type:<6} | Parent: {parent:<25} | Loc: ({loc.x:7.2f}, {loc.y:7.2f}, {loc.z:7.2f}) | Dim: ({obj.dimensions.x:6.2f}, {obj.dimensions.y:6.2f}, {obj.dimensions.z:6.2f})")

print("\n=== OVERALL BOUNDING BOX ===")
all_coords = []
for obj in objects:
    if obj.type == 'MESH':
        for v in obj.data.vertices:
            w_coord = obj.matrix_world @ v.co
            all_coords.append(w_coord)

if all_coords:
    min_x = min(c.x for c in all_coords)
    max_x = max(c.x for c in all_coords)
    min_y = min(c.y for c in all_coords)
    max_y = max(c.y for c in all_coords)
    min_z = min(c.z for c in all_coords)
    max_z = max(c.z for c in all_coords)
    print(f"BBox X: [{min_x:.3f}, {max_x:.3f}] (width: {max_x - min_x:.3f} m)")
    print(f"BBox Y: [{min_y:.3f}, {max_y:.3f}] (depth: {max_y - min_y:.3f} m)")
    print(f"BBox Z: [{min_z:.3f}, {max_z:.3f}] (height: {max_z - min_z:.3f} m)")

print("\n=== GIS POLYGON EXTENTS ===")
gis_x = [p[0] for p in gis_poly]
gis_y = [p[1] for p in gis_poly]
print(f"GIS X: [{min(gis_x):.3f}, {max(gis_x):.3f}] (width: {max(gis_x) - min(gis_x):.3f} m)")
print(f"GIS Y: [{min(gis_y):.3f}, {max(gis_y):.3f}] (depth: {max(gis_y) - min(gis_y):.3f} m)")
