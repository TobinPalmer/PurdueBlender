"""
Automated Verification Script for John W. Hicks Undergraduate Library (HIKS)
Asset: modular/buildings/hicks_library.blend
"""

import bpy
import json
import math
from mathutils import Vector

BLEND_PATH = r"modular/buildings/hicks_library.blend"
GIS_PATH = r"modular/buildings/target_buildings_gis.json"

with open(GIS_PATH, "r") as f:
    gis_poly = json.load(f)["HIKS"]["world_polygon"]

print("="*70)
print("AUDIT & VERIFICATION: JOHN W. HICKS UNDERGRADUATE LIBRARY (HIKS)")
print("="*70)

# 1. SCENE PROPERTIES & METADATA
print("\n--- 1. SCENE PROPERTIES & METADATA ---")
scene = bpy.context.scene
print(f"Scene Name: {scene.name} (Expected: Building_hicks_library)")
props = dict(scene.items())
for k, v in props.items():
    print(f"  {k}: {repr(v)}")

# 2. FILE & COLLECTION INTEGRITY
print("\n--- 2. FILE & COLLECTION INTEGRITY ---")
col_name = "Asset_hicks_library"
col = bpy.data.collections.get(col_name)
print(f"Master Collection '{col_name}' Found: {col is not None}")
if col:
    print(f"  Direct Objects: {len(col.objects)}")
    print(f"  Hierarchy Total: {len(col.all_objects)}")
    print(f"  Child Collections: {[c.name for c in col.children]}")

# 3. FOOTPRINT & GEOGRAPHIC PLACEMENT
print("\n--- 3. FOOTPRINT & GEOGRAPHIC PLACEMENT ---")
wall = bpy.data.objects.get("HIKS_Exterior_Masonry_Walls")
print(f"Exterior Wall Object: {wall.name if wall else 'MISSING'}")

if wall:
    wall_verts = [wall.matrix_world @ v.co for v in wall.data.vertices]
    xs = [v.x for v in wall_verts]
    ys = [v.y for v in wall_verts]
    zs = [v.z for v in wall_verts]
    
    print(f"Exterior Wall Bounds:")
    print(f"  X: [{min(xs):.4f}, {max(xs):.4f}] (Width: {max(xs)-min(xs):.4f} m)")
    print(f"  Y: [{min(ys):.4f}, {max(ys):.4f}] (Depth: {max(ys)-min(ys):.4f} m)")
    print(f"  Z: [{min(zs):.4f}, {max(zs):.4f}] (Height: {max(zs)-min(zs):.4f} m)")
    
    gis_xs = [p[0] for p in gis_poly]
    gis_ys = [p[1] for p in gis_poly]
    print(f"Target GIS Bounds:")
    print(f"  X: [{min(gis_xs):.4f}, {max(gis_xs):.4f}] (Width: {max(gis_xs)-min(gis_xs):.4f} m)")
    print(f"  Y: [{min(gis_ys):.4f}, {max(gis_ys):.4f}] (Depth: {max(gis_ys)-min(gis_ys):.4f} m)")
    
    dx_min = abs(min(xs) - min(gis_xs))
    dx_max = abs(max(xs) - max(gis_xs))
    dy_min = abs(min(ys) - min(gis_ys))
    dy_max = abs(max(ys) - max(gis_ys))
    print(f"Bounding Box Corner Differences:")
    print(f"  d(Xmin): {dx_min*1000:.2f} mm, d(Xmax): {dx_max*1000:.2f} mm")
    print(f"  d(Ymin): {dy_min*1000:.2f} mm, d(Ymax): {dy_max*1000:.2f} mm")
    
    # Check max point-to-point deviation across all 21 GIS vertices
    max_dev = 0.0
    for idx, gp in enumerate(gis_poly[:-1]):
        d_min = min(math.hypot(v.x - gp[0], v.y - gp[1]) for v in wall_verts)
        if d_min > max_dev:
            max_dev = d_min
    print(f"Max Vertex Deviation across all 20 unique GIS polygon vertices: {max_dev*1000:.3f} mm")

# 4. VERTICAL ELEVATIONS
print("\n--- 4. VERTICAL ELEVATIONS (OFFICIAL GIS FID 197) ---")
# Check roof peak
pyr_glass = bpy.data.objects.get("HIKS_Pyramidal_Skylights_Solar_Glazing")
pyr_frame = bpy.data.objects.get("HIKS_Pyramidal_Skylights_Bronze_Framing")
peak_z = max(max(v.co.z for v in pyr_glass.data.vertices), max(v.co.z for v in pyr_frame.data.vertices))
print(f"Pyramidal Skylight Peak Z: {peak_z:.4f} m (Target: 7.315 m / 24 ft) -> Diff: {abs(peak_z - 7.315)*1000:.2f} mm")

# Check parapet coping
coping = bpy.data.objects.get("HIKS_Limestone_Parapet_Coping_and_Base")
coping_z = max(v.co.z for v in coping.data.vertices)
print(f"Parapet Coping Peak Z: {coping_z:.4f} m (Target: 3.048 m / 10 ft) -> Diff: {abs(coping_z - 3.048)*1000:.2f} mm")

# Check roof deck
roof = bpy.data.objects.get("HIKS_Roof_Gravel_Ballast_Deck")
roof_z = min(v.co.z for v in roof.data.vertices)
print(f"Roof Deck Z: {roof_z:.4f} m (Target: 2.438 m / 8 ft) -> Diff: {abs(roof_z - 2.438)*1000:.2f} mm")

# Check ground slab
g_slab = bpy.data.objects.get("HIKS_FloorSlab_Ground_Subterranean")
g_slab_z = max(v.co.z for v in g_slab.data.vertices)
print(f"Ground Floor Slab Z: {g_slab_z:.4f} m (Target: -5.304 m / -17.4 ft) -> Diff: {abs(g_slab_z - (-5.304))*1000:.2f} mm")

# Check basement slab
b_slab = bpy.data.objects.get("HIKS_FloorSlab_Basement_Foundation")
b_slab_z = max(v.co.z for v in b_slab.data.vertices)
print(f"Basement Floor Slab Z: {b_slab_z:.4f} m (Target: -9.449 m / -31.0 ft) -> Diff: {abs(b_slab_z - (-9.449))*1000:.2f} mm")

# Check foundation wall bottom
f_walls = bpy.data.objects.get("HIKS_Subterranean_Foundation_Walls")
f_walls_z = min(v.co.z for v in f_walls.data.vertices)
print(f"Foundation Walls Bottom Z: {f_walls_z:.4f} m")

# 5. ATRIUM & CIRCULATION
print("\n--- 5. ATRIUM & CIRCULATION ---")
stairs = bpy.data.objects.get("HIKS_Central_Spiral_Staircase")
rails = bpy.data.objects.get("HIKS_Atrium_Bronze_Guardrails")
tunnel = bpy.data.objects.get("HIKS_Stewart_Center_Tunnel_Connector")
print(f"Spiral Staircase Found: {stairs is not None} (Treads & Column verts: {len(stairs.data.vertices)})")
print(f"Atrium Mezzanine Guardrails Found: {rails is not None} (Verts: {len(rails.data.vertices)})")
print(f"Stewart Center Tunnel Connector Found: {tunnel is not None} (Verts: {len(tunnel.data.vertices)})")

# 6. MATERIALS & SHADERS
print("\n--- 6. MATERIALS & SHADERS ---")
for mat in bpy.data.materials:
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    col = bsdf.inputs["Base Color"].default_value[:] if bsdf else "N/A"
    print(f"  {mat.name:<40}: BaseColor={tuple(round(c, 2) for c in col[:3])} Roughness={round(bsdf.inputs['Roughness'].default_value, 2) if bsdf else 0}")

# 7. DOCUMENTATION TEXT BLOCK
print("\n--- 7. DOCUMENTATION TEXT BLOCK ---")
for t in bpy.data.texts:
    print(f"  Text block '{t.name}': {len(t.lines)} lines")
    print(f"  Preview:\n    " + "\n    ".join(l.body for l in t.lines[:12]))

print("="*70)
print("AUDIT COMPLETE")
print("="*70)
