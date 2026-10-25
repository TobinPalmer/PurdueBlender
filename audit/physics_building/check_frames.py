import bpy
from mathutils import Vector
p='modular/buildings/physics_building_phys_3bf42f3.blend'; bpy.ops.wm.open_mainfile(filepath=p)
w=bpy.data.objects['PHYS | recessed dark sash glazing']; fr=bpy.data.objects['PHYS R2 | tall divided sash frames']
print('frame',len(fr.data.vertices),fr.hide_render,fr.data.materials[:])
# show centers of first original facing windows and near frame blocks
for poly in w.data.polygons:
 c=sum((w.data.vertices[i].co for i in poly.vertices),Vector())/4
 radial=Vector((c.x,c.y,0));radial.normalize()
 if poly.normal.dot(radial)<-.72 and c.z>2 and c.z<3:
  print('window',tuple(round(x,3) for x in c), 'norm',tuple(round(x,3) for x in poly.normal))
  break
for start in range(0,min(len(fr.data.vertices),24),8):
 g=fr.data.vertices[start:start+8]; c=sum((v.co for v in g),Vector())/8; d=fr.dimensions
 print('frame block center',tuple(round(x,3) for x in c),'bounds',tuple(round(max(v.co[j] for v in g)-min(v.co[j] for v in g),3) for j in range(3)))
