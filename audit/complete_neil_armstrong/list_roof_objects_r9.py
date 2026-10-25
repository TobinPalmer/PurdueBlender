import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
for o in bpy.data.collections['Asset_neil_armstrong_hall'].objects:
 if 'roof' in o.name.lower() or 'lidar' in o.name.lower() or 'canopy' in o.name.lower() or 'truss' in o.name.lower():
  print(o.name,o.type, list(o.dimensions), [m.name if m else None for m in o.data.materials] if o.type=='MESH' else '')
