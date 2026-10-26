import bpy,json,math
from math import cos,radians
from mathutils import Vector
base=r'modular/buildings/massing_phi_delta_theta_258cddd.blend'; data=json.load(open(r'audit/massing_phi_delta_theta_258cddd/sources/purdue_gis_fid_796.json',encoding='utf-8-sig'))
bpy.ops.wm.open_mainfile(filepath=base)
o=bpy.data.objects['Phi Delta Theta']; vs=[o.matrix_world @ v.co for v in o.data.vertices]
ring=data['geometry']['rings'][0]
gis=[((lon+86.9137)*111412.84*cos(radians(40.4274)), (lat-40.4274)*111040) for lon,lat in ring]
print('GIS extent',[(min(p[i] for p in gis),max(p[i] for p in gis)) for i in (0,1)],'n',len(gis))
print('GIS centroid',sum(p[0] for p in gis[:-1])/(len(gis)-1),sum(p[1] for p in gis[:-1])/(len(gis)-1))
for i,p in enumerate(gis):
 d=min(math.hypot(v.x-p[0],v.y-p[1]) for v in vs if abs(v.z)<0.001)
 print(i,round(p[0],3),round(p[1],3),'nearest',round(d,4))
