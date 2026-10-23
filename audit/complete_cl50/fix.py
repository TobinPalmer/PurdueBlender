import bpy,math,json
from pathlib import Path
from mathutils import Vector
c=bpy.data.collections['Asset_class_of_1950'];D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_cl50')
def cube(n,p,d,m,rot=0):
 vs=[(i*d[0]/2,j*d[1]/2,k*d[2]/2) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);me.update();o=bpy.data.objects.new(n,me);c.objects.link(o);o.location=p;o.rotation_euler.z=rot;me.materials.append(m);return o
for o in list(c.all_objects):
 if o and (o.name in ['CL50_New_Auditorium224_Partition1','CL50_New_Auditorium224_Partition9'] or ('Room' in o.name and '_North' in o.name)):
  dims=o.dimensions.copy();p=o.location.copy();rot=o.rotation_euler.z;ma=o.data.materials[0];length=dims.x;gap=1.5
  # split wall around real walkable opening, with lintel above2.3m
  for side in [-1,1]:
   le=(length-gap)/2;off=side*(gap/2+le/2);cube(o.name+'_DoorSide',p+Vector((math.cos(rot)*off,math.sin(rot)*off,0)),(le,dims.y,dims.z),ma,rot)
  bottom=p.z-dims.z/2;top=p.z+dims.z/2;cube(o.name+'_Lintel',(p.x,p.y,(bottom+2.3+top)/2),(gap,dims.y,top-bottom-2.3),ma,rot);bpy.data.objects.remove(o,do_unlink=True)
# classrooms seats at desk centers, dark seat and back
for o in list(c.all_objects):
 if o and 'CL50_New_Room' in o.name and '_Table' in o.name:
  p=o.location;ma=bpy.data.materials['CL50_Photographic_Dark_Seats'];cube(o.name+'_ChairSeat',(p.x,p.y-.4,.85),(.44,.4,.08),ma);cube(o.name+'_ChairBack',(p.x,p.y-.57,1.12),(.44,.07,.48),ma)
# make facade column brickmapping cylindricalvia object coords explicitUV
for o in c.all_objects:
 if o and 'RoundBrickColumn' in o.name:
  uv=o.data.uv_layers.new(name='Meters_Cylinder');
  for l in o.data.loops:
   v=o.data.vertices[l.vertex_index].co;uv.data[l.index].uv=(math.atan2(v.y,v.x)*.4,v.z)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('FIXED',len(c.all_objects))
