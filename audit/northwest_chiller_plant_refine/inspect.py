import bpy, json
from mathutils import Vector
f='modular/buildings/northwest_chiller_plant.blend'
bpy.ops.wm.open_mainfile(filepath=f)
col=bpy.data.collections['Asset_northwest_chiller_plant']
def bounds(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[round(min(p[i] for p in pts),2) for i in range(3)],[round(max(p[i] for p in pts),2) for i in range(3)]]
objs=[]
for o in col.all_objects:
    if o.type=='MESH':
      mats=[m.name if m else None for m in o.data.materials]
      if len(objs)<450: objs.append({'n':o.name,'b':bounds(o),'m':mats})
print('scene',bpy.context.scene.render.engine,'objects',len(col.all_objects))
print(json.dumps(objs,indent=1))
