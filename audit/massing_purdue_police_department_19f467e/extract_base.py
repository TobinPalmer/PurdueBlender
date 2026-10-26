import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/massing_purdue_police_department_19f467e.blend')
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
vs=[]
for v in o.data.vertices:
 p=o.matrix_world@v.co
 if abs(p.z)<1e-3: vs.append([round(p.x,4),round(p.y,4)])
Path('audit/massing_purdue_police_department_19f467e/model_z0_vertices.json').write_text(json.dumps(vs,indent=2))
print('count',len(vs),vs)
