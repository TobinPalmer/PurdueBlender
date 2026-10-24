import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
source=root/'modular/site/foliage_library/source/tree_small_02/tree_small_02.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=False) as (src,dst): dst.objects=['tree_small_02_LOD1']
obj=dst.objects[0]; bpy.context.scene.collection.objects.link(obj)
# Source tree already centers at its mesh origin; normalize its bottom to z=0.
coords=[obj.matrix_world@Vector(c) for c in obj.bound_box]; lo=min(v.z for v in coords); obj.location.z-=lo
bpy.context.view_layer.update()
for mat in obj.data.materials:
 print('MAT',mat.name,'surface',getattr(mat,'surface_render_method',None))
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE': print('IMAGE',n.image.name,n.image.size[:], 'packed',bool(n.image.packed_file))
  if n.type=='BSDF_PRINCIPLED': print('ALPHA_LINKS',[(l.from_node.name,l.from_socket.name,l.to_socket.name) for l in mat.node_tree.links if l.to_node==n and 'Alpha' in l.to_socket.name])
camd=bpy.data.cameras.new('cam'); cam=bpy.data.objects.new('cam',camd); bpy.context.scene.collection.objects.link(cam)
cam.location=(8,-13,5); tgt=Vector((0,0,2.2)); cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler(); camd.lens=50; bpy.context.scene.camera=cam
ld=bpy.data.lights.new('key','AREA'); lo=bpy.data.objects.new('key',ld); bpy.context.scene.collection.objects.link(lo); lo.location=(2,-6,10); ld.energy=1200; ld.shape='DISK'; ld.size=8
world=bpy.data.worlds.new('world'); world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.68,.7,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8; bpy.context.scene.world=world
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=8; sc.render.resolution_x=600; sc.render.resolution_y=600; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.render.filepath=str(root/'audit/engineering_precinct/tree_source_preview.png')
bpy.ops.render.render(write_still=True)
