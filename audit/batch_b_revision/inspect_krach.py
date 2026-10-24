import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\krach_leadership_center.blend')
a=bpy.data.collections['Asset_krach_leadership_center']
for o in a.all_objects:
 if o.type=='MESH' and any(x in o.name.lower() for x in ['window','glaz','facade','sash','curtain']):
  print(o.name, [m.name if m else None for m in o.data.materials], tuple(round(v,2) for v in o.location))
