"""Render refreshed exterior, roof, and level-separated interior views from the saved asset."""
import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent; ASSET=ROOT/'modular/buildings/physics_building_phys_3bf42f3.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); scene=bpy.context.scene; asset=bpy.data.collections['Asset_physics_building']
shell=bpy.data.objects['PHYS | GIS footprint brick envelope']; sign=bpy.data.objects['PHYS NW | limestone PHYSICS sign panel']; sc=sign.location.copy()
base=[v.co.copy() for v in shell.data.vertices if abs(v.co.z)<1e-5]; axis=(base[2]-base[0]).normalized(); axis.z=0; axis.normalize(); normal=Vector((-axis.y,axis.x,0)); rot=math.atan2(axis.y,axis.x)
# Site context exists only for review renders, outside the linked asset collection.
def material(name,color,rough=.8,metallic=0):
 m=bpy.data.materials.new('REVIEW R2 | '+name); m.diffuse_color=(*color,1); m.use_nodes=True; n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); n.inputs['Base Color'].default_value=(*color,1); n.inputs['Roughness'].default_value=rough; n.inputs['Metallic'].default_value=metallic; return m
grass=material('campus turf',(.15,.28,.12)); roadmat=material('asphalt',(.18,.19,.20),.9); walkmat=material('concrete walk',(.48,.47,.43)); curbmat=material('stone curb',(.6,.58,.52)); hedge=material('ornamental hedge',(.08,.19,.05)); trunkmat=material('tree bark',(.17,.10,.05)); leaves=material('tree foliage',(.12,.24,.07)); iron=material('black rail',(.035,.045,.04),.55,.25)
def cube(name,loc,dims,mat,angle=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.z=angle;o.data.materials.append(mat);return o
bpy.ops.mesh.primitive_plane_add(size=500,location=(0,0,-.17)); bpy.context.object.name='REVIEW R2 | lawn'; bpy.context.object.data.materials.append(grass)
front=Vector((sc.x,sc.y,0))
walk=front+normal*4.1;walk.z=-.055;cube('REVIEW R2 | sidewalk',walk,(132,2.6,.11),walkmat,rot)
plant=front+normal*7.4;plant.z=-.07;cube('REVIEW R2 | planting strip',plant,(132,2,.08),grass,rot)
curb=front+normal*9;curb.z=.01;cube('REVIEW R2 | granite curb',curb,(132,.28,.20),curbmat,rot)
road=front+normal*16;road.z=-.07;cube('REVIEW R2 | Northwestern Avenue asphalt',road,(180,13,.08),roadmat,rot)
for i,s in enumerate((-52,-44,-36,-28,-20,20,28,36,44,52)):
 p=front+axis*s+normal*7.5;p.z=.50;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=p);o=bpy.context.object;o.name=f'REVIEW R2 | hedge {i:02d}';o.scale=(1.35,.72,.66);o.data.materials.append(hedge)
for i,s in enumerate((-49,49)):
 p=front+axis*s+normal*9;p.z=0;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.18,depth=3.4,location=p+Vector((0,0,1.7)));bpy.context.object.data.materials.append(trunkmat)
 q=p+Vector((0,0,3.8));bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1.8,location=q);o=bpy.context.object;o.scale=(1,.85,1.15);o.data.materials.append(leaves)
rail=front+normal*8.55;rail.z=0
for s in range(-62,63,5):
 p=rail+axis*s;p.z=.63;cube('REVIEW R2 | fence post',p,(.09,.09,1.25),iron,rot)
for z in (.38,.92):
 p=rail+normal*.12;p.z=z;cube('REVIEW R2 | fence rail',p,(126,.075,.075),iron,rot)
scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.46,.62,.86,1);bg.inputs['Strength'].default_value=.72
scene.render.engine='CYCLES';scene.cycles.samples=22;scene.render.resolution_x=1700;scene.render.resolution_y=1120;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
camera=next(o for o in bpy.data.objects if o.type=='CAMERA')
def area(name,loc,power,size,target):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('REVIEW R2 | facade key',front+normal*75+Vector((0,0,48)),26000,52,sc)
area('REVIEW R2 | facade fill',front+normal*95-axis*42+Vector((0,0,27)),15000,42,sc)
area('REVIEW R2 | roof rim',front-normal*35+Vector((0,0,60)),14500,38,(0,0,13))
def render(name,loc,target,lens=55):
 camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='PERSP';camera.data.lens=lens;scene.camera=camera;scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
# Wider yet closer-to-photo road frontage, then details at the main doors.
tar=sc.copy();tar.z=6.1
if not (OUT/'physics_building_front_nw_preview.png').exists(): render('physics_building_front_nw_preview.png',front+normal*150+Vector((0,0,17.5)),tar,80)
entry=sc.copy();entry.z=3.3
if not (OUT/'physics_building_entry_detail_preview.png').exists(): render('physics_building_entry_detail_preview.png',front+normal*46+Vector((0,0,8.7)),entry,68)
roof_target=Vector((0,0,14.2));
if not (OUT/'physics_building_roof_detail_preview.png').exists(): render('physics_building_roof_detail_preview.png',front+normal*95+Vector((0,0,38)),roof_target,62)
# Interior plan view: isolate one level of the source-plan-informed schematic, not a false all-floor pile.
hidden=[]
external_prefixes=('PHYS | GIS footprint brick envelope','PHYS | estimated sloped red tile roof','PHYS | GIS-aligned main clay ridge cap','PHYS | recessed dark sash glazing','PHYS | pale limestone window surrounds','PHYS | limestone story belt','PHYS | limestone water table','PHYS | limestone cornice','PHYS R2 | eave shadow fascia','PHYS R2 | eave limestone crown','PHYS NW | entrance','PHYS NW | limestone PHYSICS sign panel','PHYS NW | broad entry stair','PHYS NW | basement sash','PHYS R2 | tall divided sash frames','PHYS R2 | entrance','PHYS | long clay ridge cap','PHYS | secondary hip ridge','PHYS | skybridge')
for o in bpy.data.objects:
 if o is None: continue
 if any(o.name.startswith(k) for k in external_prefixes): hidden.append((o,o.hide_render));o.hide_render=True
for o in list(scene.objects):
 if o.name.startswith('REVIEW R2 |'):hidden.append((o,o.hide_render));o.hide_render=True
for o in asset.all_objects:
 if o is None: continue
 if 'floor plate' in o.name:
  want=o.name=='PHYS R2 | ground floor plate';hidden.append((o,o.hide_render));o.hide_render=not want
 if 'floor-plan partitions' in o.name:
  want=o.name=='PHYS R2 | ground floor-plan partitions';hidden.append((o,o.hide_render));o.hide_render=not want
 if 'schematic interior' in o.name:
  hidden.append((o,o.hide_render));o.hide_render=o.location.z>4.2
 if o.name.startswith('PHYS R2 | first ') or o.name.startswith('PHYS R2 | second '):
  hidden.append((o,o.hide_render));o.hide_render=True
camera.location=(0,0,75);camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=135;scene.render.resolution_x=1700;scene.render.resolution_y=1450;scene.camera=camera;scene.render.filepath=str(OUT/'physics_building_interior_ground_plan_preview.png');bpy.ops.render.render(write_still=True)
for o,state in hidden:o.hide_render=state
print('Rendered exterior, entrance closeup, pitched-roof detail, and single-floor interior plan from a fresh asset reopen; campus context remains review-only.')
