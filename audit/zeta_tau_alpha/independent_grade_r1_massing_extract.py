import bpy, json, math, hashlib, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'modular'/'buildings'/'massing_zeta_tau_alpha_af8a443.blend'
bpy.ops.wm.open_mainfile(filepath=str(PATH))
scene=bpy.data.scenes.get('Building_massing_zeta_tau_alpha_af8a443')
asset=bpy.data.collections.get('Asset_massing_zeta_tau_alpha_af8a443')
objs=list(asset.all_objects) if asset else []
rows=[]
for o in objs:
 if o.type!='MESH': continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 rows.append({'name':o.name,'bounds':[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)],'vertex_count':len(vs),'xy_vertices':sorted(set((round(v.x,6),round(v.y,6)) for v in vs))})
out={'sha256':hashlib.sha256(PATH.read_bytes()).hexdigest(),'scene':scene.name if scene else None,'asset_collection':asset.name if asset else None,'objects':rows}
outpath=Path(__file__).resolve().with_name('independent_grade_r1_massing_extract.json')
outpath.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
