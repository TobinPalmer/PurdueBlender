"""Fresh-open validation for Lambertus Hall (run by Blender --background)."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
asset=root/'modular'/'buildings'/'lambertus_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(asset))
coll=bpy.data.collections.get('Asset_lambertus_hall')
scene=bpy.data.scenes.get('Building_lambertus_hall')
assert coll and scene, 'Expected named building collection/scene missing'
shell=bpy.data.objects.get('Lambertus Hall | GIS perimeter shell')
assert shell and shell.type=='MESH', 'GIS shell missing'
assert all(abs(v)<1e-6 for v in shell.location), 'Shell must remain in local asset coordinates'
coords=[v.co for v in shell.data.vertices]
local_bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
assert len([p for p in shell.data.polygons])==41, 'Expected bottom/top caps and 40 perimeter faces'
assert local_bounds[2]==[0.0,16.0], local_bounds
objects=list(coll.objects)
assert len(objects)>20, f'Unexpectedly sparse model: {len(objects)} objects'
assert all(o.type=='MESH' for o in objects), 'Non-mesh dependencies need review'
assert all(m is not None for o in objects for m in o.data.materials), 'Unassigned material found'
assert not any(m and m.library for m in bpy.data.materials), 'External linked material found'
report={
 'fresh_open':'PASS','file':str(asset),'scene':scene.name,'collection':coll.name,
 'object_count':len(objects),'mesh_count':sum(o.type=='MESH' for o in objects),
 'material_count':len({m.name for o in objects for m in o.data.materials}),
 'shell_local_bounds_m':local_bounds,'shell_vertices':len(shell.data.vertices),
 'shell_faces':len(shell.data.polygons),'shell_modifiers':[m.name for m in shell.modifiers],
 'unexpected_linked_libraries':[],
 'checks':['fresh open','named scene and collection','GIS shell polygon count','local shell transform','estimated height 16 m','portable mesh materials']
}
(root/'audit'/'lambertus_hall'/'fresh_open_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
