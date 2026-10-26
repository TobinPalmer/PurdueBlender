"""Background Blender validation after opening modular/purdue_campus_linked.blend."""
import bpy,json,os
from pathlib import Path
base=Path(__file__).resolve().parents[2]/'modular'
m=json.loads((base/'manifest.json').read_text())
transforms=json.loads((base/'source_transforms.json').read_text())
corrections_path=base.parent/'audit/placement_corrections.json'
corrections=json.loads(corrections_path.read_text()) if corrections_path.exists() else []
expected_deltas={n:c['translation_m'] for c in corrections for n in c['objects']}
objects=list(bpy.context.scene.objects)
byname={o.name:o for o in objects}
errors=[]
if len(objects)!=m['source_object_count']:errors.append('Object count mismatch')
for name,mat in transforms.items():
 o=byname.get(name)
 if o is None:errors.append('Missing object: '+name);continue
 expected=[row[:] for row in mat]
 if name in expected_deltas:
  for i in range(3):expected[i][3]+=expected_deltas[name][i]
 if max(abs(o.matrix_world[i][j]-expected[i][j]) for i in range(4) for j in range(4))>0.001:errors.append('Unexpected transform change: '+name)
for a in m['assets']:
 path=base/a['file']
 if not path.is_file():errors.append('Missing file: '+a['file']);continue
 # Read every .blend's directory through Blender to check saved scenes and collection exports.
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):
  if a['collection'] not in src.collections:errors.append('Missing exported collection: '+a['id'])
  if a['scene'] not in src.scenes:errors.append('Missing editable scene: '+a['id'])
 col=next((c for c in bpy.context.scene.collection.children if c.name==a['collection']),None)
 if not col or not col.library:errors.append('Asset not linked: '+a['id'])
 elif len(col.all_objects)!=a['object_count']:errors.append('Object dependency mismatch: '+a['id'])
for lib in bpy.data.libraries:
 if not os.path.exists(bpy.path.abspath(lib.filepath)):errors.append('Missing library: '+lib.filepath)
 if not lib.filepath.startswith('//'):errors.append('Nonrelative library: '+lib.filepath)
visibility=json.loads((base/'source_visibility.json').read_text()) if (base/'source_visibility.json').exists() else {}
for name,flags in visibility.items():
 o=byname.get(name)
 if o and flags['hide_set']!=o.hide_get():
  o.hide_set(flags['hide_set'])
# Restore per-view-layer hidden state, which collection linking does not carry.
if visibility:
 bpy.ops.wm.save_as_mainfile(filepath=str(base/'purdue_campus_linked.blend'))
r={'status':'PASS' if not errors else 'FAIL','asset_count':len(m['assets']),'building_count':sum(a['kind']!='site' for a in m['assets']),'source_objects':m['source_object_count'],'master_objects':len(objects),'errors':errors}
r['documented_placement_corrections']=[c['asset_id'] for c in corrections]
r['independent_open_checks']=[]
samples=[next(a for a in m['assets'] if a['id']==key) for key in ('walc','hovde_hall')]
samples.append(next(a for a in m['assets'] if a['kind']=='massing'))
for a in samples:
 bpy.ops.wm.open_mainfile(filepath=str(base/a['file']))
 good=len(bpy.context.scene.objects)==a['object_count'] and bpy.data.collections.get(a['collection']) is not None
 r['independent_open_checks'].append({'id':a['id'],'objects':len(bpy.context.scene.objects),'status':'PASS' if good else 'FAIL'})
 if not good:errors.append('Independent open mismatch: '+a['id'])
r['status']='PASS' if not errors else 'FAIL'
(base/'verification.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
if errors:raise RuntimeError('Modular validation failed')
