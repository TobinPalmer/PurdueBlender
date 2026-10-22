import bpy, math, json, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(os.path.join(ROOT,'../../../modular_source_snapshot.blend'),link=False) as (a,b):
    b.collections=['16_Loeb_Fountain_and_Founders_Park']
c=b.collections[0]; bpy.context.scene.collection.children.link(c)
names=[o.name for o in c.all_objects]
json.dump(names,open(ROOT+'/source_objects.json','w'),indent=2)
c.name='Fountain_Loeb'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/original_backup.blend')
for o in list(c.all_objects):
    if any(x in o.name for x in ['Laminar','Geyser','Bubbler','Water_Film','Granite_Bollard','Bollard_Nozzle']): bpy.data.objects.remove(o,do_unlink=True)
def move(o,name):
    o.name=name
    for co in list(o.users_collection): co.objects.unlink(o)
    c.objects.link(o)
    return o
def cyl(name,loc,r,d):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d,location=loc)
    return move(bpy.context.object,name)
limestone=bpy.data.materials.new('Loeb_Limestone_EvidenceSupported'); limestone.diffuse_color=(.65,.61,.51,1)
water=bpy.data.materials.new('Loeb_SimulatedWater'); water.use_nodes=True
p=water.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(.14,.4,.5,1); p.inputs['Transmission Weight'].default_value=.7; p.inputs['Roughness'].default_value=.12; p.inputs['IOR'].default_value=1.333
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.gravity=(0,0,-9.81); s.render.fps=24; s.frame_end=48
for i in range(24):
    a=2*math.pi*i/24; x,y=-50+8.2*math.cos(a),-255+8.2*math.sin(a)
    o=cyl('Loeb_Limestone_Bollard_%02d'%i,(x,y,.52),.28,.85); o.data.materials.append(limestone)
    o=cyl('Loeb_Liquid_Inflow_%02d'%i,(x,y,1.03),.19,.28)
    m=o.modifiers.new('Liquid inflow','FLUID'); m.fluid_type='FLOW'; f=m.flow_settings; f.flow_type='LIQUID'; f.flow_behavior='INFLOW'; f.use_initial_velocity=True; f.velocity_coord=(-4.8*math.cos(a),-4.8*math.sin(a),4.5)
    o.hide_render=True; o.display_type='WIRE'
bpy.ops.mesh.primitive_cube_add(size=1,location=(-50,-255,4.6)); dom=move(bpy.context.object,'Loeb_Mantaflow_Liquid_Domain'); dom.dimensions=(18.5,18.5,9.6)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
m=dom.modifiers.new('Baked physical liquid','FLUID'); m.fluid_type='DOMAIN'; d=m.domain_settings; d.domain_type='LIQUID'; d.resolution_max=64; d.cache_type='ALL'; d.cache_frame_start=1; d.cache_frame_end=48; d.cache_directory='//cache_attempt1'; d.use_mesh=True; d.mesh_scale=1
dom.data.materials.append(water)
# Dedicated collision plate: surface drains approximated by domain-open bottom.
bpy.ops.mesh.primitive_cube_add(size=1,location=(-50,-255,.02)); floor=move(bpy.context.object,'Loeb_Simulation_Deck_Collider'); floor.dimensions=(18,18,.18); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
m=floor.modifiers.new('Deck collision','FLUID'); m.fluid_type='EFFECTOR'; floor.hide_render=True; floor.display_type='WIRE'
bpy.ops.object.camera_add(location=(-23,-284,24)); cam=move(bpy.context.object,'Loeb_ReviewCamera'); cam.rotation_euler=(Vector((-50,-255,1.7))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=46; s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-50,-255,22)); light=move(bpy.context.object,'Loeb_ReviewLight'); light.data.energy=4000; light.data.shape='DISK'; light.data.size=20
s.world=bpy.data.worlds.new('Loeb_ReviewWorld'); s.world.color=(.35,.35,.35); s.render.engine='CYCLES'; s.cycles.samples=16; s.render.resolution_x=900; s.render.resolution_y=700; s.render.resolution_percentage=100
s['simulation_limitations']='Coarse 0.289m voxels; widened 0.19m emitter radius for numerical support, not surveyed nozzle bore. Velocities and 8.2m radius inferred; 24 limestone bollards supported by Purdue Alumnus. No dimensional or positional certification.'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/loeb.blend')
bpy.context.view_layer.objects.active=dom; bpy.ops.object.select_all(action='DESELECT'); dom.select_set(True)
print('BAKE START',flush=True); bpy.ops.fluid.bake_all(); print('BAKE END',flush=True)
stats=[]
for frame in [12,24,48]:
    s.frame_set(frame); deps=bpy.context.evaluated_depsgraph_get(); ev=dom.evaluated_get(deps); mesh=ev.to_mesh(); stats.append({'frame':frame,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons)}); ev.to_mesh_clear()
    s.render.filepath=ROOT+'/frame_%03d.png'%frame; bpy.ops.render.render(write_still=True)
json.dump(stats,open(ROOT+'/bake_verification.json','w'),indent=2)
s.frame_set(48); bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/loeb.blend')
