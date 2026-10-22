import bpy, json, math
from mathutils import Vector
r={}
r['views']=[{'screen':s.name,'shading':a.spaces.active.shading.type,'studio':a.spaces.active.shading.studiolight_rotate_z,'distance':a.spaces.active.region_3d.view_distance,'location':list(a.spaces.active.region_3d.view_location),'rotation':list(a.spaces.active.region_3d.view_rotation),'perspective':a.spaces.active.region_3d.view_perspective,'matrix':[list(x) for x in a.spaces.active.region_3d.view_matrix]} for s in bpy.data.screens for a in s.areas if a.type=='VIEW_3D']
r['cameras']=[{'name':o.name,'clip':[o.data.clip_start,o.data.clip_end],'type':o.data.type,'scale':o.data.ortho_scale,'location':list(o.location)} for o in bpy.data.objects if o.type=='CAMERA']
r['bad_vertices']=[]
for m in bpy.data.meshes:
    if any(not math.isfinite(x) for v in m.vertices for x in v.co): r['bad_vertices'].append(m.name)
r['bounds']=sorted([(max(abs(x) for c in o.bound_box for x in (o.matrix_world@Vector(c))),o.name) for o in bpy.data.objects if o.type=='MESH'],reverse=True)[:20]
open(bpy.path.abspath('//stability_details.json'),'w').write(json.dumps(r,indent=2))
print(json.dumps({k:v for k,v in r.items() if k!='cameras'},indent=2))
