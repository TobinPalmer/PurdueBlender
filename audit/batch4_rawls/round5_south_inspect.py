import bpy, json, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'))
wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls']
for p in wall.data.polygons:
 pts=[wall.matrix_world@wall.data.vertices[i].co for i in p.vertices]
 cx=sum(v.x for v in pts)/len(pts); cy=sum(v.y for v in pts)/len(pts); cz=sum(v.z for v in pts)/len(pts)
 if cy < -23 and -13 < cx < -3 and cz < 20:
  print('WALL',p.index,'center',tuple(round(v,3) for v in (cx,cy,cz)),'normal',tuple(round(v,2) for v in p.normal),'bounds',[(round(min(v[i] for v in pts),3),round(max(v[i] for v in pts),3)) for i in range(3)],'verts',[tuple(round(v,3) for v in q) for q in pts])
for nm in ['RAWL_South_Windows_South_Glass','RAWL_South_Windows_East_Glass']:
 o=bpy.data.objects[nm]
 print('GLASS',nm)
 for p in o.data.polygons:
  pts=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
  print(p.index,'center',tuple(round(sum(v[i] for v in pts)/len(pts),3) for i in range(3)),'bounds',[(round(min(v[i] for v in pts),3),round(max(v[i] for v in pts),3)) for i in range(3)],'normal',tuple(round(v,2) for v in (o.matrix_world.to_3x3()@p.normal)))
for nm in ['RAWL_South_Windows_South_BronzeMullions','RAWL_South_Windows_East_BronzeMullions']:
 o=bpy.data.objects[nm]
 print('FRAME',nm,'faces',len(o.data.polygons),'verts',len(o.data.vertices))
 for v in o.data.vertices[:20]:print(tuple(round(q,3) for q in (o.matrix_world@v.co)))
