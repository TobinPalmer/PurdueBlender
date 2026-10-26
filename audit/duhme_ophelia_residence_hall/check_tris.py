import bpy,math
for name in ['DUHME_Continuous_GIS_Footprint_Foundation','DUHME_Interior_Floor_1','DUHME_Continuous_Slate_Roof_Underlay']:
 o=bpy.data.objects.get(name)
 area=0
 for p in o.data.polygons:
  if len(p.vertices)==3:
   a,b,c=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
   area+=abs((b.x-a.x)*(c.y-a.y)-(c.x-a.x)*(b.y-a.y))/2
 print(name,len(o.data.polygons),area)
