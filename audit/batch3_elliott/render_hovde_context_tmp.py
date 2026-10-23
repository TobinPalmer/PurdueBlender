import bpy,pathlib
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');AUD=P/'audit/batch3_elliott';bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/elliott_hall_of_music.blend'))
# Append a temporary linked Hovde collection instance in Elliott's local frame.
hovde=P/'modular/buildings/hovde_hall.blend'
with bpy.data.libraries.load(str(hovde),link=True) as (src,dst): dst.collections=['Asset_hovde_hall']
coll=next(c for c in dst.collections if c and c.name.startswith('Asset_hovde_hall'))
inst=bpy.data.objects.new('TEMP_Hovde_Adjacent_Overview',None);bpy.context.scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=coll;inst.location=(61.197312832,28.344248772,0)
# Hide interior detail for legible urban connection review.
for o in bpy.data.objects:
 if o.name.startswith('ELLT_B3_'): o.hide_render=True
 if o.name.startswith('HOVD_') and not any(x in o.name for x in ['Wall','Base','Beltcourse','Roof','Door','Entrance','Portico','Walkway','Bridge','Stair','Infill']): o.hide_render=True
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
for name,loc,target,scale in [('adjacent_top',(18,20,180),(20,20,0),175),('connection_oblique',(80,-25,65),(47,15,7),95)]:
 d=bpy.data.cameras.new('TEMP_'+name);d.type='ORTHO';d.ortho_scale=scale;c=bpy.data.objects.new('TEMP_'+name,d);scene.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();scene.camera=c;scene.render.filepath=str(AUD/('round4_'+name+'.png'));bpy.ops.render.render(write_still=True)
