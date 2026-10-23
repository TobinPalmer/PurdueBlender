import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');o=bpy.data.objects['RAWL_Masonry_Exterior_Walls']
for p in o.data.polygons:
 pts=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];cx=sum(v.x for v in pts)/len(pts);cy=sum(v.y for v in pts)/len(pts);cz=sum(v.z for v in pts)/len(pts)
 if abs(cy-20.7)<2:print('poly',p.index,'center',round(cx,3),round(cy,3),round(cz,3),'n',tuple(round(v,3) for v in p.normal),'verts',[tuple(round(q,2) for q in v) for v in pts])
