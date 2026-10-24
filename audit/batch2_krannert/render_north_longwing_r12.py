import bpy,os
from mathutils import Vector
ROOT=r'C:/Users/Tobin/Documents/Blender/PurdueMap'; ASSET=ROOT+'/modular/buildings/krannert_building.blend'; OUT=ROOT+'/audit/batch2_krannert'
bpy.ops.wm.open_mainfile(filepath=ASSET); scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.73,.82,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
mat=bpy.data.materials.new('R12_LongWing_RenderOnly_Ground');mat.diffuse_color=(.27,.29,.28,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.27,.29,.28,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.98
bpy.ops.mesh.primitive_plane_add(size=220,location=(0,0,-.03));bpy.context.object.name='R12_LONGWING_RENDER_ONLY_GROUND';bpy.context.object.data.materials.append(mat)
camdata=bpy.data.cameras.new('R12_LONGWING_CAMERA');camdata.lens=52;cam=bpy.data.objects.new('R12_LONGWING_CAMERA',camdata);scene.collection.objects.link(cam);cam.location=(19,62,20);target=Vector((19,18,16));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam;scene.render.filepath=OUT+'/krannert_north_long_wing_r12.png';bpy.ops.render.render(write_still=True)


