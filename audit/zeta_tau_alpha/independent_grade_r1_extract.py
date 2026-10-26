import bpy, json, os, hashlib, math
from mathutils import Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
PATH=os.path.join(ROOT,'modular','buildings','zeta_tau_alpha.blend')
OUT=os.path.join(os.path.dirname(__file__),'independent_grade_r1_extract.json')
EXPECTED='795eef2993264674747768df2bd29ff6bdef3ff7ab48d33299c03060691b67d6'
sha=hashlib.sha256(open(PATH,'rb').read()).hexdigest()
assert sha==EXPECTED, f'candidate changed: {sha}'
bpy.ops.wm.open_mainfile(filepath=PATH)
asset=bpy.data.collections.get('Asset_massing_zeta_tau_alpha_af8a443')
assert asset is not None
objs=list(asset.all_objects)
mesh_objs=[o for o in objs if o.type=='MESH']
shell=bpy.data.objects.get('ZTA_Continuous_Red_Brick_Exterior_Shell')
assert shell and shell.type=='MESH'
verts=[list(shell.matrix_world @ v.co) for v in shell.data.vertices]
minz=min(v[2] for v in verts)
base=[v for v in verts if abs(v[2]-minz)<1e-4]
center=[sum(v[i] for v in base)/len(base) for i in range(3)]
base_xy=sorted([[v[0],v[1]] for v in base],key=lambda p: math.atan2(p[1]-center[1],p[0]-center[0]))
base_idx={i for i,v in enumerate(verts) if abs(v[2]-minz)<1e-4}
adj={i:set() for i in base_idx}
for face in shell.data.polygons:
    ids=list(face.vertices)
    btm=[i for i in ids if i in base_idx]
    if len(btm)==2:
        a,b=btm
        adj[a].add(b); adj[b].add(a)
cycle=[]
if adj and all(len(v)==2 for v in adj.values()):
    start=min(adj); prev=None; cur=start
    while not cycle or cur!=start:
        cycle.append([verts[cur][0],verts[cur][1]])
        nxt=next((n for n in adj[cur] if n!=prev),None)
        prev,cur=cur,nxt
        if cur is None or len(cycle)>len(adj)+1: break
world_bounds=[]
for axis in range(3):
    vals=[]
    for o in objs:
        if o.type=='MESH':
            ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
            me=ev.to_mesh()
            try: vals.extend([(o.matrix_world @ Vector(c))[axis] for c in ev.bound_box])
            finally: ev.to_mesh_clear()
    world_bounds.append([min(vals),max(vals)] if vals else None)
materials=[]
for m in bpy.data.materials:
    if m.name.startswith('ZTA |'):
        nodes=[]; imgs=[]
        if m.use_nodes and m.node_tree:
            for n in m.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image:
                    imgs.append({'name':n.image.name,'packed':n.image.packed_file is not None,'size':list(n.image.size)})
            nodes=[n.type for n in m.node_tree.nodes]
        materials.append({'name':m.name,'nodes':nodes,'images':imgs})
images=[{'name':i.name,'filepath':i.filepath,'packed':i.packed_file is not None,'size':list(i.size)} for i in bpy.data.images if i.source=='FILE']
counts={}
for o in objs:
    prefix=o.name.split('_')[0]
    counts[prefix]=counts.get(prefix,0)+1
report={'sha256':sha,'scene':bpy.data.scenes.get('Building_massing_zeta_tau_alpha_af8a443').name,
'asset_collection':asset.name,'object_count':len(objs),'mesh_count':len(mesh_objs),'nonmesh_objects':[{'name':o.name,'type':o.type} for o in objs if o.type!='MESH'],
'mesh_vertex_count':sum(len(o.data.vertices) for o in mesh_objs),'mesh_face_count':sum(len(o.data.polygons) for o in mesh_objs),
'world_bounds_xyz':world_bounds,'shell_object':shell.name,'shell_mesh_vertices':len(verts),'shell_mesh_faces':len(shell.data.polygons),
'shell_z_bounds':[minz,max(v[2] for v in verts)],'shell_base_ring_count':len(base_xy),'shell_base_ring_xy_sorted':base_xy,
'shell_base_ring_xy_ordered':cycle,'shell_base_ring_graph_degrees':{str(k):len(v) for k,v in adj.items()},
'asset_custom_properties':{k:(list(v) if hasattr(v,'__len__') and not isinstance(v,str) else v) for k,v in asset.items()},
'text_objects':[{'name':o.name,'body':getattr(o.data,'body',''),'location':list(o.matrix_world.translation),
 'rotation_degrees':[math.degrees(a) for a in o.matrix_world.to_euler()],
 'world_bounds':[[min((o.matrix_world@Vector(c))[i] for c in o.bound_box),max((o.matrix_world@Vector(c))[i] for c in o.bound_box)] for i in range(3)]} for o in objs if o.type=='FONT'],
'materials':materials,'images':images,'object_name_prefix_counts':counts}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))

