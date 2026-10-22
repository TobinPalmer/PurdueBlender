import bpy
import json
import math
from mathutils import Vector, geometry

blend_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\rawls_hall.blend"
gis_path = r"C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\target_buildings_gis.json"

with open(gis_path, "r") as f:
    gis_data = json.load(f)["RAWL"]

gis_poly = [Vector((p[0], p[1])) for p in gis_data["world_polygon"]]
unique_gis = gis_poly[:-1] if gis_poly[0] == gis_poly[-1] else gis_poly

print("="*60)
print("1. FOOTPRINT & GEOGRAPHIC ALIGNMENT")
print("="*60)
print(f"GIS unique vertices: {len(unique_gis)}")

wire_obj = bpy.data.objects.get("RAWL_Footprint_Reference_Wire")
walls_obj = bpy.data.objects.get("RAWL_Masonry_Exterior_Walls")

if wire_obj:
    wire_verts = [wire_obj.matrix_world @ v.co for v in wire_obj.data.vertices]
    print(f"Wire reference vertices count: {len(wire_verts)}")
    wire_2d = [Vector((v.x, v.y)) for v in wire_verts]
    max_gis_to_wire = 0.0
    for gp in unique_gis:
        d = min((gp - wp).length for wp in wire_2d)
        if d > max_gis_to_wire:
            max_gis_to_wire = d
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

coping_obj = bpy.data.objects.get("RAWL_Limestone_Parapet_Coping")
if coping_obj:
    coping_z = [(coping_obj.matrix_world @ v.co).z for v in coping_obj.data.vertices]
    print(f"Parapet coping Z: min={min(coping_z):.3f} m, max={max(coping_z):.3f} m (Target: 79 ft = 24.079 m)")

skylight_objs = [o for o in bpy.data.objects if o.type == 'MESH' and any(k in o.name for k in ["Skylight", "Arched", "Penthouse", "Barrel", "Atrium"])]
print(f"Skylight / Atrium objects ({len(skylight_objs)}):")
for o in sorted(skylight_objs, key=lambda x: x.name):
    z_coords = [(o.matrix_world @ v.co).z for v in o.data.vertices]
    print(f"  {o.name:<35}: Z min={min(z_coords):.3f} m, max={max(z_coords):.3f} m")

max_scene_z = max(max((o.matrix_world @ v.co).z for v in o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
print(f"Scene Max Z (Roof Crest): {max_scene_z:.3f} m (Target: 102 ft = 31.090 m, Diff = {max_scene_z - 31.0896:.3f} m)")

skywalk_objs = [o for o in bpy.data.objects if o.type == 'MESH' and "Skywalk" in o.name]
print(f"Skywalk objects ({len(skywalk_objs)}):")
for o in sorted(skywalk_objs, key=lambda x: x.name):
    coords = [o.matrix_world @ v.co for v in o.data.vertices]
    x_c = [c.x for c in coords]
    y_c = [c.y for c in coords]
    z_c = [c.z for c in coords]
    print(f"  {o.name:<35}: X=[{min(x_c):.2f}, {max(x_c):.2f}] span={max(x_c)-min(x_c):.2f}m | Z=[{min(z_c):.2f}, {max(z_c):.2f}] h={max(z_c)-min(z_c):.2f}m")

rotunda_objs = [o for o in bpy.data.objects if o.type == 'MESH' and "Rotunda" in o.name]
print(f"Rotunda objects ({len(rotunda_objs)}):")
for o in sorted(rotunda_objs, key=lambda x: x.name):
    coords = [o.matrix_world @ v.co for v in o.data.vertices]
    x_c = [c.x for c in coords]
    y_c = [c.y for c in coords]
    z_c = [c.z for c in coords]
    print(f"  {o.name:<35}: X=[{min(x_c):.2f}, {max(x_c):.2f}] | Y=[{min(y_c):.2f}, {max(y_c):.2f}] | Z=[{min(z_c):.2f}, {max(z_c):.2f}]")

mech_objs = [o for o in bpy.data.objects if o.type == 'MESH' and ("Mechanical" in o.name or "HVAC" in o.name)]
print(f"Mechanical & HVAC objects ({len(mech_objs)}):")
for o in sorted(mech_objs, key=lambda x: x.name):
    coords = [o.matrix_world @ v.co for v in o.data.vertices]
    z_c = [c.z for c in coords]
    print(f"  {o.name:<35}: Z=[{min(z_c):.2f}, {max(z_c):.2f}]")

belt_objs = [o for o in bpy.data.objects if o.type == 'MESH' and "BeltCourse" in o.name]
print(f"Beltcourses ({len(belt_objs)}):")
for o in sorted(belt_objs, key=lambda x: x.name):
    z_c = [(o.matrix_world @ v.co).z for v in o.data.vertices]
    print(f"  {o.name:<35}: Z=[{min(z_c):.3f}, {max(z_c):.3f}]")

print("\n" + "="*60)
print("3. EXTERIOR MATERIALS & NODE TREES")
print("="*60)
for mat in bpy.data.materials:
    print(f"Material: {mat.name}")
    if mat.use_nodes:
        principled = None
        for n in mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                principled = n
                break
        if principled:
            bc = principled.inputs['Base Color'].default_value
            met = principled.inputs['Metallic'].default_value
            rough = principled.inputs['Roughness'].default_value
            print(f"  Principled BSDF: BaseColor=({bc[0]:.3f}, {bc[1]:.3f}, {bc[2]:.3f}, {bc[3]:.2f}), Roughness={rough:.3f}, Metallic={met:.3f}")
            bump_nodes = [n for n in mat.node_tree.nodes if n.type in ('BUMP', 'NORMAL_MAP')]
            tex_nodes = [n for n in mat.node_tree.nodes if 'TEX' in n.type]
            print(f"  Nodes count: {len(mat.node_tree.nodes)}, Bump/Normal: {[n.name for n in bump_nodes]}, Tex: {[n.name for n in tex_nodes]}")
            for inp_name in ['Transmission Weight', 'Transmission', 'Alpha', 'IOR']:
                if inp_name in principled.inputs:
                    print(f"  {inp_name}: {principled.inputs[inp_name].default_value}")
        else:
            print("  No Principled BSDF node found!")
    else:
        print("  Does not use nodes!")

print("\n" + "="*60)
print("4. INTERIOR / FLOORPLAN STRUCTURE & HONESTY")
print("="*60)
interior_objs = [o for o in bpy.data.objects if o.type == 'MESH' and any(k in o.name for k in ["FloorSlab", "Atrium", "Column", "Interior", "Room", "Wall_Int"])]
print(f"Interior / Structural objects ({len(interior_objs)}):")
for o in interior_objs:
    print(f"  {o.name}: verts={len(o.data.vertices)}, faces={len(o.data.polygons)}")

print(f"\nScene custom properties:")
for k in bpy.context.scene.keys():
    if not k.startswith("_"):
        print(f"  {k}: {bpy.context.scene[k]}")

# Also check objects custom properties
print("\nObject custom properties / documentation notes:")
for o in bpy.data.objects:
    custom_keys = [k for k in o.keys() if not k.startswith("_")]
    if custom_keys:
        print(f"  {o.name}:")
        for k in custom_keys:
            print(f"    {k} = {o[k]}")

print("\n" + "="*60)
print("5. MESH INTEGRITY & QUALITY")
print("="*60)
import bmesh
mesh_issues = []
non_manifold_summary = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        mesh = obj.data
        if len(mesh.vertices) == 0:
            mesh_issues.append((obj.name, "EMPTY MESH"))
            continue
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
        loose_verts = [v for v in bm.verts if len(v.link_edges) == 0]
        zero_area_faces = [f for f in bm.faces if f.calc_area() < 1e-6]
        
        if len(loose_verts) > 0:
            mesh_issues.append((obj.name, f"{len(loose_verts)} loose vertices"))
        if len(zero_area_faces) > 0:
            mesh_issues.append((obj.name, f"{len(zero_area_faces)} zero-area faces"))
        if len(non_manifold_edges) > 0:
            non_manifold_summary.append((obj.name, len(non_manifold_edges)))
        bm.free()

print(f"Mesh issues (loose verts / zero-area faces): {len(mesh_issues)}")
for issue in mesh_issues:
    print(f"  {issue[0]}: {issue[1]}")

print(f"Objects with boundary / non-manifold edges (normal for open sheets/curtain walls/canopies/wires): {len(non_manifold_summary)}")
for item in non_manifold_summary:
    print(f"  {item[0]}: {item[1]} open/boundary edges")
