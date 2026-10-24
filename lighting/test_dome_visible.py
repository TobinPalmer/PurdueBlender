import bpy,importlib.util
from pathlib import Path
p=Path(bpy.data.filepath).parent.parent/'lighting'/'sunset_cloud_world.py';spec=importlib.util.spec_from_file_location('sunset_cloud_world',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.build_sky_dome(bpy.context.scene)
s=bpy.context.scene;s.world.use_nodes=True;nt=s.world.node_tree;nt.nodes.clear();bg=nt.nodes.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(0,0,0,1);out=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(bg.outputs[0],out.inputs['Surface']);s.render.resolution_x=640;s.render.resolution_y=400;s.render.resolution_percentage=100;s.cycles.samples=2;s.render.filepath=str(p.parent/'renders'/'dome_isolation_test.png');bpy.ops.render.render(write_still=True)
