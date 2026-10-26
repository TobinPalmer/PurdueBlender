import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
asset = root / 'modular/buildings/rawls_hall.blend'
out = root / 'audit/batch4_rawls/independent_reopen_r10.json'
scene = bpy.context.scene
expected_collection = bpy.data.collections.get('Asset_rawls_hall')
root_obj = bpy.data.objects.get('AssetRoot_rawls_hall')
glass = bpy.data.objects.get('RAWL_SE_Diagonal_CurtainWall_Glass')
shell = bpy.data.objects.get('RAWL_Masonry_Exterior_Walls')
plan_wall = bpy.data.objects.get('RAWL_2026_Plan1086_02_00')
if not all([expected_collection, root_obj, glass, shell, plan_wall]):
    raise RuntimeError('Expected Rawls R10 collections/objects missing on standalone reopen')
scene_objs = list(scene.objects)
mesh_objs = [o for o in scene_objs if o.type == 'MESH']
materialless = [o.name for o in mesh_objs if not o.data.materials or all(m is None for m in o.data.materials)]
invalid_slots = []
for o in mesh_objs:
    mats = list(o.data.materials)
    if any(p.material_index >= len(mats) or mats[p.material_index] is None for p in o.data.polygons):
        invalid_slots.append(o.name)
external_image_nodes=[]
missing_images=[]
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image and node.image.source == 'FILE':
            image = node.image
            filepath = bpy.path.abspath(image.filepath)
            external_image_nodes.append({'material':mat.name,'image':image.name,'packed':bool(image.packed_file),'filepath':filepath})
            if not image.packed_file and not Path(filepath).exists():
                missing_images.append(filepath)

def evaluated_bounds(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg); me = ev.to_mesh()
    try:
        pts = [ev.matrix_world @ v.co for v in me.vertices]
        return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)] if pts else None
    finally:
        ev.to_mesh_clear()

def bvh_for(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg); me = ev.to_mesh()
    try:
        verts = [ev.matrix_world @ v.co for v in me.vertices]
        faces = [tuple(poly.vertices) for poly in me.polygons]
        return BVHTree.FromPolygons(verts, faces, all_triangles=False)
    finally:
        ev.to_mesh_clear()

glass_polys = [p for p in glass.data.polygons]
if len(glass_polys) != 44:
    raise RuntimeError(f'Expected 44 pane quads; found {len(glass_polys)}')
inward = (glass.matrix_world.to_3x3() @ glass_polys[0].normal).normalized()
shell_bvh, plan_bvh = bvh_for(shell), bvh_for(plan_wall)
def hit_count(tree, max_dist):
    clear=0; distances=[]
    for poly in glass_polys:
        pts=[glass.matrix_world @ glass.data.vertices[i].co for i in poly.vertices]
        center=sum(pts, Vector())/len(pts)
        start=center-inward*0.5
        hit, normal, face, dist=tree.ray_cast(start, inward, max_dist)
        if hit is None:
            clear += 1
        else:
            distances.append(float(dist))
    return {'clear':clear,'total':len(glass_polys),'hit_distances_m':distances}
ray_shell=hit_count(shell_bvh,1.2)
ray_room=hit_count(plan_bvh,2.0)
outliers=[]
for obj in mesh_objs:
    bounds=evaluated_bounds(obj)
    if bounds and max(abs(x) for axis in bounds[:2] for x in axis) > 120:
        outliers.append({'object':obj.name,'bounds_local_m':bounds})
classes=[o.name for o in scene_objs if '1086_R10_Schematic' in o.name]
tier_names=sorted(o.name for o in scene_objs if '1086_R10_Schematic_Tier_' in o.name)
row_desk_names=sorted(o.name for o in scene_objs if '1086' in o.name and ('Desk' in o.name or 'desk' in o.name))
report={
 'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'reopened_saved_asset':True,
 'blender_version':bpy.app.version_string,'scene':scene.name,'scene_object_count':len(scene_objs),'scene_mesh_count':len(mesh_objs),
 'export_collection':expected_collection.name,'export_collection_object_count':len(expected_collection.all_objects),
 'root_transform':{'name':root_obj.name,'location':list(root_obj.location),'rotation_euler':list(root_obj.rotation_euler),'scale':list(root_obj.scale),'matrix_world':[[float(root_obj.matrix_world[r][c]) for c in range(4)] for r in range(4)]},
 'used_material_names':sorted({m.name for o in expected_collection.all_objects if o.type=='MESH' for m in o.data.materials if m}),
 'materialless_meshes':materialless,'invalid_material_meshes':invalid_slots,'external_image_nodes':external_image_nodes,'missing_external_images':missing_images,
 'linked_libraries':[lib.filepath for lib in bpy.data.libraries],
 'bounds_outliers_over_120m':outliers,
 'southeast_glass_panes':len(glass_polys),
 'independent_ray_checks':{'exterior_shell':ray_shell,'room1086_wall':ray_room},
 'classroom_r10_objects':classes,'tier_object_names':tier_names,'tier_object_count':len(tier_names),'1086_desk_object_names_sample':row_desk_names[:60],'1086_desk_object_name_count':len(row_desk_names),
 'evaluated_shell_bounds_local_m':evaluated_bounds(shell),'evaluated_room_wall_bounds_local_m':evaluated_bounds(plan_wall),
 'limitations':['This is a standalone asset inspection; it does not verify master placement.','A ray-clear center path does not prove complete unobstructed interior visibility from every camera angle.','Room guide states 62 seats; the modeled 42 desks are a visual schematic, not a complete seat inventory.','Exact tier rise/seat dimensions, facade glazing geometry, current materials and upper-floor circulation remain unverified.']
}
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('external_image_nodes','used_material_names','1086_desk_object_names_sample')},indent=2))
