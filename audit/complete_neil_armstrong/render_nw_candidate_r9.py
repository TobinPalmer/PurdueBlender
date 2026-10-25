import bpy,os
from mathutils import Vector
ROOT=r'C:\\Users\\Tobin\\Documents\\Blender\\PurdueMap'
asset=os.path.join(ROOT,'modular','buildings','neil_armstrong_hall.blend'); out=os.path.join(ROOT,'audit','complete_neil_armstrong','renders_r9')
bpy.ops.wm.open_mainfile(filepath=asset); sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'; sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-0.3
world=sc.world or bpy.data.worlds.new('R9_Facade_Review_World');sc.world=world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(0.2,0.25,0.32,1);bg.inputs['Strength'].default_value=0.25
camd=bpy.data.cameras.new('R9_NW_Camera_Data');cam=bpy.data.objects.new('R9_NW_Camera',camd);sc.collection.objects.link(cam);cam.location=(-154,47.3,1.7);target=Vector((-10,10,8.5));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.type='PERSP';camd.lens=48;camd.sensor_width=36;camd.clip_end=1200;sc.camera=cam
ld=bpy.data.lights.new('R9_NW_Key_Data','AREA');lo=bpy.data.objects.new('R9_NW_Key',ld);sc.collection.objects.link(lo);lo.location=(-80,-25,75);ld.energy=4800;ld.shape='DISK';ld.size=50;lo.rotation_euler=(Vector((0,0,8))-Vector(lo.location)).to_track_quat('-Z','Y').to_euler()
filld=bpy.data.lights.new('R9_NW_Fill_Data','AREA');fill=bpy.data.objects.new('R9_NW_Fill',filld);sc.collection.objects.link(fill);fill.location=(35,60,42);filld.energy=1800;filld.shape='DISK';filld.size=65;fill.rotation_euler=(Vector((0,0,8))-Vector(fill.location)).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=os.path.join(out,'facade_nw_local_front_r9.png');bpy.ops.render.render(write_still=True);print(sc.render.filepath)
