import bpy, hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
asset = root / 'modular/buildings/stanley_coulter_hall.blend'
report_path = root / 'audit/batch3_stanley/exterior_bounds_r6.json'
origin_xy = [-57.55689525604248, -99.14793586730957]
asset_collection = bpy.data.collections['Asset_stanley_coulter_hall']
exterior_names = {'SC_Exterior_Structure','SC_Portico_and_Entrances','SC_Fenestration','SC_Roof_and_Dormers','SC_Plaza_and_Site'}
collections = [asset_collection] + [bpy.data.collections[name] for name in exterior_names]
# Include direct root meshes and meshes in the exterior child groups, excluding interiors and inspection cameras.
objects = set()
for collection in collections:
    if collection == asset_collection:
        objects.update(obj for obj in collection.objects if obj.type == 'MESH')
    else:
        objects.update(obj for obj in collection.all_objects if obj.type == 'MESH')
depsgraph = bpy.context.evaluated_depsgraph_get()
points=[]
for obj in objects:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
    finally:
        evaluated.to_mesh_clear()
if not points:
    raise RuntimeError('No exterior mesh vertices')
local = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
world = [[local[i][0]+origin_xy[i],local[i][1]+origin_xy[i]] if i<2 else local[i] for i in range(3)]
report={'asset':str(asset),'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'exterior_collections':sorted(exterior_names),'direct_root_meshes_included':sum(1 for o in asset_collection.objects if o.type=='MESH'),'evaluated_mesh_object_count':len(objects),'local_bounds_axis_major_m':local,'manifest_placement_origin_xy_m':origin_xy,'world_bounds_axis_major_m':world,'method':'Fresh standalone Blender 5.2.3 reopen; evaluated mesh vertices from the active exterior structure, portico/entrance, fenestration, roof, plaza/site child collections, plus mesh objects directly in the asset root. Interior shell, schematic circulation and inspection cameras excluded; hidden sibling recovery archives excluded.'}
report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
