import bpy
from mathutils import Vector
m=bpy.data.materials['HAAS_GooglePhotos_RedClayTiles_estimated'];nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
for l in list(nt.links):
 if l.to_node==bs and l.to_socket.name in {'Base Color','Emission Color'}:nt.links.remove(l)
bs.inputs['Base Color'].default_value=(0.001,0.0002,0.0001,1);bs.inputs['Emission Color'].default_value=(0.07,0.008,0.002,1);bs.inputs['Emission Strength'].default_value=2.0;bs.inputs['Roughness'].default_value=0.98
S=bpy.context.scene;S.render.resolution_x=1200;S.render.resolution_y=960;S.cycles.samples=8;S.view_settings.exposure=-3;S.render.filepath='C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_haas/roof_uniform_preview.png';bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
