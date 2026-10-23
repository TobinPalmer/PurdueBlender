import bpy,pathlib
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');A=P/'audit/batch3_elliott';S=P/'modular/buildings/elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene
# Temporary linked context only; this script does not save the file.
hovde=P/'modular/buildings/hovde_hall.blend'
with bpy.data.libraries.load(str(hovde),link=True) as (src,dst):dst.collections=['Asset_hovde_hall']
hc=next(c for c in dst.collections if c and c.name.startswith('Asset_hovde_hall'))
inst=bpy.data.objects.new('TEMP_Hovde_R4_Registration_Check',None);scene.collection.objects.link(inst);inst.instance_type='COLLECTION';inst.instance_collection=hc;inst.location=(61.197312832,28.344248772,0)
for o in bpy.data.objects:
    if o.name.startswith('ELLT_B3_'):o.hide_render=True
    if o.name.startswith('HOVD_') and not any(x in o.name for x in ['Wall','Base','Beltcourse','Roof','Door','Entrance','Portico','Walkway','Bridge','Stair','Infill']):o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
views=[('connection_top_r4',(35,45,180),(34,20,0),190),('connection_oblique_context_r4',(54,-23,28),(54,11,5.5),65)]
for name,loc,target,scale in views:
 d=bpy.data.cameras.new('TEMP_R4_'+name);d.type='ORTHO';d.ortho_scale=scale;c=bpy.data.objects.new('TEMP_R4_'+name,d);scene.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();scene.camera=c;scene.render.filepath=str(A/(name+'_r4.png'));bpy.ops.render.render(write_still=True)
print('Rendered',*[v[0] for v in views])
