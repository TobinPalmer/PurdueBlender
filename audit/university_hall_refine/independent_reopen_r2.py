import bpy, hashlib, json
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
asset = root_dir / 'modular/buildings/university_hall.blend'
collection = bpy.data.collections.get('Asset_university_hall')
if collection is None:
    raise RuntimeError('Asset_university_hall collection not found on fresh reopen')
objects = list(collection.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
root_obj = bpy.data.objects.get('AssetRoot_university_hall')

def bounds_for(names):
    pts=[]
    for name in names:
        o=bpy.data.objects.get(name)
        if o and o.type=='MESH':
            for v in o.data.vertices:
                pts.append(o.matrix_world @ v.co)
    if not pts: return None
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]

shell_names = ['UNIV_Wall_East_NorthSection','UNIV_Wall_East_SouthSection',
               'UNIV_Wall_East_CenterUpper','UNIV_Wall_West','UNIV_Wall_North',
               'UNIV_Wall_South']
used_mats={m.name:m for o in meshes for m in o.data.materials if m}
materialless=[o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]
invalid=[]; tex_nodes=[]; missing=[]; linked=[]
for o in meshes:
    for poly in o.data.polygons:
        if poly.material_index>=len(o.data.materials) or o.data.materials[poly.material_index] is None:
            invalid.append(o.name); break
for mat in used_mats.values():
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image:
                path=bpy.path.abspath(node.image.filepath) if node.image.source=='FILE' else None
                tex_nodes.append({'material':mat.name,'image':node.image.name,'filepath':path,'packed':bool(node.image.packed_file)})
                if node.image.source=='FILE' and path and not Path(path).exists() and not node.image.packed_file:
                    missing.append(path)
for lib in bpy.data.libraries:
    linked.append({'name':lib.name,'filepath':bpy.path.abspath(lib.filepath)})

report={
 'asset':str(asset), 'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string, 'scene':bpy.context.scene.name,
 'scene_object_count':len(bpy.context.scene.objects), 'collection':collection.name,
 'collection_object_count':len(objects), 'mesh_count':len(meshes),
 'type_counts':{t:sum(o.type==t for o in objects) for t in sorted({o.type for o in objects})},
 'root':None if root_obj is None else {'location':list(root_obj.location),'rotation':list(root_obj.rotation_euler),'scale':list(root_obj.scale)},
 'all_mesh_bounds_xyz_m':bounds_for([o.name for o in meshes]),
 'primary_wall_shell_bounds_xyz_m':bounds_for(shell_names),
 'wall_shell_objects_found':[n for n in shell_names if bpy.data.objects.get(n)],
 'selected_feature_object_counts':{
   'dormers':sum('Dormer' in o.name for o in objects),
   'tower_or_spire':sum(any(k in o.name.lower() for k in ('tower','spire','lantern','clock','finial')) for o in objects),
   'gallery_or_stair':sum(any(k in o.name.lower() for k in ('gallery','atrium','stair','overlook','column')) for o in objects),
 },
 'used_material_count':len(used_mats), 'materialless_mesh_count':len(materialless),
 'invalid_material_index_count':len(invalid), 'image_texture_nodes':tex_nodes,
 'missing_external_images':missing, 'linked_libraries':linked,
}
out=root_dir/'audit/university_hall_refine/independent_reopen_r2.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
