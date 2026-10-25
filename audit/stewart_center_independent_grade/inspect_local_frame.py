import bpy
from mathutils import Vector
c=bpy.data.collections['Asset_stewart_center']
for n in ['STEW_Portico_Back_Wall','STEW_South_Entrance_Glazing','STEW_South_Door_Frame_84.0','STEW_North_Grand_Curtain_Glass','STEW_North_Door_Bronze_85.0','STEW_East_Portal_Glazing','STEW_FlyLoft_Body','STEW_Penthouse_East','HSSE_Interior_Wall_South','Loeb_Interior_Wall_North']:
 o=bpy.data.objects[n]; vs=[o.matrix_world@Vector(v) for v in o.bound_box]; print(n,[[round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)] for i in range(3)])
