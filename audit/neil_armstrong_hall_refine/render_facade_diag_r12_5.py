import bpy
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'; OUT=ROOT/'audit/neil_armstrong_hall_refine/facade_diag_west.png'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); scene=bpy.context.scene
for o in scene.objects:
 o.hide_render=True
for name in ['ARMS_West_Wall_North','ARMS_West_Beltcourse_4','ARMS_West_Beltcourse_9','ARMS_West_Beltcourse_14','ARMS_West_Beltcourse_19']:
 o=bpy.data.objects.get(name)
 if o:o.hide_render=False
# include any mesh intersecting face region, x [-63,-9], y [-4,-3], z [0,20]
from mathutils import Vector
for o in scene.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]; mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
 if mn[0]<-9 and mx[0]>-63 and mn[1]<-2.5 and mx[1]>-4.5 and mn[2]<21 and mx[2]>0 and o.name!='ARMS_Cantilever_Canopy_Deck':o.hide_render=False
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1300;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('diagnostic');scene.world.use_nodes=True;next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(0.4,0.4,0.4,1)
bpy.ops.object.light_add(type='AREA',location=(-35,-15,35));light=bpy.context.object;light.data.energy=12000;light.data.shape='DISK';light.data.size=40;light.rotation_euler=(Vector((-36,-3,10))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-36,-55,10));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=68;cam.rotation_euler=(Vector((-36,-3,10))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;scene.render.filepath=str(OUT);bpy.ops.render.render(write_still=True);print(OUT)
