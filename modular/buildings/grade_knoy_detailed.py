import bpy
import json
import math
from mathutils import Vector

BLEND_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend"
GIS_PATH = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\target_buildings_gis.json"

bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
scene = bpy.context.scene

print("="*80)
print("COMPREHENSIVE AUDIT OF KNOY HALL (MAURICE G. KNOY HALL OF TECHNOLOGY)")
print("="*80)

with open(GIS_PATH, "r") as f:
    gis_all = json.load(f)
gis_data = gis_all["KNOY"]

gis_poly = [Vector((p[0], p[1])) for p in gis_data["world_polygon"]]
# If closed polygon with duplicate last vertex:
if gis_poly[0] == gis_poly[-1]:
    unique_gis = gis_poly[:-1]
else:
    unique_gis = gis_poly

print(f"\n--- 1. GIS FOOTPRINT & VERTEX MATCHING ---")
print(f"GIS Raw Polygon points: {len(gis_poly)}, Unique: {len(unique_gis)}")
for i, pt in enumerate(unique_gis):
    print(f"  GIS V{i:02d}: ({pt.x:10.4f}, {pt.y:10.4f})")

wire_obj = bpy.data.objects.get("KNOY_Footprint_Reference_Wire")
walls_obj = bpy.data.objects.get("KNOY_Exterior_Masonry_Walls")

if wire_obj:
    wire_verts = [wire_obj.matrix_world @ v.co for v in wire_obj.data.vertices]
    wire_2d = [Vector((v.x, v.y)) for v in wire_verts]
    print(f"\nWire object vertices: {len(wire_verts)}")
    
    # Check 1-to-1 matching
    max_d = 0.0
    sum_d = 0.0
    for i, gp in enumerate(unique_gis):
        dists = [(gp - wp).length for wp in wire_2d]
        min_d = min(dists)
        idx = dists.index(min_d)
        sum_d += min_d
        if min_d > max_d:
            max_d = min_d
        if min_d > 0.001:
            print(f"  Warning: GIS V{i} dist to wire V{idx} is {min_d:.6f} m")
    print(f"GIS to Wire: Max deviation = {max_d:.8f} m, Avg deviation = {sum_d/len(unique_gis):.8f} m")

if walls_obj:
    wall_verts_w = [walls_obj.matrix_world @ v.co for v in walls_obj.data.vertices]
    base_verts = [v for v in wall_verts_w if abs(v.z - 0.0) < 0.05]
    base_2d = [Vector((v.x, v.y)) for v in base_verts]
    print(f"\nWalls base vertices (Z~0): {len(base_2d)}")
    max_w_d = 0.0
    sum_w_d = 0.0
    for i, gp in enumerate(unique_gis):
        dists = [(gp - wp).length for wp in base_2d]
        min_d = min(dists)
        sum_w_d += min_d
        if min_d > max_w_d:
            max_w_d = min_d
    print(f"GIS to Wall Base: Max deviation = {max_w_d:.8f} m, Avg deviation = {sum_w_d/len(unique_gis):.8f} m")

print("\n--- 2. OBJECT TRANSFORMS & ANCHORS ---")
non_ident = 0
for o in bpy.data.objects:
    loc = o.matrix_world.translation
    rot = o.matrix_world.to_euler()
    sca = o.matrix_world.to_scale()
    is_ident = (loc.length < 1e-4 and all(abs(r) < 1e-4 for r in rot) and all(abs(s-1.0) < 1e-4 for s in sca))
    if not is_ident:
        print(f"  NON-IDENTITY: {o.name} Loc={loc}, Rot={rot}, Scale={sca}")
        non_ident += 1
if non_ident == 0:
    print("  ALL objects have strict Identity world matrix [Loc=(0,0,0), Rot=(0,0,0), Scale=(1,1,1)].")

print("\n--- 3. MESH TOPOLOGY & GEOMETRY QUALITY ---")
for o in bpy.data.objects:
    if o.type == 'MESH':
        me = o.data
        # Check loose vertices (vertices not in any edge)
        edge_verts = set()
        for e in me.edges:
            edge_verts.add(e.vertices[0])
            edge_verts.add(e.vertices[1])
        loose_verts = len(me.vertices) - len(edge_verts)
        
        # Check zero-area faces
        zero_faces = sum(1 for p in me.polygons if p.area < 1e-7)
        
        # Check unassigned material polygons
        mat_slots = len(o.material_slots)
        bad_mat_faces = sum(1 for p in me.polygons if p.material_index < 0 or p.material_index >= mat_slots)
        
        print(f"  {o.name:<35}: V={len(me.vertices):<5} E={len(me.edges):<5} F={len(me.polygons):<5} | LooseV={loose_verts} ZeroF={zero_faces} BadMatF={bad_mat_faces}")

print("\n--- 4. STRUCTURAL COLUMNS AND CORE ---")
core_obj = bpy.data.objects.get("KNOY_Structural_Columns_And_Core")
if core_obj:
    verts_z = [(core_obj.matrix_world @ v.co).z for v in core_obj.data.vertices]
    verts_x = [(core_obj.matrix_world @ v.co).x for v in core_obj.data.vertices]
    verts_y = [(core_obj.matrix_world @ v.co).y for v in core_obj.data.vertices]
    print(f"  Core Object Z Range: [{min(verts_z):.3f}, {max(verts_z):.3f}] m")
    print(f"  Core Object X Range: [{min(verts_x):.3f}, {max(verts_x):.3f}] m")
    print(f"  Core Object Y Range: [{min(verts_y):.3f}, {max(verts_y):.3f}] m")

print("\n--- 5. FENESTRATION & SAWTOOTH DETAILS ---")
mullions_obj = bpy.data.objects.get("KNOY_Fenestration_Bronze_Mullions")
glass_obj = bpy.data.objects.get("KNOY_Fenestration_Ribbon_Glass")
if mullions_obj and glass_obj:
    print(f"  Mullions: {len(mullions_obj.data.vertices)} verts, {len(mullions_obj.data.polygons)} faces")
    print(f"  Ribbon Glass: {len(glass_obj.data.vertices)} verts, {len(glass_obj.data.polygons)} faces")

print("\n--- 6. ROOF ASSETS DETAILS ---")
for r_name in ["KNOY_Roof_Mechanical_Penthouse", "KNOY_Roof_Cooling_Towers", "KNOY_Roof_Solar_Photovoltaic_Array", "KNOY_Entrances_And_Canopies"]:
    ro = bpy.data.objects.get(r_name)
    if ro:
        zs = [(ro.matrix_world @ v.co).z for v in ro.data.vertices]
        xs = [(ro.matrix_world @ v.co).x for v in ro.data.vertices]
        ys = [(ro.matrix_world @ v.co).y for v in ro.data.vertices]
        print(f"  {r_name}: Z=[{min(zs):.3f}, {max(zs):.3f}] X=[{min(xs):.3f}, {max(xs):.3f}] Y=[{min(ys):.3f}, {max(ys):.3f}] | Mats={[m.name for m in ro.material_slots]}")

print("\n--- 7. MATERIAL SHADER CONFIGURATION ---")
for mat in bpy.data.materials:
    print(f"Material: {mat.name}")
    if mat.use_nodes and mat.node_tree:
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                for inp in ['Base Color', 'Metallic', 'Roughness', 'IOR', 'Transmission Weight', 'Alpha']:
                    if inp in node.inputs:
                        dv = node.inputs[inp].default_value
                        if hasattr(dv, '__len__'):
                            val_str = f"({', '.join(f'{x:.3f}' for x in dv[:3])})"
                        else:
                            val_str = f"{dv:.3f}"
                        print(f"    {inp}: {val_str}")
            elif node.type == 'EMISSION':
                col = node.inputs['Color'].default_value
                st = node.inputs['Strength'].default_value
                print(f"    Emission: Color=({col[0]:.2f}, {col[1]:.2f}, {col[2]:.2f}), Strength={st:.2f}")

print("\n--- 8. SCENE PROPERTIES & METADATA ---")
print(f"Scene Name: {scene.name}")
for k, v in scene.items():
    print(f"  Property '{k}': {repr(v)}")

print("\n--- 9. CAMERA DETAILS ---")
for c in [o for o in bpy.data.objects if o.type == 'CAMERA']:
    cam = c.data
    loc = c.location
    rot = [math.degrees(r) for r in c.rotation_euler]
    print(f"  Camera {c.name:<35}: Type={cam.type}, Focal={cam.lens if cam.type=='PERSP' else cam.ortho_scale}, Loc=({loc.x:.1f},{loc.y:.1f},{loc.z:.1f}), Rot=({rot[0]:.1f},{rot[1]:.1f},{rot[2]:.1f})")

print("="*80)
