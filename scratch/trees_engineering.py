import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend'; bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.objects:
 if any(t in o.name.lower() for t in ['tree','oak','elm','gum','hawthorn','arborvitae']):
  x,y,z=o.location
  if -130<x<130 and 80<y<370: print(o.name,tuple(round(v,1) for v in o.location),o.type)
