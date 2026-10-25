import bpy,json,os
from mathutils import Vector
ASSET=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
bpy.ops.wm.open_mainfile(filepath=ASSET)
# Undo the tiny 2-D rescale introduced by the corrected plan registration for the documented display.
SX=.092105;SY=(40.611-(-42.493))/(986-86);OLD=.0944;X0=-13.209-SX*323;Y0=40.611+SY*86
ax=SX/OLD; ay=SY/OLD
bx=X0+SX*(327+15.55/OLD); by=Y0-SY*(88+42.27/OLD)
def inverse(x,y):return((x-bx)/ax,(y-by)/ay)
updated=[]
for o in bpy.data.collections['Asset_lawson_hall'].objects:
 if o.type!='MESH' or not (o.name=='LWSN_1130_Harris_Video_Wall' or o.name.startswith('LWSN_R5_VideoWall_')):continue
 if o.data.users>1:o.data=o.data.copy()
 mw=o.matrix_world.copy(); inv=mw.inverted(); old=[]
 for v in o.data.vertices:
  p=mw@v.co;old.append((v,inverse(p.x,p.y),p))
 cx=sum(x[2].x for x in old)/len(old);cy=sum(x[2].y for x in old)/len(old)
 ox=sum(x[1][0] for x in old)/len(old);oy=sum(x[1][1] for x in old)/len(old)
 for v,(px,py),p in old:
  nw=Vector((cx+(px-ox),cy+(py-oy),p.z));v.co=inv@nw
 o.data.update();updated.append(o.name)
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(json.dumps({'restored_documented_wall_components':len(updated),'names':updated,'source':bpy.data.filepath},indent=2))
