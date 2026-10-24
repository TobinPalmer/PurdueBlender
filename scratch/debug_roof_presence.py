import bpy,os
from mathutils import Vector
root=os.path.abspath('.')
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'modular/buildings/niswonger_aviation_tech.blend'))
o=bpy.data.objects['NISW_Flat_Roof_Membrane'];
for x in bpy.data.objects:x.hide_render=(x!=o)
o.hide_render=False
mat=bpy.data.materials.new('DEBUG red roof');mat.diffuse_color=(1,0,0,1);mat.use_nodes=True; mat.node_tree.nodes.clear(); out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial'); em=mat.node_tree.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(1,0,0,1);mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);o.data.materials.clear();o.data.materials.append(mat)
pts=[o.matrix_world@Vector(c) for c in o.bound_box];mn=Vector(tuple(min(p[i] for p in pts) for i in range(3)));mx=Vector(tuple(max(p[i] for p in pts) for i in range(3)));c=(mn+mx)*.5; print('BBOX',tuple(mn),tuple(mx),tuple(c))
scene=bpy.context.scene; cd=bpy.data.cameras.new('debug');cam=bpy.data.objects.new('debug',cd);scene.collection.objects.link(cam);cam.location=c+Vector((0,0,50));cam.rotation_euler=(Vector((0,0,-1))).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=24;scene.camera=cam; scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.filepath=os.path.join(root,'audit/texture_final_two/nisw_roof_debug.png');bpy.ops.render.render(write_still=True)
