import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
audit=root/'audit'/'batchC_national_soil_erosion'
scene=bpy.context.scene
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
def make_camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    obj.location=loc;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale
    return obj
old=scene.camera
cam=make_camera('TEMP | NSEL R2 final exterior',(74,-112,62),(0,0,3.0),88);scene.camera=cam
scene.render.filepath=str(audit/'nsel_revision_r2_exterior.png');bpy.ops.render.render(write_still=True)
cam.location=(4,-72,13);cam.rotation_euler=(Vector((-3,-25.4,3.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=27
scene.render.filepath=str(audit/'nsel_revision_r2_entry_detail.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,110);cam.rotation_euler=Vector((0,0,-1)).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=82
scene.render.filepath=str(audit/'nsel_revision_r2_roof_outline.png');bpy.ops.render.render(write_still=True)
scene.camera=old;data=cam.data;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(data)
