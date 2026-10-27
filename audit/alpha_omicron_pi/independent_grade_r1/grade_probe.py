import bpy, json, os, hashlib
from collections import Counter
from mathutils import Vector
asset_id='massing_house_970455277_a3fb72a'
scene=bpy.data.scenes.get('Building_'+asset_id)
coll=bpy.data.collections.get('Asset_'+asset_id)
assert scene is not None and coll is not None
objs=list(coll.all_objects)
# object-level geometry statistics, world bounds, material slots
mat_counts=Counter(); role_counts=Counter(); mesh_vertices=0; mesh_faces=0; empty=[]; linked=[]
for obj in objs:
    role_counts[obj.name.split('_')[0]]+=1
    if obj.type!='MESH': continue
    mesh_vertices+=len(obj.data.vertices); mesh_faces+=len(obj.data.polygons)
    if len(obj.data.polygons)==0: empty.append(obj.name)
    for slot in obj.material_slots:
        if slot.material: mat_counts[slot.material.name]+=1
    if obj.library: linked.append(obj.name)
coords=[obj.matrix_world @ v.co for obj in objs if obj.type=='MESH' for v in obj.data.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)] if coords else []
materials=[]
for m in bpy.data.materials:
    d={'name':m.name,'users':m.users,'use_nodes':m.use_nodes}
    if m.use_nodes and m.node_tree:
        nodes=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']
        if nodes:
            n=nodes[0]
            try: d['base_color']=list(n.inputs['Base Color'].default_value)
            except Exception: pass
            try: d['roughness']=float(n.inputs['Roughness'].default_value)
            except Exception: pass
    materials.append(d)
image_report=[]
for image in bpy.data.images:
    if image.source=='FILE':
        path=bpy.path.abspath(image.filepath)
        image_report.append({'name':image.name,'path':path,'exists':os.path.exists(path),'packed':bool(image.packed_file)})
# Evaluate each relevant collection with expected local origin custom property.
report={'file':bpy.data.filepath,'scene':scene.name,'collection':coll.name,'collection_object_count':len(objs),'type_counts':dict(Counter(o.type for o in objs)),'vertices':mesh_vertices,'faces':mesh_faces,'bounds_local_m':bounds,'origin_world_xy_m':list(scene.get('local_origin_world_xy_m',[])),'linked_objects':linked,'empty_meshes':empty,'material_slot_users':dict(mat_counts),'material_data':materials,'external_images':image_report,'roles':dict(role_counts),'collections':[c.name for c in bpy.data.collections if c.name.startswith('Asset_') or c.name.startswith('Building_')]}
out=os.path.join(os.path.dirname(bpy.data.filepath),'..','alpha_omicron_pi','independent_grade_r1','fresh_open_probe.json')
# Resolve report destination relative to project file (asset resides in modular/buildings).
out=os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath),'..','..','audit','alpha_omicron_pi','independent_grade_r1','fresh_open_probe.json'))
os.makedirs(os.path.dirname(out),exist_ok=True)
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
