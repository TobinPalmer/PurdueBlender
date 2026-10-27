import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path.cwd(); asset_path=root/'modular/buildings/hicks_library.blend'; audit=root/'audit/batch2_hicks'
assert bpy.context.scene.name=='Building_hicks_library'
asset=bpy.data.collections['Asset_hicks_library']
assert len(asset.all_objects)>=340
sloped=bpy.data.objects['HIKS_R2_Four_Sloped_GIS_Masonry_Walls']
assert sloped.type=='MESH' and len(sloped.data.vertices)==40 and len(sloped.data.polygons)==20
assert bpy.data.collections['HIKS_R2_Sloped_Masonry_Envelope'] in sloped.users_collection; assert bpy.data.collections['HIKS_R2_Sloped_Masonry_Envelope'] in asset.children_recursive
assert all(o.type=='LIGHT' for o in bpy.data.collections['HIKS_R2_Review'].objects if o.type=='LIGHT')
missing=[]
for im in bpy.data.images:
 if im.source=='FILE' and im.packed_file is None and im.filepath and not Path(bpy.path.abspath(im.filepath)).exists(): missing.append(im.filepath)
assert not missing,missing
scene=bpy.context.scene; cam=bpy.data.objects['HIKS_R2_Exterior_Review']; scene.camera=cam
scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.filepath=str(audit/'fresh_open_exterior.png'); bpy.ops.render.render(write_still=True)
cam.location=(-14,-10,-2.25); cam.rotation_euler=(Vector((2,0,-4.25))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=34; scene.view_settings.exposure=0
scene.render.filepath=str(audit/'fresh_open_interior.png'); bpy.ops.render.render(write_still=True)
report={'sha256':hashlib.sha256(asset_path.read_bytes()).hexdigest(),'scene':scene.name,'collection':asset.name,'asset_object_count':len(asset.all_objects),'sloped_wall_vertices':len(sloped.data.vertices),'sloped_wall_faces':len(sloped.data.polygons),'missing_external_images':missing,'fresh_open_renders':['audit/batch2_hicks/fresh_open_exterior.png','audit/batch2_hicks/fresh_open_interior.png']}
(audit/'fresh_open_validation_r2.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
