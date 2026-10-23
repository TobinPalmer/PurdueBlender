import bpy
from pathlib import Path
from mathutils import Vector
root=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); src=root/'modular/buildings/math_sciences.blend'; out=root/'audit/batch3_math'
bpy.ops.wm.open_mainfile(filepath=str(src)); asset=bpy.data.collections['Asset_math_sciences']
sc=bpy.data.scenes.new('Math Library Plan Review Round 4'); sc.collection.children.link(bpy.data.collections.new('Round 4 interior evidence objects'))
sel=sc.collection.children[-1]
for o in asset.all_objects:
 if ((o.name in {'MATH_Lib_Floor_Terrazzo','MATH_Lib_Border_Terrazzo','MATH_Lib_Wall_East','MATH_Lib_Wall_South','MATH_Lib_Wall_North'}) or o.name.startswith('MATH_2026_Library_') or o.name.startswith('MATH_2026_Inferred_Group_Room_') or o.name.startswith('MATH_2026_Library_2022_') or o.name.startswith('MATH_2026_Testing_Room_') or o.name.startswith('MATH_2026_Third_Floor_')): sel.objects.link(o)
# Workbench object colors separate room boundaries, shared study, shelving and group-room elements.
for o in sel.objects:
 n=o.name.lower()
 if 'boundar' in n or 'partition' in n or 'frame' in n: o.color=(.22,.27,.29,1)
 elif 'group_room_glaz' in n or 'door' in n: o.color=(.36,.66,.72,1)
 elif 'book_spines' in n: o.color=(.73,.38,.22,1)
 elif 'bookcase' in n: o.color=(.52,.33,.17,1)
 elif 'chair' in n or 'seat' in n: o.color=(.76,.54,.33,1)
 elif 'table' in n or 'carrel' in n: o.color=(.62,.40,.21,1)
 elif 'stair' in n or 'elevator' in n: o.color=(.42,.48,.51,1)
 elif 'floor' in n or 'carpet' in n or 'inlay' in n: o.color=(.82,.78,.68,1)
 else: o.color=(.68,.66,.59,1)
sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.light='STUDIO'; sc.display.shading.color_type='OBJECT'; sc.display.shading.show_shadows=False; sc.display.shading.show_cavity=True; sc.display.shading.cavity_type='WORLD'; sc.display.shading.curvature_ridge_factor=1.4; sc.display.shading.curvature_valley_factor=1.1; sc.display.shading.background_type='WORLD'; sc.world=bpy.data.worlds.new('Round 4 interior diagram world'); sc.world.color=(.95,.95,.95)
camd=bpy.data.cameras.new('Math plan diagram camera'); camd.type='ORTHO'; camd.ortho_scale=25
cam=bpy.data.objects.new('Math plan diagram camera',camd); sc.collection.objects.link(cam); cam.location=(.5,17.1,48); cam.rotation_euler=(Vector((.5,17.1,11))-cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
# Source labels are placed above model geometry in this review render only.
for label,x,y in [('311.3',-8.3,17.1),('311.4',-4.0,17.1),('311.5',1.8,17.1),('311.7',6.2,17.1),('311.8',9.0,17.1)]:
 d=bpy.data.curves.new('label '+label,'FONT'); d.body=label; d.size=.40; d.extrude=0; o=bpy.data.objects.new('Review label '+label,d); sc.collection.objects.link(o); o.location=(x,y,16.0); o.color=(.03,.04,.05,1)
sc.render.resolution_x=1500; sc.render.resolution_y=1500; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.render.filepath=str(out/'library_plan_round4.png')
bpy.context.window.scene=sc; bpy.ops.render.render(write_still=True); print('round4 plan diagram generated from reopened file, object count',len(sel.objects))

