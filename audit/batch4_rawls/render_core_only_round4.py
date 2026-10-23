import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
# Core-only diagnostic: retain plan-derived core partitions and a neutral backing plane.
for o in bpy.data.objects:o.hide_render=True
for o in bpy.data.objects:
 if o.name.startswith('RAWL_2026_PlanCore'):o.hide_render=False
# Build a neutral, explicitly non-survey backing surface so wall gaps read cleanly.
bpy.ops.mesh.primitive_plane_add(size=1,location=(-8,-11,-.32));pl=bpy.context.object;pl.name='R4_Core_Diagnostic_Backdrop';pl.dimensions=(13,22,0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mat=bpy.data.materials.new('R4_Core_Backdrop_Material');mat.diffuse_color=(.88,.89,.87,1);mat.use_nodes=True;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.88,.89,.87,1);bs.inputs['Roughness'].default_value=.9;pl.data.materials.append(mat)
wall=bpy.data.materials.new('R4_Core_Wall_Material');wall.diffuse_color=(.08,.11,.14,1);wall.use_nodes=True;bs=next(n for n in wall.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.08,.11,.14,1);bs.inputs['Roughness'].default_value=.8
for o in bpy.data.objects:
 if o.name.startswith('RAWL_2026_PlanCore') and o.type=='MESH':o.data.materials.clear();o.data.materials.append(wall)
s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('R4_Core_World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.9,.91,.92,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
ld=bpy.data.lights.new('R4_Core_Light','AREA');ld.energy=1200;ld.size=12;l=bpy.data.objects.new('R4_Core_Light',ld);s.collection.objects.link(l);l.location=(-8,-11,24);ld.shape='DISK'
camd=bpy.data.cameras.new('R4_Core_Camera');cam=bpy.data.objects.new('R4_Core_Camera',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(-8,-11,28);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=23
s.render.filepath=os.path.abspath('audit/batch4_rawls/core_plan_detail_round4.png');bpy.ops.render.render(write_still=True)
