import bpy
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/batch4_potter';P=R/'modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.collections['Asset_potter_engineering']
for o in list(bpy.data.objects):o.hide_render=True
names=['POTR_Official_864_Roof','POTR_2016_StairCore3_Level3_Flight','POTR_2016_StairCore3_Level3_Handrails','POTR_2016_StairCore3_Level3_UpperLanding','POTR_2016_StairCore3_Penthouse_Landing_4S04_Estimate','POTR_4S04_Enclosure_Walls_183sf_Estimate']
for n in names:
 o=c.objects.get(n)
 if o:o.hide_render=False
# Render-only palette.
def material(name,color,emission=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.78
 if emission:bs.inputs['Emission Color'].default_value=(*emission,1);bs.inputs['Emission Strength'].default_value=.45
 return m
roofmat=material('R8_render_roof',(.18,.24,.32));wallmat=material('R8_render_penthouse_walls',(.57,.43,.29));stairmat=material('R8_render_stairs',(.76,.79,.82));landmat=material('R8_render_landing',(.12,.39,.52),(.06,.35,.62));metalmat=material('R8_render_metal',(.08,.11,.14));
for n,m in [('POTR_Official_864_Roof',roofmat),('POTR_4S04_Enclosure_Walls_183sf_Estimate',wallmat),('POTR_2016_StairCore3_Level3_Flight',stairmat),('POTR_2016_StairCore3_Level3_UpperLanding',landmat),('POTR_2016_StairCore3_Penthouse_Landing_4S04_Estimate',landmat),('POTR_2016_StairCore3_Level3_Handrails',metalmat)]:
 o=c.objects[n]
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
 elif o.type=='CURVE':o.data.materials.clear();o.data.materials.append(m)
# Hypothesis/path graphic: step to the landing, turn toward the centered west opening.
pathmat=material('R8_render_path',(1,.42,.03),(1,.18,.005));cu=bpy.data.curves.new('R8_landing_turn_proxy','CURVE');cu.dimensions='3D';cu.bevel_depth=.035;cu.bevel_resolution=3;sp=cu.splines.new('POLY');pts=[(9.65,35.725,13.55),(9.65,35.2,13.55),(9.28,35.2,13.55)];sp.points.add(2)
for p,co in zip(sp.points,pts):p.co=(*co,1)
path=bpy.data.objects.new('R8_landing_turn_proxy',cu);s.collection.objects.link(path);path.data.materials.append(pathmat)
world=s.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.025,.035,.05,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
ld=bpy.data.lights.new('R8_interface_key','AREA');lo=bpy.data.objects.new('R8_interface_key',ld);s.collection.objects.link(lo);lo.location=(10.5,35.2,24);ld.energy=750;ld.size=8;lo.rotation_euler=(Vector((10.5,35.2,13.4))-lo.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('R8_interface_camera');cam=bpy.data.objects.new('R8_interface_camera',camd);s.collection.objects.link(cam);cam.location=(10.5,35.2,28);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=8;s.camera=cam
labelmat=material('R8_render_label',(.95,.93,.86),(.5,.4,.18))
for name,body,size,loc in [('R8_title','S03 / 4S04 UPPER APPROACH — ESTIMATED PLAN',.20,(8.1,38.1,13.7)),('R8_note','1.2 m ENTRY ESTIMATE — LANDING TURN PATH PROXY',.16,(8.1,32.15,13.7))]:
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;tx=bpy.data.objects.new(name,cu);s.collection.objects.link(tx);tx.location=loc;tx.data.materials.append(labelmat)
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.render.filepath=str(D/'round8_s03_upper_interface_plan.png');bpy.ops.render.render(write_still=True)
