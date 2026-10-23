import bpy, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene
# Render-only crop of plan-derived first-floor core geometry over the exact 2024
# plan image. No plan/building geometry is changed or saved.
for o in s.objects:o.hide_render=True
core=[]
for o in bpy.data.objects:
 if not o.name.startswith('RAWL_2026_Plan') or o.type!='MESH':continue
 cs=[o.matrix_world@Vector(v) for v in o.bound_box]
 x0=min(v.x for v in cs);x1=max(v.x for v in cs);y0=min(v.y for v in cs);y1=max(v.y for v in cs)
 if x1>=-18 and x0<=4 and y1>=-24 and y0<=-3:
  o.hide_render=False;core.append(o)
ink=bpy.data.materials.new('R7_Core_Plan_Ink_RenderOnly');ink.diffuse_color=(.035,.065,.085,1);ink.use_nodes=True
bs=next(n for n in ink.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.035,.065,.085,1);bs.inputs['Roughness'].default_value=.9
for o in core:o.data.materials.clear();o.data.materials.append(ink)
img=bpy.data.images.load(os.path.abspath('audit/batch4_rawls/plan.png'),check_existing=True)
verts=[(75.342,25.622,-.06),(75.342,-32.938,-.06),(-47.538,-32.938,-.06),(-47.538,25.622,-.06)]
mesh=bpy.data.meshes.new('R7_Core_Plan_Image_Mesh');mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
for loop,coord in zip(mesh.polygons[0].loop_indices,[(0,1),(1,1),(1,0),(0,0)]):uv.data[loop].uv=coord
plane=bpy.data.objects.new('R7_Core_Plan_Image_Overlay_RenderOnly',mesh);s.collection.objects.link(plane)
pm=bpy.data.materials.new('R7_Core_Plan_Image_Material_RenderOnly');pm.use_nodes=True;pm.node_tree.nodes.clear();out=pm.node_tree.nodes.new('ShaderNodeOutputMaterial');em=pm.node_tree.nodes.new('ShaderNodeEmission');tex=pm.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;pm.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);pm.node_tree.links.new(em.outputs['Emission'],out.inputs['Surface']);mesh.materials.append(pm)
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.new('R7_Core_Plan_World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.82,.84,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8;s.world=world
camd=bpy.data.cameras.new('R7_Core_Plan_Camera');cam=bpy.data.objects.new(camd.name,camd);s.collection.objects.link(cam);s.camera=cam;cam.location=(-7,-13,65);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=30
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1400;s.render.resolution_y=1200;s.eevee.taa_render_samples=64;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.abspath('audit/batch4_rawls/core_plan_detail_round7.png')
bpy.ops.render.render(write_still=True);print('Rendered core plan detail with',len(core),'plan-derived mesh components; render-only changes unsaved.')
