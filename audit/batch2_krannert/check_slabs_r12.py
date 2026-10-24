import bpy
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/krannert_building.blend';bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.objects:
 if o.name.startswith('KRAN_FloorSlab_'):
  z=sorted(set(round(float(v.co.z),4) for v in o.data.vertices));print(o.name,z[:3],z[-3:])
