import bpy,math,json,shutil
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');shutil.copy2(P,D/'round4.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
centers=[(49.8,1.5),(49.9,53.4),(10.5,35.2)];levels=[(-4.064,.6096),(.6096,4.8768),(4.8768,9.144),(9.144,13.4112)]
# Widen the start landings and overlap their boxes with each lowest stair flight.
for i,(x,y) in enumerate(centers,1):
 o=c.objects[f'POTR_2016_StairCore{i}_Basement_Landing_Estimate'];o.location.x=x-1.55;o.dimensions=(1.5,2.1,.16);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.location.z=-4.064+.08;o['interface']='Expanded to overlap the lowest flight; its surrounding basement corridor/core registration remains unverified.'
# Upper landings bridge flight noses to the corresponding upper slab surface. Widen existing plates in place.
for i,(x,y) in enumerate(centers,1):
 for level,(z0,z1) in enumerate(levels):
  nm=f'POTR_2016_StairCore{i}_Level{level}_UpperLanding';o=bpy.data.objects.get(nm)
  if not o:continue
  o.dimensions=(1.5,2.1,.16);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.location.x=x-1.97;o.location.z=z1-.08+.15;o['interface']='Widened to overlap top flight tread and align landing top to estimated upper floor slab top.'
  # Last eight mesh vertices belong to the modeled mid-landing inside the paired-flight assembly.
  flight=c.objects[f'POTR_2016_StairCore{i}_Level{level}_Flight'];me=flight.data;mid=(z0+z1)/2
  vv=me.vertices[-8:];oldcenter=x+1.97;newcenter=x+1.35;oldhalf=.31;newhalf=.75
  for v in vv:
   rel=(v.co.x-oldcenter)/oldhalf;v.co.x=newcenter+rel*newhalf
  me.update();flight['mid_landing_interface']='Expanded in mesh to overlap both flight ends; dimensions remain estimated.'
# Rebuild the Room 401 penthouse as an open perimeter-wall shell instead of a solid block.
mass=c.objects['POTR_Historic2016_Room401_Penthouse_Massing'];me=mass.data
base=13.4112;top=15.5
bottom_face=next(p for p in me.polygons if all(abs(me.vertices[k].co.z-base)<1e-4 for k in p.vertices))
pts=[tuple(me.vertices[k].co[:2]) for k in bottom_face.vertices][::-1]
# Convert the 2016 Room401 outline to 0.2m perimeter walls; split the west wall for the estimated 4S04 entry.
verts=[];faces=[];wall_depth=.2;height=top-base

def add_wall(a,b,zlo,zhi,depth=.2):
 dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy)
 if L<.02 or zhi-zlo<.02:return
 nx,ny=-dy/L*depth/2,dx/L*depth/2;zmid=(zlo+zhi)/2;idx=len(verts)
 verts.extend([(a[0]+nx,a[1]+ny,zlo),(b[0]+nx,b[1]+ny,zlo),(b[0]-nx,b[1]-ny,zlo),(a[0]-nx,a[1]-ny,zlo),(a[0]+nx,a[1]+ny,zhi),(b[0]+nx,b[1]+ny,zhi),(b[0]-nx,b[1]-ny,zhi),(a[0]-nx,a[1]-ny,zhi)])
 faces.extend([tuple(idx+j for j in q) for q in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])

door_y=35.3;door_w=.9;door_top=15.4
for i,a in enumerate(pts):
 b=pts[(i+1)%len(pts)]
 # Current T outline's west wall along x≈15.2 adjoins the 4S04 stair enclosure.
 if abs(a[0]-15.2)<.15 and abs(b[0]-15.2)<.15 and min(a[1],b[1])<door_y<max(a[1],b[1]):
  ylo,yhi=sorted((a[1],b[1]));lo=door_y-door_w/2;hi=door_y+door_w/2
  add_wall((a[0],ylo),(a[0],lo),base,top,wall_depth);add_wall((a[0],hi),(a[0],yhi),base,top,wall_depth);add_wall((a[0],lo),(a[0],hi),door_top,top,wall_depth)
 else:add_wall(a,b,base,top,wall_depth)
newme=bpy.data.meshes.new('POTR_Room401_Perimeter_Walls_With_4S04_Access');newme.from_pydata(verts,[],faces);newme.update();precast=bpy.data.materials.get('POTR_Pale_Precast') or bpy.data.materials.get('POTR_Exterior_Precast')
if precast:newme.materials.append(precast)
old=mass.data;mass.data=newme;mass['description']='2016 Existing Penthouse Room401 perimeter walls at approximate plan registration; solid-block proxy replaced with hollow wall shell and one 0.9m estimated opening to 4S04.';mass['interior_connection']='4S04 west/east doorway alignments are approximate, door height 2.1m estimated.'
if old.users==0:bpy.data.meshes.remove(old)
# Save and reopen, then simple axis-aligned interface clearance report for the lowest flights.
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];interfaces=[]
def bounds(o):
 co=[o.matrix_world@v.co for v in o.data.vertices];return [min(v[j] for v in co) for j in range(3)],[max(v[j] for v in co) for j in range(3)]
for i in range(1,4):
 land=c.objects[f'POTR_2016_StairCore{i}_Basement_Landing_Estimate'];flight=c.objects[f'POTR_2016_StairCore{i}_Level0_Flight'];a0,a1=bounds(land);b0,b1=bounds(flight);gap=[max(0,b0[j]-a1[j],a0[j]-b1[j]) for j in range(3)];interfaces.append({'core':i,'landing_flight_aabb_gap_m':gap,'overlap_or_contact':max(gap)<1e-4})
print(json.dumps({'objects':len(c.all_objects),'root':list(c.objects['AssetRoot_potter_engineering'].location),'shell_xy':list(c.objects['POTR_Official_864_Structural_Envelope'].dimensions[:2]),'room401_vertices':len(c.objects['POTR_Historic2016_Room401_Penthouse_Massing'].data.vertices),'door_alignment':'4S04 opening on room401 perimeter at y=35.3, z=13.4112–15.4m (estimate)','basement_interfaces':interfaces},indent=2))
