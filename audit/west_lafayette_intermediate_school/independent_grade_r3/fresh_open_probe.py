import bpy, json, os, hashlib
p = bpy.data.filepath
h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
expected_scene = 'Building_massing_west_lafayette_intermediate_school_d72f0fa'
expected_collection = 'Asset_massing_west_lafayette_intermediate_school_d72f0fa'
scene = bpy.data.scenes.get(expected_scene)
coll = bpy.data.collections.get(expected_collection)
objs = list(coll.all_objects) if coll else []
mesh_objs = [o for o in objs if o.type == 'MESH']
features = {}
for token in ('Classroom', 'room', 'Roof', 'roof', 'Entry', 'entry', 'Canopy', 'canopy', 'Gym', 'gym', 'Clerestory', 'classroom_center'):
    features[token] = [o.name for o in objs if token in o.name][:40]
materials = sorted({m.name for o in objs if o.type == 'MESH' for m in o.data.materials if m})
images = [{'name': im.name, 'filepath': im.filepath, 'packed': bool(im.packed_file)} for im in bpy.data.images]
# evaluated world-space bounds over all mesh vertices
from mathutils import Vector
lo = [float('inf')]*3; hi = [float('-inf')]*3
dg = bpy.context.evaluated_depsgraph_get()
for o in mesh_objs:
    eo = o.evaluated_get(dg)
    me = eo.to_mesh()
    try:
        for v in me.vertices:
            q = eo.matrix_world @ v.co
            for i in range(3): lo[i]=min(lo[i],q[i]); hi[i]=max(hi[i],q[i])
    finally: eo.to_mesh_clear()
result = {'fresh_open': True, 'blender_version': bpy.app.version_string, 'asset_path': p, 'asset_sha256': h, 'scene_found': bool(scene), 'collection_found': bool(coll), 'collection_is_scene_linked': bool(coll and scene and coll in scene.collection.children_recursive), 'object_count': len(objs), 'mesh_object_count': len(mesh_objs), 'mesh_vertex_count': sum(len(o.data.vertices) for o in mesh_objs), 'mesh_polygon_count': sum(len(o.data.polygons) for o in mesh_objs), 'world_bounds_mesh_m': [lo,hi], 'collections': sorted(c.name for c in bpy.data.collections if c.name.startswith('WLIS_')), 'material_names': materials, 'image_dependencies': images, 'feature_name_samples': features}
print('INDEPENDENT_PROBE_JSON=' + json.dumps(result, separators=(',', ':')))
with open(os.environ['WLI_GRADER_OUT'], 'w', encoding='utf-8') as f: json.dump(result,f,indent=2)
