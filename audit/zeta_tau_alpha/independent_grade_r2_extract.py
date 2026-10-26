import bpy,json,hashlib,math
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/zeta_tau_alpha.blend'
OUT=Path(__file__).with_name('independent_grade_r2_extract.json')
EXPECTED='1e9b54a032ac508e3e473e1757b6edce6ee8724b581c884d54e984572ed8a7af'
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
assert sha==EXPECTED, f'candidate changed {sha}'
assert Path(bpy.data.filepath).resolve()==ASSET.resolve(), f'wrong blend loaded: {bpy.data.filepath}'
col=bpy.data.collections.get('Asset_massing_zeta_tau_alpha_af8a443')
assert col is not None and len(col.all_objects)==563
objs=list(col.all_objects); meshes=[o for o in objs if o.type=='MESH']
assert len(meshes)==562 and all(o.data.materials for o in meshes)
shell=bpy.data.objects.get('ZTA_Continuous_Red_Brick_Exterior_Shell')
assert shell is not None
verts=[list(shell.matrix_world @ v.co) for v in shell.data.vertices]
minz=min(v[2] for v in verts); base=[v for v in verts if abs(v[2]-minz)<1e-4]
center=[sum(v[i] for v in base)/len(base) for i in range(3)]
base_order=sorted([[v[0],v[1]] for v in base],key=lambda p:math.atan2(p[1]-center[1],p[0]-center[0]))
base_set={i for i,v in enumerate(verts) if abs(v[2]-minz)<1e-4}
adj={i:set() for i in base_set}
for f in shell.data.polygons:
 ids=list(f.vertices); b=[i for i in ids if i in base_set]
 if len(b)==2: a,c=b; adj[a].add(c); adj[c].add(a)
cycle=[]
if adj and all(len(x)==2 for x in adj.values()):
 start=min(adj); prev=None; cur=start
 while not cycle or cur!=start:
  cycle.append([verts[cur][0],verts[cur][1]])
  nxt=next((n for n in adj[cur] if n!=prev),None); prev,cur=cur,nxt
  if cur is None or len(cycle)>len(adj)+1:break
bounds=[]
for ax in range(3):
 vals=[]
 for o in meshes:
  for c in o.bound_box: vals.append((o.matrix_world@Vector(c))[ax])
 bounds.append([min(vals),max(vals)])
images=[{'name':i.name,'packed':i.packed_file is not None,'size':list(i.size)} for i in bpy.data.images if i.source=='FILE']
materials=sorted({m.name for o in meshes for m in o.data.materials if m})
letters=bpy.data.objects.get('ZTA_Pediment_Letters')
plaque=bpy.data.objects.get('ZTA_Pediment_Plaque')
ped=bpy.data.objects.get('ZTA_Portico_Pediment')
def wb(o):
 return [[min((o.matrix_world@Vector(c))[i] for c in o.bound_box),max((o.matrix_world@Vector(c))[i] for c in o.bound_box)] for i in range(3)]
report={'sha256':sha,'scene':bpy.context.scene.name,'collection':col.name,'object_count':len(objs),'mesh_count':len(meshes),'vertex_count':sum(len(o.data.vertices) for o in meshes),'face_count':sum(len(o.data.polygons) for o in meshes),'material_names':materials,'material_count':len(materials),'materialless_meshes':[o.name for o in meshes if not o.data.materials],'images':images,'nonmesh_objects':[{'name':o.name,'type':o.type} for o in objs if o.type!='MESH'],'world_bounds_xyz':bounds,'shell_base_ring_ordered':cycle,'shell_base_ring_count':len(base_order),'shell_bounds_z':[minz,max(v[2] for v in verts)],'asset_origin_xy_m':list(col.get('placement_origin_xy_m',[])),'letter_text':getattr(getattr(letters,'data',None),'body',None),'letter_world_bounds':wb(letters) if letters else None,'plaque_world_bounds':wb(plaque) if plaque else None,'pediment_world_bounds':wb(ped) if ped else None,'material_images_all_packed':all(i['packed'] for i in images),'fresh_process_reopen':True}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2))
