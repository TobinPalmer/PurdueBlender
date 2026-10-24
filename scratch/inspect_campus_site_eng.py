import bpy
f=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend'
bpy.ops.wm.open_mainfile(filepath=f)
for ob in bpy.data.objects:
 if ob.type=='MESH' and any(k in ob.name.lower() for k in ('engineering','mall','fountain','lawn','campus_site')):
  print(ob.name,'loc',tuple(round(v,2) for v in ob.location),'dims',tuple(round(v,2) for v in ob.dimensions),'mat',[m.name for m in ob.data.materials if m])
