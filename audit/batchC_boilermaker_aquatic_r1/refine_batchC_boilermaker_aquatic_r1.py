import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; rig=bpy.data.collections['Preview_Rig']
for o in asset.all_objects:
 if o and o.type=='MESH' and o.name.startswith('AQUA | schematic clear-span roof truss'):
  if o.data.users>1:o.data=o.data.copy()
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z>11.95: p.z=11.95; v.co=inv@p
# interior detail camera from west, toward the competition pool and dive tower
name='AQUA R1 | Interior Detail Camera'
old=bpy.data.objects.get(name)
if old:bpy.data.objects.remove(old,do_unlink=True)
data=bpy.data.cameras.new(name); data.lens=43
o=bpy.data.objects.new(name,data); rig.objects.link(o); o.location=(-54,43,21); o.rotation_euler=(Vector((-9,2,3))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET)); print('AQUA_R1_ROOF_CLEARANCE_AND_DETAIL_CAMERA')
