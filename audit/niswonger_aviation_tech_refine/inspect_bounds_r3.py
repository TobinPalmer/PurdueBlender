import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/niswonger_aviation_tech.blend'))
a=bpy.data.collections['Asset_niswonger_aviation_tech']
out=[]
for o in a.all_objects:
    ps=[o.matrix_world@Vector(c) for c in o.bound_box]
    b=[[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
    if b[0][0]<-50 or b[1][0]>50 or b[0][1]<-65.5 or b[1][1]>65.5 or b[0][2]<-0.16 or b[1][2]>10.21:
        out.append({'name':o.name,'type':o.type,'bounds':b})
out.sort(key=lambda x:max(abs(x['bounds'][0][2]),abs(x['bounds'][1][2])),reverse=True)
meshes=[o for o in a.all_objects if o.type=='MESH']
pts=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
mesh_bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
(ROOT/'audit/niswonger_aviation_tech_refine/bounds_outliers_r3.json').write_text(json.dumps({'mesh_bounds':mesh_bounds,'non_mesh_or_other_objects_outside_manifest_envelope':out},indent=2))
print('outliers',len(out),'highest',out[:10])
