import bpy, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
# Isolate the existing modeled core partition, jamb and header pieces; no new architectural layout is added.
for o in s.objects:o.hide_render=not any(k in o.name for k in ['PlanCore'])
wallmat=bpy.data.materials.new('R5_Core_Drawing_Ink');wallmat.diffuse_color=(.04,.08,.12,1);wallmat.use_nodes=True
bs=next(n for n in wallmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.035,.07,.10,1);bs.inputs['Roughness'].default_value=.9
for o in s.objects:
 if not o.hide_render and o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(wallmat)
# A temporary light drawing ground clarifies partition outlines while preserving exact wall/door extents.
fm=bpy.data.meshes.new('R5_Core_Plan_Ground_Mesh');fm.from_pydata([(-16,-23,.02),(1,-23,.02),(1,1,.02),(-16,1,.02)],[],[(0,1,2,3)]);fm.update()
floor=bpy.data.objects.new('R5_Core_Plan_Ground',fm);s.collection.objects.link(floor)
fmat=bpy.data.materials.new('R5_Core_Drawing_Paper');fmat.use_nodes=True;fmat.diffuse_color=(.86,.88,.87,1);next(n for n in fmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.86,.88,.87,1);fm.materials.append(fmat)
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
w=bpy.data.worlds.new('R5_Core_Plan_World');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.86,.88,.87,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;s.world=w
camd=bpy.data.cameras.new('R5_Core_Plan_Camera');cam=bpy.data.objects.new('R5_Core_Plan_Camera',camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(-7.5,-11,28);cam.rotation_euler=(Vector((-7.5,-11,1))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=19
ld=bpy.data.lights.new('R5_Core_Plan_Key','AREA');ld.energy=2200;ld.size=15;light=bpy.data.objects.new('R5_Core_Plan_Key',ld);s.collection.objects.link(light);light.location=(-7.5,-11,24);light.rotation_euler=(Vector((-7.5,-11,0))-light.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.abspath('audit/batch4_rawls/core_partitions_ink_plan_round5.png');bpy.ops.render.render(write_still=True)
