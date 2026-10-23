exec(open('audit/batch4_rawls/round4_rebuild_wall_diag.py').read().split("# set pane to diagnostic emission")[0])
# isolate diagnostic wall, show the generated cutout pattern as emission
for ob in s.objects:ob.hide_render=ob not in {dup,cam if 'cam' in locals() else None}
# camera setup explicitly
from mathutils import Vector
cd=bpy.data.cameras.new('R4_WallOnlyCam');cam=bpy.data.objects.new('R4_WallOnlyCam',cd);s.collection.objects.link(cam);cam.location=(25,62,10);cam.rotation_euler=(Vector((25,20,10))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=30;s.camera=cam
m=bpy.data.materials.new('R4_WALL_EMIT');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.1,1,.1,1);e.inputs['Strength'].default_value=1;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface']);dup.data.materials.clear();dup.data.materials.append(m)
s.render.engine='CYCLES';s.cycles.samples=4;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.filepath=os.path.abspath('audit/batch4_rawls/northwall_grid_isolated_round4.png');bpy.ops.render.render(write_still=True)
