import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); D=P/'modular/fountains/engineering'; D.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'modular_source_snapshot.blend'))
source=bpy.data.collections['08_Engineering_Fountain_and_Mall']
names=[o.name for o in source.all_objects if o.name.startswith(('Fountain_','Engineering_Fountain_','EngFountain_'))]
(D/'replaced_objects.json').write_text(json.dumps(names,indent=2))
bpy.data.libraries.write(str(D/'original_fountain_backup.blend'),set(source.all_objects),fake_user=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.fps=24;s.frame_start=1;s.frame_end=96;s.gravity=(0,0,-9.81)
c=bpy.data.collections.new('Fountain_Engineering');s.collection.children.link(c)
x=(-86.91385039624882+86.9137)*84810.60416539927;y=(40.4284649888877-40.4274)*111040

def mat(n,color,metal=0,rough=.5,trans=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Transmission Weight'].default_value=trans;p.inputs['IOR'].default_value=1.333;return m
stone=mat('EF_Architectural_concrete',(.62,.59,.52));steel=mat('EF_Stainless',(.65,.7,.74),.95,.14);water=mat('EF_Clear_water',(.65,.85,.94),0,.07,1);brick=mat('EF_Brick',(.27,.12,.07))
def own(o,n,m=None):
 o.name=n
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o)
 if m:o.data.materials.append(m)
 return o
def mesh(n,v,f,m):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);c.objects.link(o);me.materials.append(m);return o
def eff(o):
 mod=o.modifiers.new('Liquid collision','FLUID');mod.fluid_type='EFFECTOR'
 return o
# Correct sculpture height 38ft=11.5824m. Remaining horizontal profiles estimated from official photograph.
for a in [45,135,225,315]:
 t=math.radians(a);r=Vector((math.cos(t),math.sin(t),0));q=Vector((-math.sin(t),math.cos(t),0));v=[];f=[]
 for i in range(65):
  u=i/64;z=.12+u*11.5824;ri=.85+.28*u;ro=1.5+6.0*(1-u)**2.7;th=.64-.28*u
  for rr,tt in [(ri,-th/2),(ro,-th/2),(ro,th/2),(ri,th/2)]:
   p=Vector((x,y,z))+r*rr+q*tt;v.append(tuple(p))
  if i:
   k=4*i
   for j in range(4):f.append((k-4+j,k-4+(j+1)%4,k+(j+1)%4,k+j))
 f += [(3,2,1,0),(256,257,258,259)]
 eff(mesh('EF_Curved_fin_'+str(a),v,f,stone))
for a in [0,90,180,270]:
 v=[];f=[]
 for i in range(49):
  t=math.radians(a-32+i*64/48)
  for rr,z in [(7.4,.12),(8,.12),(8,.88),(7.4,.88)]:v.append((x+rr*math.cos(t),y+rr*math.sin(t),z))
  if i:
   k=4*i
   for j in range(4):f.append((k-4+j,k-4+(j+1)%4,k+(j+1)%4,k+j))
 f += [(3,2,1,0),(192,193,194,195)];mesh('EF_Perimeter_wall_'+str(a),v,f,stone)
bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=9,depth=.12,location=(x,y,.02));own(bpy.context.object,'EF_Paved_deck',brick)
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.41,depth=3.05,location=(x,y,1.645));own(bpy.context.object,'EF_Safety_cylinder',steel)
# Domain bounded to the central spray, underside open to represent drain. No fabricated static water geometry.
bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,7));domain=own(bpy.context.object,'EF_Liquid_domain',water);domain.dimensions=(9,9,14);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
m=domain.modifiers.new('Mantaflow Liquid','FLUID');m.fluid_type='DOMAIN';ds=m.domain_settings;ds.domain_type='LIQUID';ds.resolution_max=192;ds.cache_type='MODULAR';ds.cache_directory='//cache/attempt1';ds.cache_frame_start=1;ds.cache_frame_end=96;ds.use_mesh=True;ds.mesh_scale=2;ds.cache_data_format='UNI';ds.cache_mesh_format='BOBJECT';ds.use_collision_border_bottom=False;ds.timesteps_max=8
# True historical 588 US gpm=.03710m3/s. 13.5m/s at3.19m gives ballistic apex12.48m. Actual nozzle radius .0296m is underresolved.
# Coarse-grid emitter .08m is explicitly enlarged to survive voxelization: simulated discharge not calibrated.
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.08,location=(x,y,3.19));flow=own(bpy.context.object,'EF_Central_jet_inflow');flow.scale.z=1.5;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
f=flow.modifiers.new('Liquid inflow','FLUID');f.fluid_type='FLOW';fs=f.flow_settings;fs.flow_type='LIQUID';fs.flow_behavior='INFLOW';fs.use_initial_velocity=True;fs.velocity_coord=(0,0,13.5);fs.surface_distance=0;flow.hide_render=True
# Camera and light outside export collection.
bpy.ops.object.camera_add(location=(x+24,y-31,18));cam=bpy.context.object;cam.name='Engineering_preview';cam.rotation_euler=(Vector((x,y,5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=47;s.camera=cam
bpy.ops.object.light_add(type='SUN',location=(x,y,20));bpy.context.object.rotation_euler=(.45,-.3,-.5);bpy.context.object.data.energy=3
s.world=bpy.data.worlds.new('EF_World');s.world.color=(.22,.28,.35);s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
s['uncertainty']='Map-centered placement provisional, fin/deck plan inferred from single official image; no survey or hydraulic plans. Emitter enlarged at finite resolution.'
bpy.ops.wm.save_as_mainfile(filepath=str(D/'engineering.blend'))
bpy.context.view_layer.objects.active=domain;bpy.ops.object.select_all(action='DESELECT');domain.select_set(True)
print('BAKE_DATA_BEGIN',flush=True);bpy.ops.fluid.bake_data();print('BAKE_MESH_BEGIN',flush=True);bpy.ops.fluid.bake_mesh();print('BAKE_DONE',flush=True)
s.frame_set(72);bpy.ops.wm.save_as_mainfile(filepath=str(D/'engineering.blend'))
