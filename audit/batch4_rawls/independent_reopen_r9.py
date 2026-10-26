import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root_path = Path(__file__).resolve().parents[2]
asset_path = root_path / 'modular/buildings/rawls_hall.blend'
report_path = root_path / 'audit/batch4_rawls/independent_reopen_r9.json'
asset_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
expected_hash = '5ea4dde459d6ed6a594f49bf7c30411a6ed960124c8580e3fb7832d7f91f6910'
if asset_hash != expected_hash:
    raise RuntimeError(f'Unexpected R9 asset hash: {asset_hash}')
scene = bpy.context.scene
asset_collection = bpy.data.collections.get('Asset_rawls_hall')
root_obj = bpy.data.objects.get('AssetRoot_rawls_hall')
if asset_collection is None or root_obj is None:
    raise RuntimeError('Expected Rawls asset collection/root is missing')
objects = list(asset_collection.all_objects)
meshes = [obj for obj in objects if obj.type == 'MESH']
depsgraph = bpy.context.evaluated_depsgraph_get()
all_points = []
outliers = []
materialless = []
invalid_slots = []
for obj in meshes:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        all_points.extend(points)
        if points:
            bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
            if any(abs(v) > 120 for axis in bounds for v in axis):
                outliers.append({'object':obj.name,'bounds_local_m':bounds})
    finally:
        evaluated.to_mesh_clear()
    slots = [slot.material for slot in obj.material_slots]
    if not slots or all(material is None for material in slots):
        materialless.append(obj.name)
    if obj.data.polygons and (not slots or any(poly.material_index >= len(slots) or slots[poly.material_index] is None for poly in obj.data.polygons)):
        invalid_slots.append(obj.name)
materials = {material.name: material for obj in meshes for slot in obj.material_slots if (material := slot.material)}
external_images = []
for material in materials.values():
    if not material.use_nodes:
        continue
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image and node.image.source == 'FILE':
            filepath = bpy.path.abspath(node.image.filepath)
            external_images.append({'material':material.name,'image':node.image.name,'path':filepath,'packed':bool(node.image.packed_file),'exists':Path(filepath).exists()})
linked_libraries = [lib.filepath for lib in bpy.data.libraries if lib.filepath]
root_matrix = [[float(root_obj.matrix_world[row][col]) for col in range(4)] for row in range(4)]
root_identity = all(abs(root_matrix[r][c] - (1.0 if r == c else 0.0)) < 1e-6 for r in range(4) for c in range(4))
repair_names = [
    'Cam_RAWL_01_North_StateSt','Cam_RAWL_02_NW_Curved_Rotunda','Cam_RAWL_03_West_GrantSt_Skywalk',
    'Cam_RAWL_04_SE_Diagonal_Facade','Cam_RAWL_05_Roof_Arched_Penthouse','Cam_RAWL_06_Ortho_Footprint_Top',
    'RAWL_Site_Sidewalk_Apron','RAWL_South_Windows_South_BronzeMullions'
]
parent_inverse = {}
for name in repair_names:
    obj = bpy.data.objects.get(name)
    if obj is None:
        parent_inverse[name] = {'present':False}
    else:
        mat = [[float(obj.matrix_parent_inverse[r][c]) for c in range(4)] for r in range(4)]
        parent_inverse[name] = {'present':True,'identity':all(abs(mat[r][c]-(1.0 if r==c else 0.0))<1e-6 for r in range(4) for c in range(4)),'translation':list(obj.matrix_parent_inverse.translation)}
all_bounds = [[min(p[i] for p in all_points), max(p[i] for p in all_points)] for i in range(3)] if all_points else None
pane_obj = bpy.data.objects.get('RAWL_SE_Diagonal_CurtainWall_Glass')
glass = pane_obj
frame_obj = bpy.data.objects.get('RAWL_SE_Diagonal_CurtainWall_BronzeMullions')
wall_obj = bpy.data.objects.get('RAWL_Masonry_Exterior_Walls')
wall = wall_obj
plan_wall = bpy.data.objects.get('RAWL_2026_Plan1086_02_00')
inward = (glass.matrix_world.to_3x3() @ glass.data.polygons[0].normal).normalized()

def build_bvh(obj):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        faces = [tuple(poly.vertices) for poly in mesh.polygons]
        return BVHTree.FromPolygons(vertices, faces, all_triangles=False)
    finally:
        evaluated.to_mesh_clear()

def pane_ray_coverage(obj, distance):
    tree = build_bvh(obj)
    results = []
    for poly in glass.data.polygons:
        vertices = [glass.matrix_world @ glass.data.vertices[i].co for i in poly.vertices]
        center = sum(vertices, Vector()) / len(vertices)
        hit, normal, face_index, ray_distance = tree.ray_cast(center - inward * 0.5, inward, distance)
        results.append({'pane':poly.index,'occluded':hit is not None,'distance_m':ray_distance,'face_index':face_index})
    return results

exterior_rays = pane_ray_coverage(wall, 1.2)
plan_rays = pane_ray_coverage(plan_wall, 2.0)
result = {
    'review_target':'Rawls Hall R9 independently reopened in Blender',
    'asset_path':str(asset_path),
    'asset_sha256':asset_hash,
    'expected_sha256':expected_hash,
    'hash_matches_expected':asset_hash == expected_hash,
    'blender_version':bpy.app.version_string,
    'scene':scene.name,
    'collection':asset_collection.name,
    'collection_object_count':len(objects),
    'mesh_count':len(meshes),
    'identity_root':{'object':root_obj.name,'matrix_world':root_matrix,'identity':root_identity},
    'evaluated_asset_bounds_local_m_axis_major':all_bounds,
    'parent_inverse_repairs':parent_inverse,
    'south_east_glazing':{
        'pane_object_present':pane_obj is not None,
        'pane_faces':len(pane_obj.data.polygons) if pane_obj else None,
        'frame_object_present':frame_obj is not None,
        'frame_vertices':len(frame_obj.data.vertices) if frame_obj else None,
        'frame_faces':len(frame_obj.data.polygons) if frame_obj else None,
        'frame_bars_reported':176,
        'shell_face_count':len(wall_obj.data.polygons) if wall_obj else None,
    },
    'room1086_wall':{'present':plan_wall is not None,'face_count':len(plan_wall.data.polygons) if plan_wall else None},
    'independent_pane_ray_checks':{
        'exterior_shell_clear':sum(not row['occluded'] for row in exterior_rays),
        'exterior_shell_total':len(exterior_rays),
        'first_floor_1086_wall_clear':sum(not row['occluded'] for row in plan_rays),
        'first_floor_1086_wall_total':len(plan_rays),
        'method':'Independent Blender BVH rays from each pane center, offset 0.5 m outward, aimed inward along the saved glass plane normal; 1.2 m exterior-shell and 2.0 m plan-wall ranges.',
        'exterior_shell_occluded_panes':[row for row in exterior_rays if row['occluded']],
        'first_floor_wall_occluded_panes':[row for row in plan_rays if row['occluded']],
    },
    'materials':{'unique_used_materials':len(materials),'materialless_meshes':materialless,'invalid_material_slot_meshes':invalid_slots},
    'file_backed_image_nodes':external_images,
    'linked_libraries':linked_libraries,
    'mesh_bounds_outliers_over_120m':outliers,
    'review_limits':['This is a standalone library reopen; it does not validate the master Placement_rawls_hall marker or campus registration.','The first-floor 1086 wall openings and layout are plan-derived; plan-to-shell XY registration remains about 1 m uncertain.','No upper-floor circulation or current interior finish was independently verified.']
}
report_path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
if len(objects) != 722 or len(meshes) != 714 or not root_identity or len(pane_obj.data.polygons) != 44 or len(frame_obj.data.vertices) != 1408 or len(frame_obj.data.polygons) != 1056:
    raise RuntimeError('R9 collection/root/glazing counts differ from the expected handoff')
if materialless or invalid_slots or external_images or linked_libraries or outliers or not all(entry.get('identity') for entry in parent_inverse.values()):
    raise RuntimeError('R9 portability, material, transform or bounds check failed')
if len(exterior_rays) != 44 or any(row['occluded'] for row in exterior_rays) or len(plan_rays) != 44 or any(row['occluded'] for row in plan_rays):
    raise RuntimeError('R9 independent pane ray coverage did not clear every pane through both wall skins')
