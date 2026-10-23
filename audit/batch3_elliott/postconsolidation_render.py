import bpy, pathlib
from mathutils import Vector
ROOT=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');SRC=ROOT/'modular/buildings/elliott_hall_of_music.blend';AUD=ROOT/'audit/batch3_elliott'
bpy.ops.wm.open_mainfile(filepath=str(SRC));scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1250;scene.render.resolution_y=875;scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
camdata=bpy.data.cameras.new('ELLT_PostMerge_Camera');cam=bpy.data.objects.new('ELLT_PostMerge_Camera',camdata);scene.collection.objects.link(cam);cam.location=(126,-135,82);camdata.type='ORTHO';camdata.ortho_scale=155;cam.rotation_euler=(Vector((0,2,11))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;scene.render.filepath=str(AUD/'exterior_final_reopened.png');bpy.ops.render.render(write_still=True)
print('export',[(o.name,len(o.data.vertices),len(o.data.polygons)) for o in bpy.data.collections['Asset_elliott_hall_of_music'].objects if o.type=='MESH' and o.name.startswith(('ELLT_EXT_','ELLT_FIN_'))])
