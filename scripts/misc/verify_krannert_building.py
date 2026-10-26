"""
Deep Verification Script for Krannert Building (KRAN) Asset
Checks all 5 Project Grading Rubric Criteria
"""

import bpy
import bmesh
import json
import math
from mathutils import Vector

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\krannert_building.blend"
GIS_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\target_buildings_gis.json"

with open(GIS_PATH, "r") as f:
    gis_data = json.load(f)["KRAN"]

gis_poly = [Vector((p[0], p[1])) for p in gis_data["world_polygon"]]
unique_gis = gis_poly[:-1] if (gis_poly[0] - gis_poly[-1]).length < 0.001 else gis_poly

print("="*70)
print("KRANNERT BUILDING (KRAN) - COMPREHENSIVE VERIFICATION AUDIT")
print("="*70)

# -----------------------------------------------------------------------------
# 1. SCENE PROPERTIES & MASTER COMPATIBILITY
# -----------------------------------------------------------------------------
print("\n--- 1. SCENE PROPERTIES & MASTER COMPATIBILITY ---")
scene = bpy.context.scene
print(f"Scene Name: {scene.name} (Expected: Building_krannert_building)")
assert scene.name == "Building_krannert_building", "Scene name mismatch!"

assert "Asset_krannert_building" in bpy.data.collections, "Asset collection missing!"
asset_col = bpy.data.collections["Asset_krannert_building"]
print(f"Asset Collection: {asset_col.name} with {len(asset_col.objects)} objects")

print("Custom Properties:")
for k in scene.keys():
    if not k.startswith("_"):
        print(f"  {k} = {repr(scene[k])}")

# -----------------------------------------------------------------------------
# 2. FOOTPRINT & GEOGRAPHIC ALIGNMENT
# -----------------------------------------------------------------------------
print("\n--- 2. FOOTPRINT & GEOGRAPHIC ALIGNMENT ---")
print(f"Official GIS unique vertices: {len(unique_gis)}")

wire_obj = bpy.data.objects.get("KRAN_Footprint_Reference_Wire")
walls_obj = bpy.data.objects.get("KRAN_Exterior_Masonry_Walls")

if wire_obj:
    wire_verts = [wire_obj.matrix_world @ v.co for v in wire_obj.data.vertices]
    wire_2d = [Vector((v.x, v.y)) for v in wire_verts]
    max_gis_to_wire = max(min((gp - wp).length for wp in wire_2d) for gp in unique_gis)
    print(f"Wire Reference Object: {len(wire_verts)} verts | Max deviation from GIS: {max_gis_to_wire:.6f} m")

if walls_obj:
    wall_verts_w = [walls_obj.matrix_world @ v.co for v in walls_obj.data.vertices]
    base_verts = [v for v in wall_verts_w if abs(v.z - 0.0) < 0.1]
    base_2d = [Vector((v.x, v.y)) for v in base_verts]
    max_gis_to_wall = max(min((gp - wp).length for wp in base_2d) for gp in unique_gis)
    avg_gis_to_wall = sum(min((gp - wp).length for wp in base_2d) for gp in unique_gis) / len(unique_gis)
    print(f"Exterior Walls Base: {len(base_verts)} base verts | Max dev: {max_gis_to_wall:.6f} m | Avg dev: {avg_gis_to_wall:.6f} m")
    
    wall_min_x = min(v.x for v in wall_verts_w)
    wall_max_x = max(v.x for v in wall_verts_w)
    wall_min_y = min(v.y for v in wall_verts_w)
    wall_max_y = max(v.y for v in wall_verts_w)
    
    gis_min_x = min(p.x for p in unique_gis)
    gis_max_x = max(p.x for p in unique_gis)
    gis_min_y = min(p.y for p in unique_gis)
    gis_max_y = max(p.y for p in unique_gis)
    
    print(f"Walls BBox X: [{wall_min_x:.3f}, {wall_max_x:.3f}] (diff: {abs(wall_min_x - gis_min_x):.4f}, {abs(wall_max_x - gis_max_x):.4f})")
    print(f"Walls BBox Y: [{wall_min_y:.3f}, {wall_max_y:.3f}] (diff: {abs(wall_min_y - gis_min_y):.4f}, {abs(wall_max_y - gis_max_y):.4f})")

# Check object transforms
non_identity = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        if obj.location.length > 0.001 or any(abs(r) > 0.001 for r in obj.rotation_euler) or any(abs(s - 1.0) > 0.001 for s in obj.scale):
            non_identity.append(obj.name)
print(f"Mesh objects with non-identity transform: {len(non_identity)}")

# -----------------------------------------------------------------------------
# 3. DIMENSIONS & VERTICAL ELEVATIONS
# -----------------------------------------------------------------------------
print("\n--- 3. DIMENSIONS & VERTICAL ELEVATIONS ---")
slabs = [o for o in bpy.data.objects if o.type == 'MESH' and "FloorSlab" in o.name]
print(f"Total floor slabs: {len(slabs)}")
for s in sorted(slabs, key=lambda o: max(v.co.z for v in o.data.vertices)):
    z_coords = [(s.matrix_world @ v.co).z for v in s.data.vertices]
    print(f"  {s.name:<28}: top Z={max(z_coords):.3f} m, bot Z={min(z_coords):.3f} m")

coping = bpy.data.objects.get("KRAN_Limestone_Parapet_Coping")
if coping:
    z_c = [(coping.matrix_world @ v.co).z for v in coping.data.vertices]
    print(f"Parapet Coping Z: min={min(z_c):.3f} m, max={max(z_c):.3f} m (Target: 32.918 m / 108 ft)")

penthouse = bpy.data.objects.get("KRAN_Rooftop_Mechanical_Penthouse")
if penthouse:
    z_p = [(penthouse.matrix_world @ v.co).z for v in penthouse.data.vertices]
    print(f"Penthouse Z: min={min(z_p):.3f} m, max={max(z_p):.3f} m (Target: 35.662 m / 117 ft)")

all_coords = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for v in obj.data.vertices:
            all_coords.append(obj.matrix_world @ v.co)
print(f"Overall Building Height: {max(c.z for c in all_coords) - min(c.z for c in all_coords if c.z >= 0.0):.3f} m above grade")
print(f"Subterranean Foundation Depth: {abs(min(c.z for c in all_coords)):.3f} m below grade")

# -----------------------------------------------------------------------------
# 4. MATERIALS & SHADERS
# -----------------------------------------------------------------------------
print("\n--- 4. EXTERIOR MATERIALS & NODE TREES ---")
for mat in bpy.data.materials:
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if mat.use_nodes else None
    if bsdf:
        bc = bsdf.inputs["Base Color"].default_value
        rough = bsdf.inputs["Roughness"].default_value
        met = bsdf.inputs["Metallic"].default_value
        print(f"  {mat.name:<30}: Color=({bc[0]:.2f}, {bc[1]:.2f}, {bc[2]:.2f}), Rough={rough:.2f}, Met={met:.2f}")

# -----------------------------------------------------------------------------
# 5. MESH INTEGRITY AUDIT
# -----------------------------------------------------------------------------
print("\n--- 5. MESH INTEGRITY AUDIT ---")
issues = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        loose = [v for v in bm.verts if len(v.link_edges) == 0]
        zero_area = [f for f in bm.faces if f.calc_area() < 1e-6]
        if loose:
            issues.append(f"{obj.name}: {len(loose)} loose vertices")
        if zero_area:
            issues.append(f"{obj.name}: {len(zero_area)} zero-area faces")
        bm.free()

print(f"Mesh issues detected: {len(issues)}")
for iss in issues:
    print(f"  {iss}")

# -----------------------------------------------------------------------------
# 6. EVIDENCE TEXT BLOCK
# -----------------------------------------------------------------------------
print("\n--- 6. EVIDENCE & INTERIOR DOCUMENTATION ---")
txt = bpy.data.texts.get("EVIDENCE_AND_INTERIOR_NOTES.txt")
if txt:
    print(f"Found EVIDENCE_AND_INTERIOR_NOTES.txt with {len(txt.lines)} lines")
else:
    print("ERROR: EVIDENCE_AND_INTERIOR_NOTES.txt NOT FOUND!")

print("\n=== VERIFICATION AUDIT COMPLETE ===")
