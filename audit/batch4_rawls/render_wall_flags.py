import bpy, math, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
s=bpy.context.scene
for o in bpy.data.objects:o.hide_render=True
fp=bpy.data.objects['RAWL_FloorSlab_L1_Ground'];fp.hide_render=False
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('RAWL_2026_Plan'):o.hide_render=False
# Flat, readable top-down diagnostic: assign clay materials to visible objects only.
def mat(name,color):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=1
 return m
floor=mat('RAWL_R2_DIAGNOSTIC_FLOOR',(0.65,0.67,0.69));walls=mat('RAWL_R2_DIAGNOSTIC_WALLS',(0.8,0.14,0.08))
fp.data.materials.clear();fp.data.materials.append(floor)
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('RAWL_2026_Plan'):
  o.data.materials.clear();o.data.materials.append(walls)
# area camera covers the entire plan
camd=bpy.data.cameras.new('R2_Wall_Flag_Camera');cam=bpy.data.objects.new('R2_Wall_Flag_Camera',camd);s.collection.objects.link(cam);s.camera=cam
cam.location=(10,0,150);cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=100
# Blender camera local -Z, +Y is image up. straight down
cam.rotation_euler=(0,0,0)
# top-down camera needs rotation 0 gives view down -Z, Y up
ld=bpy.data.lights.new('R2_Wall_Flag_Area','AREA');lo=bpy.data.objects.new('R2_Wall_Flag_Area',ld);s.collection.objects.link(lo);lo.location=(10,0,70);ld.energy=22000;ld.size=90;lo.rotation_euler=(0,0,0)
s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.abspath('audit/batch4_rawls/round2_wall_shell_top.png')
bpy.ops.render.render(write_still=True)
