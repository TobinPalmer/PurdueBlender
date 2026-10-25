import bpy, json
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
bpy.ops.wm.open_mainfile(filepath=ROOT+r'\modular\buildings\neil_armstrong_hall.blend')
col=bpy.data.collections['Asset_neil_armstrong_hall']
rows=[]
for o in col.objects:
    if o.type!='MESH': continue
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    mn=[min(p[i] for p in pts) for i in range(3)]; mx=[max(p[i] for p in pts) for i in range(3)]
    if any(q in o.name for q in ('Curtain','Mullion','Transom','Canopy','West_Wall')):
        rows.append({'name':o.name,'bounds':[[round(x,3) for x in mn],[round(x,3) for x in mx]],'verts':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials]})
print(json.dumps(rows,indent=2))
