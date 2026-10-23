import bpy
from pathlib import Path
from mathutils import Vector
D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_potter');bpy.ops.wm.open_mainfile(filepath=str(D.parents[1]/'modular/buildings/potter_engineering.blend'));c=bpy.data.collections['Asset_potter_engineering'];roof=next(o for o in c.objects if 'Roof' in o.name);center=sum((roof.matrix_world@Vector(v) for v in roof.bound_box),Vector())/8
s=bpy.context.scene;camd=bpy.data.cameras.new('Evidence');cam=bpy.data.objects.new('Evidence',camd);s.collection.objects.link(cam);cam.location=center+Vector((90,-110,80));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=105;s.camera=cam;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.35,.35,.35,1);s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.3;s.view_settings.exposure=-1;ld=bpy.data.lights.new('Daylight','SUN');lo=bpy.data.objects.new('Daylight',ld);s.collection.objects.link(lo);lo.rotation_euler=(.4,-.5,-.3);ld.energy=3;bpy.ops.mesh.primitive_plane_add(size=300,location=(center.x,center.y,-.02));ground=bpy.context.object;ground.name='Temporary_Evidence_Grade';s.render.filepath=str(D/'materials_after.png');bpy.ops.render.render(write_still=True)
ground.hide_render=True
for o in c.objects:o.hide_render=not ('Historic2016_Plan53_' in o.name or 'Interior_Slab_Level_1_' in o.name)
cam.location=center+Vector((30,-35,90));center.z=1;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.render.filepath=str(D/'interior_historic2016.png');bpy.ops.render.render(write_still=True)

