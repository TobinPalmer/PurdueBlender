import bpy
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/batch4_potter';P=R/'modular/buildings/potter_engineering.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.collections['Asset_potter_engineering']
for o in list(bpy.data.objects):o.hide_render=True
plan=bpy.data.objects['POTR_Historic2016_Plan53_MergedPartitions'];plan.hide_render=False
mat=bpy.data.materials.new('R7_plan_neutral');mat.diffuse_color=(.38,.45,.53,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.27,.34,.42,1);bs.inputs['Roughness'].default_value=.8;plan.data.materials.clear();plan.data.materials.append(mat)
mat2=bpy.data.materials.new('R7_plan_marker');mat2.diffuse_color=(1,.42,.03,1);mat2.use_nodes=True;bs=mat2.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(1,.27,.01,1);bs.inputs['Emission Color'].default_value=(1,.14,.005,1);bs.inputs['Emission Strength'].default_value=1
cu=bpy.data.curves.new('R7_anchor_outline','CURVE');cu.dimensions='3D';cu.bevel_depth=.10;cu.bevel_resolution=2
sp=cu.splines.new('POLY');pts=[(3,30,.86),(12,30,.86),(12,45,.86),(3,45,.86),(3,30,.86)];sp.points.add(4)
for p,co in zip(sp.points,pts):p.co=(*co,1)
edge=bpy.data.objects.new('R7_approx_library_outline',cu);s.collection.objects.link(edge);edge.data.materials.append(mat2);edge.hide_render=False
world=s.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.018,.025,.035,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
ld=bpy.data.lights.new('R7_plan_key','AREA');lo=bpy.data.objects.new('R7_plan_key',ld);s.collection.objects.link(lo);lo.location=(11,39.5,30);ld.energy=1000;ld.size=22;lo.rotation_euler=(Vector((11,39.5,0))-lo.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('R7_plan_camera');cam=bpy.data.objects.new('R7_plan_camera',camd);s.collection.objects.link(cam);cam.location=(11,39.5,35);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=31;s.camera=cam
for name,body,size,loc in [('R7_plan_title','LEVEL 1  |  2016 EXISTING PLAN',.62,(3,51,.8)),('R7_plan_legend','ORANGE OUTLINE: APPROX. ROOM 160 / SW STACK USE ZONE',.36,(12.6,27.5,.8))]:
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;tx=bpy.data.objects.new(name,cu);s.collection.objects.link(tx);tx.location=loc;tx.data.materials.append(mat2);tx.hide_render=False
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.render.filepath=str(D/'floor1_plan_current_library_anchor_round7.png');bpy.ops.render.render(write_still=True)
