import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
for o in bpy.data.objects:o.hide_render=True
for n in ['RAWL_FloorSlab_L1_Ground']:bpy.data.objects[n].hide_render=False
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('RAWL_2026_Plan'):o.hide_render=False
s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
world=bpy.data.worlds.new('R2_Core_Plan_World');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.7,.72,.74,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
ld=bpy.data.lights.new('R2_Core_Plan_Sun','SUN');ld.energy=3;light=bpy.data.objects.new('R2_Core_Plan_Sun',ld);s.collection.objects.link(light);light.rotation_euler=(0,0,0)
camd=bpy.data.cameras.new('R2_Core_Plan_Camera');cam=bpy.data.objects.new('R2_Core_Plan_Camera',camd);s.collection.objects.link(cam);s.camera=cam
cam.location=(-7,-9,60);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=24
s.render.filepath=os.path.abspath('audit/batch4_rawls/interior_core_cutaway_round2.png');bpy.ops.render.render(write_still=True)
