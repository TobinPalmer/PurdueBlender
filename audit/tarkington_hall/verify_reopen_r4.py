import bpy,hashlib,json,math
from pathlib import Path
p=Path(bpy.data.filepath).resolve(); expected='B844A77E35AD44BF722EA0432ED40DC47A6B01FFF24C095CBABF68E760F87065'
sha=hashlib.sha256(p.read_bytes()).hexdigest()
if sha.upper()!=expected: raise RuntimeError(f'Candidate SHA changed: {sha}')
a=bpy.data.collections.get('Asset_tarkington_hall'); r=bpy.data.objects.get('AssetRoot_tarkington_hall')
if not a or not r: raise RuntimeError('Missing asset collection/root')
objs=list(a.objects); meshes=[o for o in objs if o.type=='MESH']; names={o.name for o in objs}
connect=[o for o in bpy.data.objects if 'Connector' in o.name]
outside=[o.name for o in connect if o.name not in names]
parent_errors=[o.name for o in connect if o.name in names and o.parent!=r]
missing_mats=[o.name for o in meshes if not any(o.data.materials)]
nonfinite=[o.name for o in meshes if any(not all(math.isfinite(float(x)) for x in v.co) for v in o.data.vertices)]
dupes=sorted(n for n in names if sum(1 for o in objs if o.name==n)>1)
external=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.users and not im.packed_file:
  path=Path(bpy.path.abspath(im.filepath))
  if not path.exists(): external.append(str(path))
root_ok=all(abs(float(v)-1)<1e-6 for v in r.scale) and all(abs(float(v))<1e-6 for v in r.rotation_euler)
report={'fresh_process_reopen':True,'asset_path':str(p),'sha256':sha,'blender_version':bpy.app.version_string,'collection_object_count':len(objs),'mesh_count':len(meshes),'connector_objects_database_count':len(connect),'connector_objects_outside_export':outside,'connector_parent_errors':parent_errors,'materialless_meshes':missing_mats,'nonfinite_meshes':nonfinite,'duplicate_names':dupes,'missing_external_images':external,'identity_root_transform':root_ok,'used_material_count':len({m.name for o in meshes for m in o.data.materials if m})}
if any((outside,parent_errors,missing_mats,nonfinite,dupes,external)) or not root_ok: raise RuntimeError(json.dumps(report,indent=2))
Path('audit/tarkington_hall/reopen_validation_r4.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))

