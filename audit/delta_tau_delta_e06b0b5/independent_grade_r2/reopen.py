import bpy, json, math, hashlib
from pathlib import Path
p=Path(bpy.data.filepath); col=bpy.data.collections.get('Asset_massing_delta_tau_delta_e06b0b5'); s=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get(); objs=[]
for o in sorted(col.objects,key=lambda x:x.name) if col else []:
    e=o.evaluated_get(deps); m=e.to_mesh(); pts=[e.matrix_world@v.co for v in m.vertices] if m else []
    b=[[min((v[i] for v in pts),default=0),max((v[i] for v in pts),default=0)] for i in range(3)]
    objs.append({'name':o.name,'type':o.type,'vertices':len(m.vertices) if m else 0,'polygons':len(m.polygons) if m else 0,'bounds_world_m':b,'modifiers':[x.type for x in o.modifiers],'world_vertices_xyz':[[round(v.x,8),round(v.y,8),round(v.z,8)] for v in pts] if o.name=='DTD_Main_Brick_Envelope' else None})
    if m:e.to_mesh_clear()
mesh=[o for o in objs if o['type']=='MESH']; pnts=[(x,y,z) for o in mesh for x in o['bounds_world_m'][0] for y in o['bounds_world_m'][1] for z in o['bounds_world_m'][2]]
bounds=[[min(v[i] for v in pnts),max(v[i] for v in pnts)] for i in range(3)] if pnts else []
res={'asset':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'scene':s.name,'collection_exists':bool(col),'object_count':len(col.objects) if col else 0,'scene_object_count':len(s.objects),'bounds_world_m':bounds,'structural_body':next((o for o in objs if o['name']=='DTD_Main_Brick_Envelope'),None),'modifiers_total':sum(len(o['modifiers']) for o in objs),'external_libraries':[x.filepath for x in bpy.data.libraries if x.filepath],'scene_unassigned_objects':[{'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection]} for o in s.objects if not col or o.name not in col.objects.keys()],'objects':objs}
out=Path(__file__).parent/'reopen_inspection.json'; out.write_text(json.dumps(res,indent=2)); print('R2_REOPEN',json.dumps({k:v for k,v in res.items() if k!='objects'},indent=2))


