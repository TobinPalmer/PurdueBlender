import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');BASE=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter/round4.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
# Read the final-area Room401 polygon from the solid round-4 backup, then rebuild its hollow walls with the door exactly at its actual west edge.
with bpy.data.libraries.load(str(BASE),link=False) as (src,dst): dst.objects=['POTR_Historic2016_Room401_Penthouse_Massing']
oldobj=dst.objects[0];oldme=oldobj.data;base=13.4112;top=15.5
bottom=next(p for p in oldme.polygons if all(abs(oldme.vertices[k].co.z-base)<1e-4 for k in p.vertices));pts=[tuple(oldme.vertices[k].co[:2]) for k in bottom.vertices][::-1]
minx=min(x for x,y in pts);door_y=35.3;door_w=.9;door_top=15.4;wall_d=.20;verts=[];faces=[]
def wall(a,b,z0,z1):
 dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
 if L<.02 or z1-z0<.02:return
 nx,ny=-dy/L*wall_d/2,dx/L*wall_d/2;i=len(verts);verts.extend([(a[0]+nx,a[1]+ny,z0),(b[0]+nx,b[1]+ny,z0),(b[0]-nx,b[1]-ny,z0),(a[0]-nx,a[1]-ny,z0),(a[0]+nx,a[1]+ny,z1),(b[0]+nx,b[1]+ny,z1),(b[0]-nx,b[1]-ny,z1),(a[0]-nx,a[1]-ny,z1)]);faces.extend([tuple(i+j for j in q) for q in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])
for i,a in enumerate(pts):
 b=pts[(i+1)%len(pts)]
 if abs(a[0]-minx)<.03 and abs(b[0]-minx)<.03 and min(a[1],b[1])<door_y<max(a[1],b[1]):
  lo,hi=sorted((a[1],b[1]));dl,dh=door_y-door_w/2,door_y+door_w/2;wall((minx,lo),(minx,dl),base,top);wall((minx,dh),(minx,hi),base,top);wall((minx,dl),(minx,dh),door_top,top)
 else:wall(a,b,base,top)
me=bpy.data.meshes.new('POTR_Room401_Perimeter_With_4S04_Door');me.from_pydata(verts,[],faces);me.update();mat=bpy.data.materials.get('POTR_Pale_Precast') or bpy.data.materials.get('POTR_Exterior_Precast');
if mat:me.materials.append(mat)
obj=c.objects['POTR_Historic2016_Room401_Penthouse_Massing'];prev=obj.data;obj.data=me;obj['door_alignment']='0.9m estimated doorway centered y=35.3, cut into actual west perimeter x=%.3f from traced/scaled 2016 plan.'%minx
if prev.users==0:bpy.data.meshes.remove(prev)
# Move the estimated 4S04 enclosure so its doorway plane meets the west face of Room401.
shift=minx-15.2
for o in c.objects:
 if o.name.startswith('POTR_4S04_'):o.location.x+=shift
# Ensure only test new actual wall surfaces are hit beside the door, not at its opening.
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];obj=c.objects['POTR_Historic2016_Room401_Penthouse_Massing'];en=c.objects['POTR_4S04_EastWall_North'];door=[]
for y in (35.3,34.7,35.9):
 h1=obj.ray_cast(Vector((minx-1,y,14.4)),Vector((1,0,0)),distance=3)[0];h2=en.ray_cast(Vector((minx-1,y,14.4)),Vector((1,0,0)),distance=3)[0];door.append({'y':y,'room401_blocks':h1,'enclosure_north_block':h2})
print(json.dumps({'west_wall_x':minx,'enclosure_shift':shift,'door_rays':door,'objects':len(c.all_objects),'root':list(c.objects['AssetRoot_potter_engineering'].location)},indent=2))
