import bpy,os,math
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
for o in bpy.data.objects:o.hide_render=True
for n in ['RAWL_FloorSlab_L2']:bpy.data.objects[n].hide_render=False
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
w=bpy.data.worlds.new('R2_Slab_Diagnostic_World');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.75,.77,.8,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=1
ld=bpy.data.lights.new('R2_Slab_Diagnostic_Sun','SUN');ld.energy=3;o=bpy.data.objects.new('R2_Slab_Diagnostic_Sun',ld);s.collection.objects.link(o);o.rotation_euler=(0,0,0)
cD=bpy.data.cameras.new('R2_Slab_Diagnostic_Camera');c=bpy.data.objects.new('R2_Slab_Diagnostic_Camera',cD);s.collection.objects.link(c);s.camera=c;c.location=(8,-2,100);c.rotation_euler=(0,0,0);c.data.type='ORTHO';c.data.ortho_scale=90
s.render.filepath=os.path.abspath('audit/batch4_rawls/floor_slab_L2_top_round2.png');bpy.ops.render.render(write_still=True)
# now show ground slab and plan walls with exterior and upper slab hidden
for o in bpy.data.objects:o.hide_render=True
bpy.data.objects['RAWL_FloorSlab_L1_Ground'].hide_render=False
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('RAWL_2026_Plan'):o.hide_render=False
c.location=(-7,-9,60);c.rotation_euler=(0,0,0);c.data.ortho_scale=30
s.render.filepath=os.path.abspath('audit/batch4_rawls/core_plan_wall_cutaway_round2.png');bpy.ops.render.render(write_still=True)
