import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
o=bpy.data.objects['RAWL_FloorSlab_L1_Ground']
polypts=[(127,318),(120,295),(245,256),(301,437),(176,475),(131,333),(127,318)]
poly=[(399-.12*y-323.658,-384-.12*x+409.622) for x,y in polypts]
def ins(x,y):
 c=False;j=len(poly)-1
 for i in range(len(poly)):
  xi,yi=poly[i];xj,yj=poly[j]
  if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:c=not c
  j=i
 return c
for p in o.data.polygons:
 c=o.matrix_world@p.center
 if abs(c.z)<.02 and ins(c.x,c.y): print(round(c.x,2),round(c.y,2),p.area,p.normal[:],p.material_index)
