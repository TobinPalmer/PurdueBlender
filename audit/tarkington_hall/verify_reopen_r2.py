import bpy, json, math
from mathutils import Vector
meshes=[o for o in bpy.data.objects if o.type=='MESH']
bad=[]
for o in meshes:
    for v in o.data.vertices:
        if not all(math.isfinite(x) for x in v.co): bad.append(o.name)
missing=[o.name for o in meshes if not any(m is not None for m in o.data.materials)]
room=bpy.data.objects.get('Tark_Dorm_Room118_Floor')
check_names=['Tark_West_Connector_Brick_Shaft','Tark_East_Connector_Brick_Shaft','Tark_SE_Wing_Brick_Shaft','Tark_SW_Wing_Upper_Brick_Shaft']
checks={}
for name in check_names:
    o=bpy.data.objects.get(name)
    if o:
        pts=[o.matrix_world@Vector(v) for v in o.bound_box]
        checks[name]={'bounds_xyz':[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],'parent':o.parent.name if o.parent else None,'materials':[m.name for m in o.data.materials if m]}
coords=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
report={'filepath':bpy.data.filepath,'scene_count':len(bpy.data.scenes),'object_count':len(bpy.data.objects),'mesh_count':len(meshes),'material_count_used':sum(1 for m in bpy.data.materials if m.users),'nonfinite_meshes':sorted(set(bad)),'meshes_without_materials':missing,'root_exists':bpy.data.objects.get('AssetRoot_tarkington_hall') is not None,'room118_floor_dimensions':list(room.dimensions) if room else None,'world_bounds_xyz':[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)],'geometry_checks':checks,'connectors_added':len([o for o in meshes if o.name.startswith(('Tark_West_Connector_','Tark_East_Connector_'))])}
print(json.dumps(report,indent=2))
