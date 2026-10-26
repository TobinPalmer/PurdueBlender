import bpy, json, math, hashlib
from pathlib import Path
p=Path(bpy.data.filepath)
colname='Asset_massing_delta_tau_delta_e06b0b5'
col=bpy.data.collections.get(colname)
s=bpy.context.scene
objects=[]
for o in sorted(col.objects, key=lambda x:x.name) if col else []:
    deps=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(deps); mesh=e.to_mesh()
    pts=[e.matrix_world @ v.co for v in mesh.vertices] if mesh else []
    b=[[min((v[i] for v in pts),default=0),max((v[i] for v in pts),default=0)] for i in range(3)]
    objects.append({'name':o.name,'type':o.type,'vertices':len(mesh.vertices) if mesh else 0,'polygons':len(mesh.polygons) if mesh else 0,'bounds_world_m':b,'modifiers':[m.type for m in o.modifiers],'library':o.library.filepath if o.library else None,'world_vertices_xyz':[[round(v.x,8),round(v.y,8),round(v.z,8)] for v in pts] if o.name=='DTD_Main_Brick_Envelope' else None})
    if mesh: e.to_mesh_clear()
meshobjs=[o for o in objects if o['type']=='MESH']
allpts=[(x,y,z) for ob in meshobjs for x in [ob['bounds_world_m'][0][0],ob['bounds_world_m'][0][1]] for y in [ob['bounds_world_m'][1][0],ob['bounds_world_m'][1][1]] for z in [ob['bounds_world_m'][2][0],ob['bounds_world_m'][2][1]]]
bounds=[[min(v[i] for v in allpts),max(v[i] for v in allpts)] for i in range(3)] if allpts else []
body=next((o for o in objects if o['name']=='DTD_Main_Brick_Envelope'),None)
result={'asset':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'scene':s.name,'collection_exists':bool(col),'collection_children':[c.name for c in col.children] if col else [],'object_count':len(col.objects) if col else 0,'scene_object_count':len(s.objects),'bounds_world_m':bounds,'structural_body':next((o for o in objects if o['name']=='DTD_Main_Brick_Envelope'),None),'objects':objects,'external_libraries':[lib.filepath for lib in bpy.data.libraries if lib.filepath]}
out=Path(__file__).parent/'reopen_inspection.json'; out.write_text(json.dumps(result,indent=2))
print('DTD_REOPEN_INSPECTION',out)
print(json.dumps({k:v for k,v in result.items() if k!='objects'},indent=2))



