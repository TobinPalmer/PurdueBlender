import bpy,math
from mathutils import Vector
c=bpy.data.collections['Asset_knoy_hall'];made=0
for o in list(c.all_objects):
 if not o.name.startswith('KNOY_Ground_TracePartition_'):continue
 idx=int(o.name.rsplit('_',1)[1]);L=o.dimensions.x
 if idx<8 or L<2.4:continue
 # Source doors cannot be individually read. Keep access openings explicit as provisional, not surveyed.
 angle=o.rotation_euler.z;d=Vector((math.cos(angle),math.sin(angle),0));center=o.location.copy();half=(L-1.05)/2
 o.dimensions.x=half;o.location=center-d*(L/4+.2625)
 q=o.copy();q.data=o.data.copy();c.objects.link(q);q.location=center+d*(L/4+.2625);q.name=o.name+'_AccessSide';q['access_opening_status']='Provisional1.05m central access gap; exact door location unverified';o['access_opening_status']=q['access_opening_status'];made+=1
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);print('access gaps',made)
