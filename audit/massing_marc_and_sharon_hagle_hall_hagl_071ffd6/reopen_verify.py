import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
asset=root/'modular'/'buildings'/'massing_marc_and_sharon_hagle_hall_hagl_071ffd6.blend'
id='massing_marc_and_sharon_hagle_hall_hagl_071ffd6'; scene_name='Building_'+id; collection_name='Asset_'+id
scene=bpy.data.scenes.get(scene_name); col=bpy.data.collections.get(collection_name)
assert scene and col
objects=list(col.all_objects); assert len(objects)==1 and objects[0].type=='MESH'
obj=objects[0]; assert obj.name=='Marc and Sharon Hagle Hall (HAGL)'
assert tuple(round(v,4) for v in obj.location)==(0.0,0.0,0.0)
assert tuple(round(v,4) for v in obj.rotation_euler)==(0.0,0.0,0.0)
assert tuple(round(v,4) for v in obj.scale)==(1.0,1.0,1.0)
assert not obj.modifiers
assert not bpy.data.libraries
assert not any(image.source=='FILE' and image.filepath and not image.packed_file for image in bpy.data.images)
coords=[obj.matrix_world@Vector(corner) for corner in obj.bound_box]
bounds=[[min(v[k] for v in coords),max(v[k] for v in coords)] for k in range(3)]
result={'asset':str(asset),'reopened':True,'scene':scene.name,'collection':col.name,'object_count':len(objects),'object_name':obj.name,'object_type':obj.type,'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),'bounds_world_m':bounds,'location':list(obj.location),'rotation_euler':list(obj.rotation_euler),'scale':list(obj.scale),'modifiers':len(obj.modifiers),'linked_libraries':len(bpy.data.libraries),'unpacked_external_images':0,'preview_camera_or_light_in_asset_collection':any(o.type in {'CAMERA','LIGHT'} for o in objects)}
(root/'audit'/id/'reopen_check.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
