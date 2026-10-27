import bpy, json
out=[]
for p in [r'modular/buildings/massing_house_301841332_9b3bd1f.blend',r'modular/buildings/massing_house_301841334_fa7e5a2.blend']:
  bpy.ops.wm.open_mainfile(filepath=p)
  s=bpy.context.scene
  for o in s.objects:
    if o.type!='MESH': continue
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    base=[[round(v.x,9),round(v.y,9)] for v in pts if abs(v.z)<.001]
    out.append({'file':p,'name':o.name,'base':base})
open(r'audit/zeta_beta_tau/candidate_base_rings.json','w',encoding='utf8').write(json.dumps(out,indent=2))
