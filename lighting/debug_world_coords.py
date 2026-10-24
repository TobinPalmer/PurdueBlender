import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent;s=bpy.context.scene
# Strip test geometry from the preview scene; this is only a coordinate diagnostic.
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
cd=bpy.data.cameras.new('DebugSkyCamera');cam=bpy.data.objects.new('DebugSkyCamera',cd);s.collection.objects.link(cam);cam.location=(0,0,0);cam.rotation_euler=(Vector((0,0,1))).to_track_quat('-Z','Y').to_euler();cd.lens=35;s.camera=cam
w=bpy.data.worlds.new('DebugCoordinateWorld');s.world=w;w.use_nodes=True
nt=w.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputWorld');bg=nt.nodes.new('ShaderNodeBackground');tc=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tc.outputs['Normal'],sep.inputs[0])
ramp=nt.nodes.new('ShaderNodeValToRGB');nt.links.new(sep.outputs['Z'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bg.inputs['Color']);nt.links.new(bg.outputs[0],out.inputs['Surface'])
s.render.engine='CYCLES';s.cycles.samples=1;s.render.resolution_x=600;s.render.resolution_y=400;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard'
for key in ('Generated','Normal','Reflection'):
 for l in list(nt.links):nt.links.remove(l)
 nt.links.new(tc.outputs[key],sep.inputs[0]);nt.links.new(sep.outputs['Z'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bg.inputs['Color']);nt.links.new(bg.outputs[0],out.inputs['Surface']);s.render.filepath=str(P/'lighting'/'renders'/f'coord_{key.lower()}.png');bpy.ops.render.render(write_still=True)
print('DONE',flush=True);bpy.ops.wm.quit_blender()
