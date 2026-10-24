import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
audit=root/'audit'/'batchC_national_soil_erosion'
scene=bpy.context.scene
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
def camera(name,loc,target,scale):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale
    return o
old=scene.camera
cam=camera('TEMP | NSEL R3 full exterior',(74,-112,62),(0,0,3),88);scene.camera=cam
scene.render.filepath=str(audit/'nsel_revision_r3_exterior.png');bpy.ops.render.render(write_still=True)
cam.location=(-3.5,-62,12);cam.rotation_euler=(Vector((-3.5,-24.65,4.0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=30
scene.render.filepath=str(audit/'nsel_revision_r3_exterior_name.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,110);cam.rotation_euler=Vector((0,0,-1)).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=82
scene.render.filepath=str(audit/'nsel_revision_r3_roof_outline.png');bpy.ops.render.render(write_still=True)
allowed=('SOIL | R2 flume','SOIL | R2 overhead instrument','SOIL | R2 adjustable instrument','SOIL | R2 instrument gantry','SOIL | R3')
saved=[]
for obj in bpy.data.objects:
    saved.append((obj,obj.hide_render))
    obj.hide_render=not (obj.name.startswith(allowed) or (obj.type=='LIGHT' and obj.name.startswith('SOIL Preview')))
cam.location=(-46,-25,24);cam.rotation_euler=(Vector((-25.4,0,2.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=43
bpy.context.view_layer.update()
scene.render.filepath=str(audit/'nsel_revision_r3_hydraulics_high_bay.png');bpy.ops.render.render(write_still=True)
for obj,value in saved:obj.hide_render=value
scene.camera=old;data=cam.data;bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(data)
