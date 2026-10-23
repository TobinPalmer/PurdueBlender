import bpy
from mathutils import Vector
m=bpy.data.materials.new('R10_EmissionOnly_TEST');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(0.08,0.006,0.002,1);e.inputs['Strength'].default_value=1.0;o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs['Surface'])
for n in ['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 bpy.data.objects[n].data.materials.clear();bpy.data.objects[n].data.materials.append(m)
S=bpy.context.scene
for x in bpy.data.objects:x.hide_render=x.name not in {'HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof'}
for x in bpy.data.objects:
 if x.type=='LIGHT':x.hide_render=True
S.render.engine='CYCLES';S.cycles.samples=2;S.render.resolution_x=1000;S.render.resolution_y=800;S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/roof_emission_test.png';bpy.ops.render.render(write_still=True)
