import bpy, json, math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]
path=root/'modular'/'buildings'/'psychological_sciences.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
scene=bpy.context.scene
asset=bpy.data.collections.get('Asset_psychological_sciences')
issues=[]
if asset is None: issues.append('Export collection missing')
if asset and asset.name not in scene.collection.children: issues.append('Export collection not linked under scene root')
objects=list(asset.all_objects) if asset else []
geometry=[o for o in objects if o.type in {'MESH','CURVE','FONT','SURFACE','META'}]
points=[o.matrix_world @ Vector(c) for o in geometry for c in o.bound_box]
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)] if points else None
materials={m.name for o in geometry for m in o.data.materials if m}
for o in geometry:
    if o.type=='MESH' and (len(o.data.vertices)==0 or len(o.data.polygons)==0): issues.append(f'empty mesh: {o.name}')
    if not o.data.materials: issues.append(f'unmaterialed geometry: {o.name}')
external_libraries=[lib.filepath for lib in bpy.data.libraries if lib.filepath]
image_paths=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath]
summary={
 'status':'PASS' if not issues and asset and bounds and not external_libraries and not image_paths else 'REVIEW',
 'file':str(path), 'scene':scene.name, 'export_collection':asset.name if asset else None,
 'export_collection_direct_objects':len(asset.objects) if asset else 0, 'export_collection_objects_including_children':len(objects),
 'geometry_object_count':len(geometry), 'mesh_count':sum(o.type=='MESH' for o in geometry),
 'mesh_vertices':sum(len(o.data.vertices) for o in geometry if o.type=='MESH'),
 'mesh_polygons':sum(len(o.data.polygons) for o in geometry if o.type=='MESH'),
 'material_count':len(materials),'material_names':sorted(materials),
 'local_bounds_m':bounds,
 'expected_origin_world_m':[-106.6966,-48.275,0.0],
 'scene_declared_origin_world_m':list(scene.get('bounds_origin_world_m',[])),
 'root_coordinate_frame':scene.get('building_id'),
 'linked_libraries':external_libraries,'external_image_paths':image_paths,
 'issues':issues,
}
(root/'audit'/'new_psyc'/'reopen_check.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
