import bpy, json, os, hashlib
from mathutils import Vector
p=bpy.data.filepath
col=bpy.data.collections.get('Asset_lambert_fieldhouse')
objs=list(col.all_objects) if col else []
meshes=[o for o in objs if o.type=='MESH']
materials={}
for m in bpy.data.materials:
    if any(m in slot.materials for slot in []): pass
for o in meshes:
    for s in o.material_slots:
        if s.material:
            materials[s.material.name]=materials.get(s.material.name,0)+1
missing=[o.name for o in meshes if not any(s.material for s in o.material_slots)]
external=[]
for im in bpy.data.images:
    if im.source=='FILE': external.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file)})
image_nodes=[]
for m in bpy.data.materials:
    if m.use_nodes and m.node_tree:
        image_nodes.extend([{'material':m.name,'image':n.image.name if n.image else None} for n in m.node_tree.nodes if n.type=='TEX_IMAGE'])
world=[]
for o in meshes:
    for c in o.bound_box:
        world.append(o.matrix_world @ Vector(c))
bounds=None
if world:
    bounds={'min':[min(v[i] for v in world) for i in range(3)],'max':[max(v[i] for v in world) for i in range(3)]}
result={'opened_path':p,'scene':bpy.context.scene.name,'collection_found':bool(col),'collection':col.name if col else None,'objects':len(objs),'types':{},'mesh_count':len(meshes),'materials_used':len(materials),'material_assignment_slots':sum(materials.values()),'unassigned_meshes':missing,'image_texture_nodes':image_nodes,'external_images':external,'bounds_world_m':bounds,'libraries':[l.filepath for l in bpy.data.libraries],'cameras':[o.name for o in bpy.data.objects if o.type=='CAMERA'],'lights':[o.name for o in bpy.data.objects if o.type=='LIGHT']}
for o in objs: result['types'][o.type]=result['types'].get(o.type,0)+1
out=os.path.join(os.path.dirname(p),'independent_grade_r8','fresh_probe.json')
with open(out,'w') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
