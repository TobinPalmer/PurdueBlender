import bpy, json, hashlib, os
from mathutils import Vector
p = bpy.data.filepath
asset = 'massing_yue_kong_pao_hall_a3cb766'
coll_name = 'Asset_' + asset
coll = bpy.data.collections.get(coll_name)
objs = list(coll.all_objects) if coll else []
mesh_objs = [o for o in objs if o.type == 'MESH']
mat_names = sorted({m.name for o in mesh_objs for m in o.data.materials if m})
missing_mats = [o.name for o in mesh_objs if not any(m for m in o.data.materials)]
image_nodes=[]
for m in bpy.data.materials:
    if m.name in mat_names and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE': image_nodes.append({'material':m.name,'image':n.image.name if n.image else None,'filepath':n.image.filepath if n.image else None,'packed':bool(n.image and n.image.packed_file)})
verts=[]
for o in mesh_objs:
    deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh()
    for v in me.vertices:
        w=o.matrix_world @ v.co
        verts.append((w.x,w.y,w.z))
    ev.to_mesh_clear()
mins=[min(v[i] for v in verts) for i in range(3)] if verts else []
maxs=[max(v[i] for v in verts) for i in range(3)] if verts else []
# root/collection overview and text labels
out={'file':p,'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'scene':bpy.context.scene.name,'collection_found':bool(coll),'collection':coll_name,'collection_object_count':len(objs),'mesh_count':len(mesh_objs),'nonmesh_count':len(objs)-len(mesh_objs),'vertex_count':sum(len(o.data.vertices) for o in mesh_objs),'face_count':sum(len(o.data.polygons) for o in mesh_objs),'materials':mat_names,'material_count':len(mat_names),'materialless_meshes':missing_mats,'image_nodes':image_nodes,'bounds_world_xyz':[[mins[i],maxs[i]] for i in range(3)],'direct_scene_link_objects':sorted(o.name for o in bpy.context.scene.objects if o.name in {x.name for x in objs}),'top_objects':sorted(o.name for o in objs if o.parent is None),'objects':[]}
for o in sorted(objs,key=lambda x:x.name):
    if o.type=='MESH':
        bb=[o.matrix_world @ Vector(c) for c in o.bound_box]
        bounds=[[min(v[i] for v in bb),max(v[i] for v in bb)] for i in range(3)]
        out['objects'].append({'name':o.name,'type':o.type,'bounds':bounds,'materials':[m.name if m else None for m in o.data.materials],'collections':sorted(c.name for c in o.users_collection),'parent':o.parent.name if o.parent else None})
    else: out['objects'].append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None})
outpath=os.path.join(os.path.dirname(p),'..','..','audit','yue_kong_pao_hall','independent_grade_r1_reopen.json')
with open(outpath,'w',encoding='utf-8') as f: json.dump(out,f,indent=2)
print(json.dumps({k:out[k] for k in out if k!='objects'},indent=2))


