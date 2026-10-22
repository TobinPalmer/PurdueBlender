"""
Deep verification script for Maurice G. Knoy Hall of Technology (KNOY).
Measures footprint deviation, vertical elevations, transforms, and rubric criteria.
"""

import bpy
import json
import math
from mathutils import Vector

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend"
GIS_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\target_buildings_gis.json"

bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
scene = bpy.context.scene

with open(GIS_PATH, "r") as f:
    gis_data = json.load(f)["KNOY"]

gis_poly = [Vector((p[0], p[1])) for p in gis_data["world_polygon"]]
unique_gis = gis_poly[:-1] if gis_poly[0] == gis_poly[-1] else gis_poly

print("="*60)
print("1. FOOTPRINT & GEOGRAPHIC ALIGNMENT")
print("="*60)
print(f"GIS unique vertices: {len(unique_gis)}")

wire_obj = bpy.data.objects.get("KNOY_Footprint_Reference_Wire")
walls_obj = bpy.data.objects.get("KNOY_Exterior_Masonry_Walls")

if wire_obj:
    wire_verts = [wire_obj.matrix_world @ v.co for v in wire_obj.data.vertices]
    wire_2d = [Vector((v.x, v.y)) for v in wire_verts]
    max_gis_to_wire = 0.0
    for gp in unique_gis:
        d = min((gp - wp).length for wp in wire_2d)
        if d > max_gis_to_wire:
            max_gis_to_wire = d
    print(f"Wire reference vertices count: {len(wire_verts)}")
    print(f"Max deviation from GIS to Wire Vertices: {max_gis_to_wire:.6f} m")

if walls_obj:
    wall_verts_w = [walls_obj.matrix_world @ v.co for v in walls_obj.data.vertices]
    min_z = min(v.z for v in wall_verts_w)
    base_verts = [v for v in wall_verts_w if abs(v.z - min_z) < 0.1]
    base_2d = [Vector((v.x, v.y)) for v in base_verts]
    print(f"Walls total vertices: {len(wall_verts_w)}, base vertices near min_z ({min_z:.2f}m): {len(base_verts)}")
    
    max_gis_to_wall = 0.0
    sum_dist = 0.0
    for i, gp in enumerate(unique_gis):
        d = min((gp - wp).length for wp in base_2d)
        sum_dist += d
        if d > max_gis_to_wall:
            max_gis_to_wall = d
    avg_dev = sum_dist / len(unique_gis)
    print(f"GIS to Wall vertices: Max dev = {max_gis_to_wall:.6f} m, Avg dev = {avg_dev:.6f} m")
    
    wall_min_x = min(v.x for v in wall_verts_w)
    wall_max_x = max(v.x for v in wall_verts_w)
    wall_min_y = min(v.y for v in wall_verts_w)
    wall_max_y = max(v.y for v in wall_verts_w)
    
    gis_min_x = min(p.x for p in unique_gis)
    gis_max_x = max(p.x for p in unique_gis)
    gis_min_y = min(p.y for p in unique_gis)
    gis_max_y = max(p.y for p in unique_gis)
    
    print(f"Walls BBox X: [{wall_min_x:.4f}, {wall_max_x:.4f}], GIS BBox X: [{gis_min_x:.4f}, {gis_max_x:.4f}], diffs: ({wall_min_x-gis_min_x:.4f}, {wall_max_x-gis_max_x:.4f})")
    print(f"Walls BBox Y: [{wall_min_y:.4f}, {wall_max_y:.4f}], GIS BBox Y: [{gis_min_y:.4f}, {gis_max_y:.4f}], diffs: ({wall_min_y-gis_min_y:.4f}, {wall_max_y-gis_max_y:.4f})")

# Check origin shift and transforms of all objects
non_identity_transforms = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        loc = obj.matrix_world.translation
        rot = obj.matrix_world.to_euler()
        scale = obj.matrix_world.to_scale()
        if loc.length > 0.001 or any(abs(r) > 0.001 for r in rot) or any(abs(s - 1.0) > 0.001 for s in scale):
            non_identity_transforms.append((obj.name, loc, rot, scale))

print(f"Mesh objects with non-identity world matrix: {len(non_identity_transforms)}")

print("\n" + "="*60)
print("2. DIMENSIONS, ELEVATIONS & ARCHITECTURAL GEOMETRY")
print("="*60)

slabs = [obj for obj in bpy.data.objects if obj.type == 'MESH' and ("FloorSlab" in obj.name or "Deck" in obj.name or "Plaza" in obj.name)]
print("Floor slabs & decks:")
for s in sorted(slabs, key=lambda o: min(v.co.z for v in o.data.vertices)):
    verts_z = [(s.matrix_world @ v.co).z for v in s.data.vertices]
    print(f"  {s.name:<30}: Z top={max(verts_z):.3f} m, bottom={min(verts_z):.3f} m, thick={max(verts_z)-min(verts_z):.3f} m")

if walls_obj:
    wall_z = [(walls_obj.matrix_world @ v.co).z for v in walls_obj.data.vertices]
    print(f"Exterior walls Z: min={min(wall_z):.3f} m, max={max(wall_z):.3f} m, height={max(wall_z)-min(wall_z):.3f} m")

roof_objs = [o for o in bpy.data.objects if o.type == 'MESH' and any(k in o.name for k in ["Penthouse", "Cooling", "Solar", "Canop"])]
print(f"Roof & Entrance features ({len(roof_objs)}):")
for o in sorted(roof_objs, key=lambda x: x.name):
    z_coords = [(o.matrix_world @ v.co).z for v in o.data.vertices]
    print(f"  {o.name:<35}: Z min={min(z_coords):.3f} m, max={max(z_coords):.3f} m")

print("\n" + "="*60)
print("3. MATERIALS & VISIBLE DETAILS")
print("="*60)
print(f"Total materials: {len(bpy.data.materials)}")
for m in bpy.data.materials:
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        col = tuple(round(c, 2) for c in bsdf.inputs['Base Color'].default_value[:3])
        rough = round(bsdf.inputs['Roughness'].default_value, 2)
        metal = round(bsdf.inputs['Metallic'].default_value, 2)
        print(f"  {m.name:<32}: color={col}, rough={rough}, metal={metal}")
    else:
        print(f"  {m.name:<32}: (no Principled BSDF or unlit emission)")

print("\n" + "="*60)
print("4. FILE INTEGRITY, SCENE PROPERTIES & METADATA")
print("="*60)
print(f"Scene Name: {scene.name}")
print(f"Collections: {[c.name for c in bpy.data.collections]}")
print(f"Exported Collection: {bpy.data.collections.get('Asset_knoy_hall') is not None}")
print(f"Scene Custom Properties: {dict(scene.items())}")
print(f"Embedded Texts: {[t.name for t in bpy.data.texts]}")
print(f"Cameras: {[c.name for c in bpy.data.objects if c.type == 'CAMERA']}")
print("="*60)
