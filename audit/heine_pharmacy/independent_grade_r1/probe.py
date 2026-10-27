import bpy, json, hashlib, os
from mathutils import Vector
asset=os.path.abspath('modular/buildings/heine_pharmacy.blend')
bpy.ops.wm.open_mainfile(filepath=asset)
coll=bpy.data.collections.get('Asset_heine_pharmacy')
objs=list(coll.all_objects) if coll else []
meshes=[o for o in objs if o.type=='MESH']
# evaluated local geometry bounds in asset coordinates (object matrix_world)
pts=[]
for o in meshes:
    for c in o.bound_box:
        pts.append(o.matrix_world @ Vector(c))
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
mats=[]
missing=[]
for m in bpy.data.materials:
    if m.users==0: continue
    rec={'name':m.name,'use_nodes':m.use_nodes,'nodes':[]}
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            rec['nodes'].append({'type':n.type,'name':n.name})
            if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE':
                p=bpy.path.abspath(n.image.filepath)
                if not os.path.exists(p): missing.append(p)
    mats.append(rec)
scene=bpy.context.scene
out={'asset':asset,'sha256':hashlib.sha256(open(asset,'rb').read()).hexdigest(),'scene':scene.name,'collection_found':bool(coll),'collection_name':coll.name if coll else None,'collection_objects':len(objs),'mesh_objects':len(meshes),'bounds_local_m':bounds,'object_names':[o.name for o in objs],'material_count':len(mats),'materials':mats,'missing_external_textures':sorted(set(missing)),'scenes':[s.name for s in bpy.data.scenes]}
p=os.path.abspath('audit/heine_pharmacy/independent_grade_r1/probe.json')
json.dump(out,open(p,'w',encoding='utf-8'),indent=2)
print(json.dumps({k:v for k,v in out.items() if k not in ('object_names','materials')},indent=2))
