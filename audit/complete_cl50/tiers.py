import bpy,math
from pathlib import Path
c=bpy.data.collections['Asset_class_of_1950'];m=bpy.data.materials['CL50_Pale_Terrazzo'];sx=(656-287)/732*43.3-30.3;sy=18.975-(154-60)/540*37.35
for row in range(20):
 y=sy-2.8-row*.8;z=.5+row*.16;half=8.5+min(row,10)*.30
 # segmented shallowcurved tier follows desks so allchairposts supported
 for j in range(24):
  x=sx-half+(j+.5)*half/12;yy=y+.007*(x-sx)**2;h=z-.42
  dx=half/12;dy=.84;vs=[(x+i*dx/2,yy+k*dy/2,.42+q*h) for i,k,q in [(-1,-1,0),(-1,-1,1),(-1,1,0),(-1,1,1),(1,-1,0),(1,-1,1),(1,1,0),(1,1,1)]];me=bpy.data.meshes.new('Tier');me.from_pydata(vs,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);me.materials.append(m);o=bpy.data.objects.new('CL50_New_SupportedTier_%s_%s'%(row,j),me);c.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);print(len(c.all_objects))
