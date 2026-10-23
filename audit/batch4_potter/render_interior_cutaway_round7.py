import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/batch4_potter';P=R/'modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;c=bpy.data.collections['Asset_potter_engineering']
for o in list(bpy.data.objects):o.hide_render=True
# Registered 2016 existing-condition partitions, retained as trace meshes at each historic floor.
plans=['POTR_Historic2016_Plan53_MergedPartitions','POTR_Historic2016_Plan54_MergedPartitions','POTR_Historic2016_Plan55_MergedPartitions']
for n in plans:bpy.data.objects[n].hide_render=False
for o in c.all_objects:
 if o.name.startswith('POTR_2016_StairCore') and any(tag in o.name for tag in ('Level0_','Level1_','Level2_')):o.hide_render=False
# Subtle footprint datum outlines at three floor surfaces; they are illustration aids, not walls.
line=bpy.data.curves.new('POTR_R7_Interior_Floor_Datum_Outlines','CURVE');line.dimensions='3D';line.bevel_depth=.035;line.bevel_resolution=2
for z in (.7596,5.0268,9.294):
 pts=[(0,27,z),(22,27,z),(22,50,z),(0,50,z),(0,27,z)]
 sp=line.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
ob=bpy.data.objects.new('POTR_R7_Interior_Floor_Datum_Outlines',line);s.collection.objects.link(ob);ob.hide_render=False
mat=bpy.data.materials.new('POTR_R7_Floor_Datum_Material');mat.diffuse_color=(.18,.43,.60,1);mat.use_nodes=True;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.18,.43,.60,1);bs.inputs['Emission Color'].default_value=(.08,.22,.38,1);bs.inputs['Emission Strength'].default_value=.65;line.materials.append(mat)
# Room 160 collections: current Purdue page says the library use spans three floors; the old study identifies steel stack framing at the SW corner. Outline only a broad estimated anchor, not a room boundary.
libmat=bpy.data.materials.new('POTR_R7_Library_Anchor_Material');libmat.diffuse_color=(.95,.58,.12,1);libmat.use_nodes=True;lb=next(n for n in libmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');lb.inputs['Base Color'].default_value=(.95,.58,.12,1);lb.inputs['Emission Color'].default_value=(.45,.18,.025,1);lb.inputs['Emission Strength'].default_value=.6
lib=bpy.data.curves.new('POTR_R7_Room160_Approx_Stack_Zone','CURVE');lib.dimensions='3D';lib.bevel_depth=.055;lib.bevel_resolution=3
x1,x2,y1,y2=3.0,12.0,30.0,45.0
for z in (.7596,5.0268,9.294):
 pts=[(x1,y1,z),(x2,y1,z),(x2,y2,z),(x1,y2,z),(x1,y1,z)];sp=lib.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
for z0,z1 in [(.7596,5.0268),(5.0268,9.294)]:
 for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:
  sp=lib.splines.new('POLY');sp.points.add(1);sp.points[0].co=(x,y,z0,1);sp.points[1].co=(x,y,z1,1)
libob=bpy.data.objects.new('POTR_R7_Room160_Approx_Stack_Zone_Outline',lib);s.collection.objects.link(libob);libob.hide_render=False;lib.materials.append(libmat)
# Evidence lighting and an axonometric cutaway camera.
world=s.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.035,.05,.07,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
for name,loc,energy,size in [('POTR_R7_Interior_Key',(45,-30,65),5000,42),('POTR_R7_Interior_Fill',(15,80,40),3500,38)]:
 ld=bpy.data.lights.new(name,'AREA');lo=bpy.data.objects.new(name,ld);s.collection.objects.link(lo);lo.location=loc;ld.energy=energy*0.20;ld.shape='DISK';ld.size=size;lo.rotation_euler=(Vector((29,25,5))-lo.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('POTR_R7_Interior_Cutaway_Camera');cam=bpy.data.objects.new(camd.name,camd);s.collection.objects.link(cam);target=Vector((11.5,37.5,5.5));cam.location=target+Vector((38,-34,22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=31;s.camera=cam
# Camera-facing evidence captions.
right=cam.rotation_euler.to_matrix()@Vector((1,0,0));up=cam.rotation_euler.to_matrix()@Vector((0,1,0));toward=Vector((cam.location-target)).normalized();textmat=bpy.data.materials.new('POTR_R7_Interior_Label_Material');textmat.use_nodes=True;tb=next(n for n in textmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tb.inputs['Base Color'].default_value=(.92,.95,1,1);tb.inputs['Emission Color'].default_value=(.45,.62,.82,1);tb.inputs['Emission Strength'].default_value=.8
for title,v in [('LEVEL 1 — 2016 existing partitions',-8),('LEVEL 2 — 2016 existing partitions',0),('LEVEL 3 — 2016 existing partitions',8)]:
 cu=bpy.data.curves.new('POTR_R7_Level_Caption','FONT');cu.body=title;cu.size=.45;cu.extrude=.001;tx=bpy.data.objects.new('POTR_R7_Label_'+title[:7].replace(' ','_'),cu);s.collection.objects.link(tx);tx.location=target+right*10+up*v+toward*14;tx.rotation_euler=cam.rotation_euler;tx.data.materials.append(textmat);tx.hide_render=False
cu=bpy.data.curves.new('POTR_R7_Library_Caption','FONT');cu.body='ROOM 160 — CURRENT LIBRARY USE — APPROX. SW STACK ZONE';cu.size=.33;cu.extrude=.001;tx=bpy.data.objects.new('POTR_R7_Label_Room160',cu);s.collection.objects.link(tx);tx.location=target+right*1+up*11+toward*14;tx.rotation_euler=cam.rotation_euler;tx.data.materials.append(libmat);tx.hide_render=False
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1300;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.45;s.render.filepath=str(D/'interior_circulation_current_anchor_round7.png');bpy.ops.render.render(write_still=True)


