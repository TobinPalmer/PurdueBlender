import bpy, json, math
from pathlib import Path
p = Path(r'modular/buildings/massing_campus_edge_343e3d8.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
asset_id='massing_campus_edge_343e3d8'
col=bpy.data.collections.get('Asset_'+asset_id)
scene=bpy.context.scene
objs=list(col.objects) if col else []
# Evaluate actual collection objects in world coordinates, including modifiers.
allco=[]; meshdata=[]
for o in objs:
    if o.type!='MESH':
        meshdata.append({'name':o.name,'type':o.type}); continue
    deps=bpy.context.evaluated_depsgraph_get(); eo=o.evaluated_get(deps); me=eo.to_mesh()
    points=[eo.matrix_world @ v.co for v in me.vertices]
    allco.extend(points)
    meshdata.append({'name':o.name,'verts':len(me.vertices),'faces':len(me.polygons),'materials':[m.name for m in me.materials if m],'modifiers':[m.name for m in o.modifiers],'world_bounds':[[min((eo.matrix_world @ v.co)[i] for v in me.vertices),max((eo.matrix_world @ v.co)[i] for v in me.vertices)] for i in range(3)] if me.vertices else None})
    eo.to_mesh_clear()
coords=[[min(v[i] for v in allco),max(v[i] for v in allco)] for i in range(3)] if allco else None
result={'asset_path':str(p),'blender_version':bpy.app.version_string,'scene':scene.name if scene else None,'collection':col.name if col else None,'collection_properties':{k:col.get(k) for k in ('asset_id','building_name','coordinate_contract','footprint_source','building_height_status','source_uncertainty')} if col else {},'object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'non_mesh_objects':[o.name for o in objs if o.type!='MESH'],'linked_libraries':[str(x.filepath) for x in bpy.data.libraries],'bounds_world_m':coords,'meshes':meshdata,'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.packed_file is None]}
Path(r'audit/massing_campus_edge_independent_grade/probe.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='meshes'},indent=2))
