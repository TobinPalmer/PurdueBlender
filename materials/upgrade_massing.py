"""Upgrade shared background-building materials, retaining individual files and coordinates."""
import bpy,json,sys,shutil,time,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;BASE=P.parent
sys.path.insert(0,str(P));import pbr_upgrade as pbr
m=json.loads((BASE/'modular/manifest.json').read_text())
assets=[a for a in m['assets'] if a['kind']=='massing']
BACK=P/'backups/massing';BACK.mkdir(parents=True,exist_ok=True)
STATE=P/'massing_progress.json'
state=json.loads(STATE.read_text()) if STATE.exists() else {'completed':{},'failed':{}}
for i,a in enumerate(assets):
 if a['id'] in state['completed']:continue
 path=BASE/'modular'/a['file']
 try:
  beforehash=hashlib.sha256(path.read_bytes()).hexdigest()
  bpy.ops.wm.open_mainfile(filepath=str(path))
  col=bpy.data.collections.get(a['collection'])
  if not col:raise RuntimeError('Missing asset collection')
  matrices={o.name:[list(r) for r in o.matrix_world] for o in col.all_objects}
  materials={slot.material for o in col.all_objects if o.type=='MESH' for slot in o.material_slots if slot.material}
  overrides={ma.name:'stone' for ma in materials if any(t in ma.name.lower() for t in ('slate','shingle','roof')) and pbr.classify(ma.name) is None}
  result=pbr.upgrade_collection(col,overrides=overrides,texture_set='red_brick',tile_m=1.4)
  if result['materials']:
   if hashlib.sha256(path.read_bytes()).hexdigest()!=beforehash:raise RuntimeError('Concurrent source edit detected; not overwriting')
   dest=BACK/path.name
   if not dest.exists():shutil.copy2(path,dest)
   for o in col.all_objects:
    if o.name not in matrices or max(abs(o.matrix_world[r][c]-matrices[o.name][r][c]) for r in range(4) for c in range(4))>.0001:raise RuntimeError('Unexpected transform change')
   bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
  state['completed'][a['id']]={'file':a['file'],'materials':result['materials'],'brick_objects':len(result['brick_uv_objects']),'source_hash':beforehash,'textures':'shared relative files in materials/textures/red_brick, not duplicated per house'}
 except Exception as e:state['failed'][a['id']]=str(e)
 if i%25==0:
  STATE.write_text(json.dumps(state,indent=2));print('MASSING_PROGRESS',i,len(assets),len(state['failed']),flush=True)
STATE.write_text(json.dumps(state,indent=2))
print('MASSING_DONE',len(state['completed']),len(state['failed']),flush=True)
