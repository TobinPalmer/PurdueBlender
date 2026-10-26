"""Render exterior and plan evidence views of the saved MRI1 asset."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'mri_modular_facility'
obj=bpy.data.objects['MRI Modular Facility (MRI1)']
pts=[obj.matrix_world@v.co for v in obj.data.vertices]
lo=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
hi=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
center=(lo+hi)*.5
scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'
scene.display.shading.studio_light='paint.sl'; scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='WORLD'
scene.render.resolution_x=1400; scene.render.resolution_y=1050; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False

def aim(ob,target): ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
 ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=loc;aim(ob,center);return ob
area('MRI1_Audit_Key',center+Vector((28,-30,40)),520,25)
area('MRI1_Audit_Fill',center+Vector((-28,15,25)),175,22)
cd=bpy.data.cameras.new('MRI1_Audit_Camera');cam=bpy.data.objects.new('MRI1_Audit_Camera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.ortho_scale=33
cam.location=center+Vector((45,-35,31));aim(cam,center)
scene.render.filepath=str(AUDIT/'preview_exterior.png');bpy.ops.render.render(write_still=True)
cd.ortho_scale=33;cam.location=center+Vector((0,0,55));aim(cam,center-Vector((0,0,2)))
scene.render.filepath=str(AUDIT/'preview_plan.png');bpy.ops.render.render(write_still=True)
