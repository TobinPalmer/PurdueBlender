import bpy, math
from mathutils import Vector
from pathlib import Path
out=Path('audit/foliage_library_tree_close.png').resolve()
tree=bpy.data.collections.get('PH_Tree_Small_02_LOD2')
if not tree: raise RuntimeError('Tree collection not found')
keep=set(tree.all_objects)
for obj in list(bpy.context.scene.objects):
    if obj not in keep: bpy.data.objects.remove(obj, do_unlink=True)
if not bpy.context.scene.collection.children.get(tree.name): bpy.context.scene.collection.children.link(tree)
def simple_mat(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=.9
    return m
floor_mat=simple_mat('Preview neutral ground',(0.20,.25,.18))
back_mat=simple_mat('Preview sky backdrop',(.22,.43,.58))
bpy.ops.mesh.primitive_plane_add(size=80, location=(0,0,-.025)); bpy.context.object.name='Preview ground'; bpy.context.object.data.materials.append(floor_mat)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0,3.5,4)); back=bpy.context.object; back.name='Preview alpha backdrop'; back.rotation_euler[0]=math.radians(90); back.data.materials.append(back_mat)
bpy.ops.object.light_add(type='AREA', location=(-4,-5,8)); key=bpy.context.object; key.data.energy=1450; key.data.shape='DISK'; key.data.size=6
bpy.ops.object.light_add(type='AREA', location=(4,1,5)); fill=bpy.context.object; fill.data.energy=550; fill.data.size=5
bpy.ops.object.camera_add(location=(7,-11,4.3)); cam=bpy.context.object; target=Vector((0,.3,2.25)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=6.4; bpy.context.scene.camera=cam
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=96
scene.render.resolution_x=1400; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(out)
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds.new('Preview world'); world.use_nodes=True; bg=world.node_tree.nodes.get('Background'); bg.inputs[0].default_value=(.12,.2,.3,1); bg.inputs[1].default_value=.35; scene.world=world
bpy.ops.wm.save_as_mainfile(filepath=str(Path('audit/foliage_library_tree_close.blend').resolve()))
bpy.ops.render.render(write_still=True)
print('RENDER',out,'TREE_OBJECTS',len(keep))
