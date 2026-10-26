import bpy, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
asset = root / 'modular/buildings/university_hall.blend'
coll = bpy.data.collections.get('Asset_university_hall')
if coll is None: raise RuntimeError('expected asset collection missing after reopen')
objs=list(coll.all_objects); meshes=[o for o in objs if o.type=='MESH']
root_obj=bpy.data.objects.get('AssetRoot_university_hall')
used={m for o in meshes for m in o.data.materials if m}
materialless=[o.name for o in meshes if not any(o.data.materials)]
invalid=[]
for o in meshes:
    for p in o.data.polygons:
        if p.material_index >= len(o.data.materials) or o.data.materials[p.material_index] is None:
            invalid.append(o.name); break
linked=[{'name':l.name,'filepath':bpy.path.abspath(l.filepath)} for l in bpy.data.libraries]
external=[]
for m in used:
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE':
                p=bpy.path.abspath(n.image.filepath)
                if not Path(p).exists() and not n.image.packed_file: external.append(p)
report={
 'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,
 'scene':bpy.context.scene.name,
 'scene_objects':len(bpy.context.scene.objects),
 'collection':coll.name,
 'objects':len(objs),
 'types':{t:sum(o.type==t for o in objs) for t in sorted({o.type for o in objs})},
 'root':None if root_obj is None else {'location':list(root_obj.location),'rotation':list(root_obj.rotation_euler),'scale':list(root_obj.scale)},
 'used_materials':len(used),'materialless_meshes':materialless,'invalid_material_indices':invalid,
 'linked_libraries':linked,'missing_external_images':external,
}
out=root/'audit/university_hall_refine/independent_reopen_r3_grade.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
