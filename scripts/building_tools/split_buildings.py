"""Run in background Blender against modular_source_snapshot.blend."""
import bpy, json, re, os, math, hashlib
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'modular'
(OUT/'buildings').mkdir(parents=True,exist_ok=True)
(OUT/'site').mkdir(exist_ok=True)
source_scene=bpy.context.scene
original=list(source_scene.objects)
original_camera=source_scene.camera.name if source_scene.camera else None
original_matrices={o.name:[list(row) for row in o.matrix_world] for o in original}
groups={}
tokens=['South_Hall','Beering_Hall','Tarkington_Hall','Owen_Hall','Ross_Ade','Winifred_Parker_Hall','Frieda_Parker_Hall','Elliott_Hall_of_Music','University_Hall','Neil_Armstrong_Hall','Mackey_Arena','Purdue_Memorial_Union','Stewart_Center','Hovde_Hall','Class_of_1950','Armory','Math_Sciences','Felix_Haas_Hall']
special={'Master_WALC_Detailed':'walc','06_Wiley_Hall_Detailed':'wiley_hall','04_Purdue_Bell_Tower_Detailed':'bell_tower','09_Mechanical_Engineering_Detailed':'mechanical_engineering','10_Potter_Engineering_Detailed':'potter_engineering','11_Electrical_Engineering_Detailed':'electrical_engineering'}
membership={}
for c in source_scene.collection.children:
 key=special.get(c.name)
 if not key:
  key=next((t.lower() for t in tokens if re.match(r'^\d+_'+re.escape(t),c.name)),None)
 if key:
  for o in c.all_objects:
   if o.name in membership and membership[o.name]!=key: raise RuntimeError('Conflicting building membership '+o.name)
   membership[o.name]=key
for o in original:
 key=membership.get(o.name)
 if key is None:
  if any(c.name in ('02_Campus_Buildings_Massing','03_West_Lafayette_Houses') for c in o.users_collection):
   slug=re.sub('[^a-z0-9]+','_',o.name.lower()).strip('_')[:90]
   key='massing_'+slug+'_'+hashlib.sha1(o.name.encode()).hexdigest()[:7]
  else: key='campus_site'
 groups.setdefault(key,[]).append(o)
# Parent dependencies must travel together, especially building roots placed in camera collections.
changed=True
while changed:
 changed=False
 owner={o.name:k for k,obs in groups.items() for o in obs}
 for o in original:
  if o.parent and owner[o.name]!=owner.get(o.parent.name):
   target=owner[o.name] if owner[o.name]!='campus_site' else owner[o.parent.name]
   for ob in (o,o.parent):
    prev=owner[ob.name]
    if prev!=target:
     groups[prev].remove(ob);groups[target].append(ob);owner[ob.name]=target;changed=True
records=[]
for index,(key,obs) in enumerate(sorted(groups.items())):
 if not obs: continue
 is_site=key=='campus_site'
 folder='site' if is_site else 'buildings'
 path=OUT/folder/(key+'.blend')
 col=bpy.data.collections.new('Asset_'+key)
 for o in obs: col.objects.link(o)
 sc=bpy.data.scenes.new('Building_'+key)
 sc.collection.children.link(col)
 sc.world=source_scene.world
 sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 sc.view_layers[0].update()
 if is_site: sc.camera=next((o for o in obs if o.name==original_camera),None)
 points=[o.matrix_world@Vector(c) for o in obs if o.type in ('MESH','FONT','CURVE') for c in o.bound_box]
 bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
 ext=[o for o in obs if any('Exterior' in c.name or 'Masonry' in c.name for c in o.users_collection)]
 ep=[o.matrix_world@Vector(c) for o in ext if o.type=='MESH' for c in o.bound_box]
 eb=[[min(p[i] for p in ep),max(p[i] for p in ep)] for i in range(3)] if ep else bounds
 if not path.exists():
  bpy.data.libraries.write(str(path),{sc},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
 records.append({'id':key,'kind':'site' if is_site else ('massing' if key.startswith('massing_') else 'detailed'),'file':path.relative_to(OUT).as_posix(),'collection':col.name,'scene':sc.name,'objects':[o.name for o in obs],'object_count':len(obs),'bounds_world_m':bounds,'exterior_bounds_world_m':eb,'accuracy_status':'unverified','placement_transform':'identity; object coordinates retained in campus world space'})
 bpy.data.scenes.remove(sc)
 bpy.data.collections.remove(col)
 if index%100==0: print('EXPORTED',index,key,flush=True)
assert sum(x['object_count'] for x in records)==len(original)
# Replace scene contents by linked asset collections, retaining the original UI and render settings.
bpy.data.batch_remove(ids=original)
for c in list(source_scene.collection.children): source_scene.collection.children.unlink(c)
for ri,r in enumerate(records):
 with bpy.data.libraries.load(str(OUT/r['file']),link=True,relative=True) as (src,dst): dst.collections=[r['collection']]
 source_scene.collection.children.link(dst.collections[0])
 if ri%100==0: print('LINKED',ri,r['id'],flush=True)
source_scene.camera=next((o for o in source_scene.objects if o.name==original_camera),None)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='SOLID'
   area.spaces.active.region_3d.view_distance=max(30,area.spaces.active.region_3d.view_distance)
manifest={'source':'../modular_source_snapshot.blend','origin':{'lat':40.4274,'lon':-86.9137,'axes':'X east, Y north, Z up','unit':'meters','latitude_to_meters':111040.0,'longitude_to_meters':111412.84*math.cos(math.radians(40.4274))},'source_object_count':len(original),'assets':records}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
(OUT/'source_transforms.json').write_text(json.dumps(original_matrices))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'purdue_campus_linked.blend'))
print('MODULAR_COMPLETE',len(records),len(source_scene.objects),flush=True)
