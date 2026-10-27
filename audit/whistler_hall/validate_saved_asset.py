"""Fresh-process structural check for the saved Whistler library."""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/massing_whistler_hall_6f6bf8d.blend'
out=root/'audit/whistler_hall/fresh_open_validation.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
collection=bpy.data.collections.get('Asset_massing_whistler_hall_6f6bf8d')
def descendants(col):
    yield col
    for child in col.children:
        yield from descendants(child)
cols=list(descendants(collection)) if collection else []
objects=[o for col in cols for o in col.objects]
building=bpy.data.objects.get('Whistler Hall')
if building is None or building.type!='MESH':
    raise RuntimeError('Expected Whistler Hall mesh missing')
world=[]
for obj in objects:
    if obj.type=='MESH':
        world.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
local_building_xy=[[min(v.co[i] for v in building.data.vertices),max(v.co[i] for v in building.data.vertices)] for i in range(2)]
material_names=sorted({m.name for o in objects if o.type=='MESH' for m in o.data.materials if m})
report={
 'fresh_open':'passed',
 'asset_path':str(asset),
 'scene':scene.name,
 'stable_collection_found':collection is not None,
 'stable_object_found':building.name,
 'asset_collection_tree':[c.name for c in cols],
 'asset_object_count':len(objects),
 'mesh_object_count':sum(o.type=='MESH' for o in objects),
 'material_count':len(material_names),
 'materials':material_names,
 'collection_geometry_bounds_xyz_m':bounds,
 'primary_shell_local_xy_bounds_m':local_building_xy,
 'primary_shell_vertices':len(building.data.vertices),
 'primary_shell_polygons':len(building.data.polygons),
 'procedural_assets_only':not any(getattr(i,'source','')=='FILE' for i in bpy.data.images),
 'preview_paths':['audit/whistler_hall/whistler_exterior.png','audit/whistler_hall/whistler_topdown.png']
}
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
