import bpy, os
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + '/modular/buildings/krannert_building.blend'
OUT = ROOT + '/audit/batch2_krannert'
bpy.ops.wm.open_mainfile(filepath=ASSET)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=20
scene.cycles.use_denoising=True
scene.render.resolution_x=1400
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.68,.73,.82,1)
bg.inputs['Strength'].default_value=.45

mat=bpy.data.materials.new('R9_RenderOnly_SouthView_Ground')
mat.diffuse_color=(.27,.29,.28,1)
mat.use_nodes=True
mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.27,.29,.28,1)
mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.98
bpy.ops.mesh.primitive_plane_add(size=220,location=(0,0,-.03))
bpy.context.object.name='R9_RENDER_ONLY_GROUND'
bpy.context.object.data.materials.append(mat)

target=Vector((0,0,16.0))
for name,loc in [
    ('south_front',(0,-94,20)),
    ('southeast_same_corner',(45,-82,20)),
    ('southwest_same_corner',(-45,-82,20)),
]:
    data=bpy.data.cameras.new('R9_TEMP_'+name)
    data.lens=42
    cam=bpy.data.objects.new('R9_TEMP_'+name,data)
    scene.collection.objects.link(cam)
    cam.location=loc
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.camera=cam
    scene.render.filepath=os.path.join(OUT,'krannert_'+name+'_r9.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True)
    bpy.data.cameras.remove(data)
print('Fresh unparented world-space camera renders; temporary camera and ground were not saved.')

