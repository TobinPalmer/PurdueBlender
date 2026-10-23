import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
# Move the sign clear of the cap, onto the front face of the flat lintel.
t=bpy.data.objects.get('SC_Portico_3D_Text')
if t:
 mw=t.matrix_world.copy();mw.translation+=Vector((0.35,0,-0.25));t.matrix_world=mw
# Ridge detailing should read as subdued metal/slate, not bright green.
m=bpy.data.materials.get('Aged_Copper_Trim')
if m:
 color=(0.24,0.22,0.19,1);m.diffuse_color=color
 if m.use_nodes:
  bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:bs.inputs['Base Color'].default_value=color;bs.inputs['Metallic'].default_value=0.35;bs.inputs['Roughness'].default_value=0.6
# Set the saved review camera to a top-down view of the schematic graduate hub.
cam=bpy.data.objects['Cam_SC_06_Interior_Schematic'];cam.location=(23.0,-7.0,13.0);cam.data.lens=45;cam.rotation_euler=(Vector((23.0,-7.0,2.1))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=p)
print('UPDATED SIGN',list(t.matrix_world.translation),'CAMERA',list(cam.location),list(cam.rotation_euler))
