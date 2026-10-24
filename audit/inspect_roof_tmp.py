import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/burton_morgan_center.blend')
for ob in bpy.data.objects:
 if 'structural flat roof' in ob.name or 'structural shell' in ob.name:
  ups=sum(1 for poly in ob.data.polygons if poly.normal.z>.9); downs=sum(1 for poly in ob.data.polygons if poly.normal.z<-.9); print(ob.name,len(ob.data.polygons),'up',ups,'down',downs, 'mat',[m.name for m in ob.data.materials])
