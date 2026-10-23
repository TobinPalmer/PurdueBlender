import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/batch4_potter';P=R/'modular/buildings/potter_engineering.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.collections['Asset_potter_engineering']
for o in list(bpy.data.objects):o.hide_render=True
# Show actual stair geometry only; blue aperture outlines show which estimated floor openings serve each transition.
for o in c.all_objects:
 if o.name.startswith('POTR_2016_StairCore3_') and ('Level' in o.name or 'Basement_Landing' in o.name):o.hide_render=False
line=bpy.data.curves.new('POTR_R6_Aperture_Outlines','CURVE');line.dimensions='3D';line.bevel_depth=.025;line.bevel_resolution=2
for z,box in [(0.7596,(8.2,33.4,12.8,37.0)),(5.0268,(8.2,33.4,12.8,37.0)),(9.294,(8.2,33.4,12.8,37.0)),(13.4112,(8.9,33.85,12.1,36.55))]:
 x1,y1,x2,y2=box
 pts=[(x1,y1,z),(x2,y1,z),(x2,y2,z),(x1,y2,z),(x1,y1,z)]
 sp=line.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
ob=bpy.data.objects.new('POTR_R6_Estimated_Slab_Opening_Outlines',line);s.collection.objects.link(ob);ob.hide_render=False
blue=bpy.data.materials.new('POTR_R6_Aperture_Outline_Material');blue.diffuse_color=(.10,.45,.90,1);blue.use_nodes=True;bs=blue.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.10,.45,.90,1);bs.inputs['Emission Color'].default_value=(.08,.36,.85,1);bs.inputs['Emission Strength'].default_value=.8;line.materials.append(blue)
ld=bpy.data.lights.new('POTR_R6_Stairs_Key','AREA');lo=bpy.data.objects.new('POTR_R6_Stairs_Key',ld);s.collection.objects.link(lo);lo.location=(20,18,18);ld.energy=1100;ld.shape='DISK';ld.size=10;lo.rotation_euler=(Vector((10.5,35.2,4.45))-lo.location).to_track_quat('-Z','Y').to_euler()
ld2=bpy.data.lights.new('POTR_R6_Stairs_Fill','AREA');lo2=bpy.data.objects.new('POTR_R6_Stairs_Fill',ld2);s.collection.objects.link(lo2);lo2.location=(1,52,9);ld2.energy=500;ld2.size=10;lo2.rotation_euler=(Vector((10.5,35.2,4.45))-lo2.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('POTR_R6_Circulation_Camera');cam=bpy.data.objects.new('POTR_R6_Circulation_Camera',camd);s.collection.objects.link(cam);target=Vector((10.5,35.2,4.45));cam.location=target+Vector((14,-4,9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=20.0;s.camera=cam
right=cam.rotation_euler.to_matrix()@Vector((1,0,0));labelmat=bpy.data.materials.new('POTR_R6_Label_Material');labelmat.diffuse_color=(.68,.82,1,1);labelmat.use_nodes=True;lbs=labelmat.node_tree.nodes.get('Principled BSDF');lbs.inputs['Base Color'].default_value=(.68,.82,1,1);lbs.inputs['Emission Color'].default_value=(.22,.42,.72,1);lbs.inputs['Emission Strength'].default_value=.5
for name,z in [('B/L start — corridor unresolved',-3.914),('Floor 1',.7596),('Floor 2',5.0268),('Floor 3',9.294),('Penthouse — 4S04 / Room 401',13.4112)]:
 cu=bpy.data.curves.new('POTR_R6_Level_Label_Text','FONT');cu.body=name;cu.size=.23;cu.extrude=.001;txt=bpy.data.objects.new('POTR_R6_Label_'+name.split()[0],cu);s.collection.objects.link(txt);txt.rotation_euler=cam.rotation_euler;txt.location=Vector((10.5,35.2,z))+right*3.1;txt.data.materials.append(labelmat);txt.hide_render=False
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1300;s.render.resolution_y=1700;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.5;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.028,.04,.06,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35;s.render.filepath=str(D/'stairwell_circulation_round7.png');bpy.ops.render.render(write_still=True)





