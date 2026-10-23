import bpy
from mathutils import Vector
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/hovde_hall.blend'))
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-0.2;s.world.color=(.16,.18,.2)
def aim(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def area(n,loc,t,power,size):
 d=bpy.data.lights.new(n,'AREA');o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,t);return o
def cam(loc,t,scale):
 d=bpy.data.cameras.new('ReviewCamera');o=bpy.data.objects.new('ReviewCamera',d);s.collection.objects.link(o);o.location=loc;aim(o,t);d.type='ORTHO';d.ortho_scale=scale;s.camera=o;return o
col=bpy.data.collections['Asset_hovde_hall'];target=(-9,15,8)
area('Key',(70,-60,75),target,6000,60);area('Fill',(-55,-25,40),target,3500,55);area('Rim',(10,100,50),target,4000,50)
c=cam((105,15,34),target,105)
s.render.filepath=str(P/'audit/batch3_hovde/exterior_material_preview.png');bpy.ops.render.render(write_still=True)
# Deliberate interior section cutaway of the modeled presidential office: the plan is an inferred illustration, not a source-verified floor plan.
for o in list(col.all_objects):
 if o is None: continue
 ok=o.name.startswith('HOVD_Pres_') and not o.name.endswith('_Ceiling')
 o.hide_render=not ok
# keep the actual model room shell and furniture, view diagonally into the cutaway
c.location=(34,-45,28);aim(c,(2,-5,5));c.data.ortho_scale=22
for o in s.objects:
 if o.type=='LIGHT': o.data.energy*=.65
s.render.filepath=str(P/'audit/batch3_hovde/presidential_office_cutaway.png');bpy.ops.render.render(write_still=True)
print('Rendered east entrance exterior and interior office cutaway')


