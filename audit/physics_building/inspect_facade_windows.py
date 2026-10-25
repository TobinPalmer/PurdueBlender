import bpy
obj=bpy.data.objects['PHYS | recessed dark sash glazing']; m=obj.data
for p in m.polygons[:18]:
 vs=[m.vertices[i].co for i in p.vertices]
 cen=sum(vs,__import__('mathutils').Vector())/len(vs)
 print(p.index,len(p.vertices),'c',tuple(round(x,2) for x in cen),'normal',tuple(round(x,2) for x in p.normal),'dim',tuple(round(max(v[j] for v in vs)-min(v[j] for v in vs),2) for j in range(3)))
