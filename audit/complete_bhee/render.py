import bpy,math
from pathlib import Path
from mathutils import Vector
D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_bhee');p=D.parents[1]/'modular/buildings/electrical_engineering.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
c=bpy.data.cameras.new('Review');o=bpy.data.objects.new('Review',c);s.collection.objects.link(o);o.location=(130,130,120);o.rotation_euler=(Vector((0,0,5))-o.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=150;s.camera=o;s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(D/'overview.png');bpy.ops.render.render(write_still=True)
# first-floor cutaway hides upper exterior meshes/slabs
for ob in list(bpy.data.objects):
 if ob and ob.type=='MESH' and (min((ob.matrix_world @ Vector(corner)).z for corner in ob.bound_box)>4.5 or ('CourtyardWall' in ob.name)):ob.hide_render=True;ob.hide_set(True)
 o.location=(90,90,120);o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(D/'interior_cutaway.png');bpy.ops.render.render(write_still=True)
