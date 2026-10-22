"""Refresh asset bounds and reference ledger from assembled linked geometry."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
M=P.parent/'modular'
manifest=json.loads((M/'manifest.json').read_text())
world=json.loads((P/'object_world_bounds.json').read_text())
for o in bpy.context.scene.objects:
 if o.type in ('MESH','FONT','CURVE'):
  world[o.name]={'world_bounds':[[min((o.matrix_world@Vector(c))[i] for c in o.bound_box),max((o.matrix_world@Vector(c))[i] for c in o.bound_box)] for i in range(3)],'matrix_world':[list(row) for row in o.matrix_world],'local_bounds':[list(c) for c in o.bound_box]}
for a in manifest['assets']:
 boxes=[world[n]['world_bounds'] for n in a['objects'] if n in world]
 a['source_bounds_world_m']=a['bounds_world_m']
 if boxes:a['bounds_world_m']=[[min(b[i][0] for b in boxes),max(b[i][1] for b in boxes)] for i in range(3)]
 a['accuracy_status']='unverified; see ../audit/master_building_audit.json'
 if a['id']=='wiley_hall':a['accuracy_status']='gross identity/location corrected; precise shell and height unverified'
(P/'object_world_bounds.json').write_text(json.dumps(world))
(M/'manifest.json').write_text(json.dumps(manifest,indent=2))
lines=['# Detailed building files','','Open these files directly to edit. Reopen `purdue_campus_linked.blend` to reload saved building changes. See `../audit/MASTER_AUDIT.md` for measured screening discrepancies and remaining work.','','| Building | File | Objects |','|---|---|---:|']
for a in manifest['assets']:
 if a['kind']=='detailed':lines.append('| '+a['id'].replace('_',' ').title()+' | ['+a['id']+'.blend]('+a['file']+') | '+str(a['object_count'])+' |')
(M/'BUILDINGS.md').write_text('\n'.join(lines))
print('FINALIZED_MANIFEST',len(manifest['assets']))
