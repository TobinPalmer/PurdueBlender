import bpy,math
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=R/'audit/batch4_potter';P=R/'modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
for o in list(bpy.data.objects):o.hide_render=False
# Evidence-only gray grade plane and broad, low camera to emphasize facade depth rather than roof area.
bpy.ops.mesh.primitive_plane_add(size=240,location=(29.6,25.7,-.1));plane=bpy.context.object;plane.name='POTR_R7_Temporary_Grade';m=bpy.data.materials.new('POTR_R7_Temporary_Grade_Material');m.use_nodes=True;next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.29,.31,.28,1);plane.data.materials.append(m)
world=s.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.37,.43,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.22
ld=bpy.data.lights.new('POTR_R7_Exterior_Sun','SUN');lo=bpy.data.objects.new('POTR_R7_Exterior_Sun',ld);s.collection.objects.link(lo);lo.rotation_euler=(math.radians(28),math.radians(-28),math.radians(-35));ld.energy=1.35
ld2=bpy.data.lights.new('POTR_R7_Exterior_Fill','AREA');lo2=bpy.data.objects.new('POTR_R7_Exterior_Fill',ld2);s.collection.objects.link(lo2);lo2.location=(15,-5,29);ld2.energy=1500;ld2.shape='DISK';ld2.size=32;lo2.rotation_euler=(Vector((29,25,6))-lo2.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('POTR_R7_Low_Exterior_Camera');cam=bpy.data.objects.new(camd.name,camd);s.collection.objects.link(cam);target=Vector((29.6,25.7,6.8));cam.location=target+Vector((118,-105,10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=94;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1500;s.render.resolution_y=1040;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.8;s.render.filepath=str(D/'exterior_facade_round7_low.png');bpy.ops.render.render(write_still=True)

