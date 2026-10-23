import bpy,math,shutil,json
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');BASE=D/'round2.blend'
shutil.copy2(P,D/'round6_before_penthouse_layout.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
# Map the page-45 room outline with the neighboring registered existing floor plan transform.
a=[0,-.19747141023745407,-.1681596489618544,0,124.03748691766648,77.05195814831893]
def cv(x,y):return (a[0]*x+a[1]*y+a[4],a[2]*x+a[3]*y+a[5])
plan_px=[(212,445),(392,445),(392,505),(272,505),(272,552),(232,552),(232,505),(212,505)]
raw=[cv(x,y) for x,y in plan_px]
def area(poly):return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)
raw_area=area(raw);scale=math.sqrt(329.6/raw_area);cx=sum(x for x,y in raw)/len(raw);cy=sum(y for x,y in raw)/len(raw)
# True polygon centroid for uniform rescaling, from shoelace.
cross=[raw[i][0]*raw[(i+1)%len(raw)][1]-raw[(i+1)%len(raw)][0]*raw[i][1] for i in range(len(raw))];sa=sum(cross);pcx=sum((raw[i][0]+raw[(i+1)%len(raw)][0])*cross[i] for i in range(len(raw)))/(3*sa);pcy=sum((raw[i][1]+raw[(i+1)%len(raw)][1])*cross[i] for i in range(len(raw)))/(3*sa)
poly=[(pcx+(x-pcx)*scale,pcy+(y-pcy)*scale) for x,y in raw]
# Small planar utility: each wall is a closed 0.2m-thick solid, with explicit door gaps.
verts=[];faces=[]
def add_wall(a0,b0,z0,z1,depth=.20):
 dx,dy=b0[0]-a0[0],b0[1]-a0[1];L=math.hypot(dx,dy)
 if L<.02 or z1-z0<.02:return
 nx,ny=-dy/L*depth/2,dx/L*depth/2;i=len(verts)
 verts.extend([(a0[0]+nx,a0[1]+ny,z0),(b0[0]+nx,b0[1]+ny,z0),(b0[0]-nx,b0[1]-ny,z0),(a0[0]-nx,a0[1]-ny,z0),(a0[0]+nx,a0[1]+ny,z1),(b0[0]+nx,b0[1]+ny,z1),(b0[0]-nx,b0[1]-ny,z1),(a0[0]-nx,a0[1]-ny,z1)])
 faces.extend([tuple(i+j for j in q) for q in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0))])
def mesh_from_parts(name,material,props):
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update();me.materials.append(material);ob=bpy.data.objects.new(name,me);c.objects.link(ob)
 for k,v in props.items():ob[k]=v
 return ob
basez=13.4112;topz=15.50;door_top=15.35;wall_d=.20
precast=bpy.data.materials.get('POTR_Pale_Precast') or bpy.data.materials.get('POTR_Exterior_Precast') or bpy.data.materials.new('POTR_Pale_Precast')
# Rebuild the Room 401 hollow wall shell in the plan's registered orientation; the 2016 label area is 3,547 sf.
verts=[];faces=[];west=min(x for x,y in poly);door_y=35.2;door_w=.9
for i,p0 in enumerate(poly):
 p1=poly[(i+1)%len(poly)]
 if abs(p0[0]-west)<.03 and abs(p1[0]-west)<.03 and min(p0[1],p1[1])<door_y<max(p0[1],p1[1]):
  lo,hi=sorted((p0[1],p1[1]));a1=door_y-door_w/2;b1=door_y+door_w/2
  add_wall(p0,(west,a1),basez,topz,wall_d);add_wall((west,b1),p1,basez,topz,wall_d);add_wall((west,a1),(west,b1),door_top,topz,wall_d)
 else:add_wall(p0,p1,basez,topz,wall_d)
mass=c.objects['POTR_Historic2016_Room401_Penthouse_Massing'];old=mass.data;me=bpy.data.meshes.new('POTR_Room401_2016_Registered_T_Walls');me.from_pydata(verts,[],faces);me.update();me.materials.append(precast);mass.data=me
mass['plan_orientation']='Reoriented from printed p.45 page coordinates using the neighboring registered p.44 affine; approximately registered, not surveyed.';mass['room_area_sf']=3547;mass['plan_to_gis_scale']=scale;mass['door_alignment']='West stem doorway centered y=35.2m, approximate 0.9m clear width into the labeled 401A room.'
if old.users==0:bpy.data.meshes.remove(old)
# Rebuild the T-shaped Room 401 roof plate with the same traced outline.
plate=c.objects['POTR_Historic2016_Room401_Penthouse_Roof'];old=plate.data
pv=[(x,y,z) for z in (15.35,15.50) for x,y in poly];n=len(poly);pf=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
for i in range(n):j=(i+1)%n;pf.append((i,j,j+n,i+n))
pm=bpy.data.meshes.new('POTR_Room401_2016_Registered_T_Roof');pm.from_pydata(pv,[],pf);pm.update()
if old.materials:pm.materials.append(old.materials[0])
plate.data=pm;plate['source']='Approximate printed p.45 Room401 T outline in neighboring p.44 registered frame, scaled to labeled 3,547 sf.';plate['top_z_m']=15.50
if old.users==0:bpy.data.meshes.remove(old)
# Replace the prior oversized enclosure; the plan labels 401A at 100 sf and 4S04 at 183 sf.
for o in list(c.objects):
 if o.name.startswith('POTR_4S04_') or o.name.startswith('POTR_2016_Room401A_') or o.name.startswith('POTR_2016_4S04_UpperLanding'):bpy.data.objects.remove(o,do_unlink=True)
col4=bpy.data.collections.get('POTR_Historic2016_4S04_Enclosure_Estimate')
if not col4:col4=bpy.data.collections.new('POTR_Historic2016_4S04_Enclosure_Estimate');c.children.link(col4)
for o in list(col4.objects):
 if o.name.startswith('POTR_4S04_'):bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.collections.get('POTR_Historic2016_Room401A_Estimate').objects) if bpy.data.collections.get('POTR_Historic2016_Room401A_Estimate') else []:bpy.data.objects.remove(o,do_unlink=True)
colA=bpy.data.collections.get('POTR_Historic2016_Room401A_Estimate')
if not colA:colA=bpy.data.collections.new('POTR_Historic2016_Room401A_Estimate');c.children.link(colA)
roommat=bpy.data.materials.get('POTR_Interior_Warm_OffWhite') or bpy.data.materials.get('POTR_2016_Lab205_Enamel') or precast
x4w,x4e=9.3,13.0;y4s,y4n=32.9,37.5;doorw4=1.2
# 4S04 north/south boundaries and west stair-entry doorway; the east wall door opens to 401A.
verts=[];faces=[]
for y in (y4s,y4n):add_wall((x4w,y),(x4e,y),basez,topz,wall_d)
lo,hi=door_y-doorw4/2,door_y+doorw4/2
add_wall((x4w,y4s),(x4w,lo),basez,topz,wall_d);add_wall((x4w,hi),(x4w,y4n),basez,topz,wall_d);add_wall((x4w,lo),(x4w,hi),door_top,topz,wall_d)
lo,hi=door_y-.45,door_y+.45
add_wall((x4e,y4s),(x4e,lo),basez,topz,wall_d);add_wall((x4e,hi),(x4e,y4n),basez,topz,wall_d);add_wall((x4e,lo),(x4e,hi),door_top,topz,wall_d)
wall4=mesh_from_parts('POTR_4S04_Enclosure_Walls_183sf_Estimate',roommat,{'source':'Printed p.45 identifies 4S04 at 183 sf; rectangular extent and openings estimated from the adjacent registered floorplan affine.','area_sf':183,'door_west':'Estimated 1.2m opening to S03 stair landing.','door_east':'Estimated 0.9m opening toward Room401A.'})
# Room 401A, 100 sf, sits between Room401 and 4S04 per the plan. Side walls remain open at the two doorway interfaces.
xA_w,xA_e=x4e,west;areaA=100*0.09290304;yAwidth=(areaA/(xA_e-xA_w));yA_s,yA_n=door_y-yAwidth/2,door_y+yAwidth/2
verts=[];faces=[];add_wall((xA_w,yA_s),(xA_e,yA_s),basez,topz,wall_d);add_wall((xA_e,yA_n),(xA_w,yA_n),basez,topz,wall_d)
roomA=mesh_from_parts('POTR_2016_Room401A_100sf_Intervening_Room_Estimate',roommat,{'source':'Printed p.45 identifies Room401A at 100 sf between Room401 and 4S04.','area_sf':100,'connection':'Open ends align with estimated 0.9m doors in Room401 west-stem wall and 4S04 east wall.'})
# Roof cut only at S03/4S04; the smaller opening leaves usable landing and floor area within the 183sf enclosure.
with bpy.data.libraries.load(str(BASE),link=False) as (src,dst):dst.meshes=['POTR_Official_864_Roof']
full=dst.meshes[0];roof=c.objects['POTR_Official_864_Roof'];oldroof=roof.data;roof.data=full
if oldroof.users==0:bpy.data.meshes.remove(oldroof)
bpy.ops.mesh.primitive_cube_add(size=1,location=(10.5,35.2,14));cut=bpy.context.object;cut.name='POTR_R6_TEMP_RoofOpening';cut.dimensions=(3.2,2.7,5);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=roof.modifiers.new('Estimated S03 4S04 roof opening 3.2x2.7m','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=roof;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
roof['stair_openings']='First/second/third-floor slabs retain 4.6x3.6m estimate; roof retains only the S03/4S04 opening, reduced to 3.2x2.7m to preserve the plan-labeled 183sf enclosure landing/walk strip.'
# The last stair run meets an estimated 1.6x2.1m landing at the penthouse floor; it bridges into the 4S04 west opening.
landmat=bpy.data.materials.get('POTR_Interior_Concrete_Stairs');bpy.ops.mesh.primitive_cube_add(size=1,location=(9.6,35.2,13.3312));land=bpy.context.object;land.name='POTR_2016_StairCore3_Penthouse_Landing_4S04_Estimate';land.dimensions=(1.6,2.1,.16);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for cc in list(land.users_collection):cc.objects.unlink(land)
col4.objects.link(land);land.data.materials.append(landmat);land['source']='Estimated landing at the 2016 4S04 stair core; ties the upper S03 flight into the 4S04 enclosure. Dimensions approximate.'
# Save/reopen and write geometric/area proof for reviewer.
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];mass=c.objects['POTR_Historic2016_Room401_Penthouse_Massing']
pts=[tuple(v.co[:2]) for v in mass.data.vertices];xs=[p[0] for p in pts];ys=[p[1] for p in pts]
result={'reopened':True,'root':list(c.objects['AssetRoot_potter_engineering'].location),'shell_xy':[round(v,4) for v in c.objects['POTR_Official_864_Structural_Envelope'].dimensions[:2]],'approx_plan_transform':a,'plan_uniform_scale_to_room401_area':scale,'room401_target_and_estimated_area_m2':329.6,'room401_shell_xy_bounds':[min(xs),min(ys),max(xs),max(ys)],'room401_door_x':west,'room401a_area_target_m2':areaA,'room401a_bounds_xy':[xA_w,yA_s,xA_e,yA_n],'4s04_area_target_m2':183*.09290304,'4s04_bounds_xy':[x4w,y4s,x4e,y4n],'4s04_west_entry_opening_width_m':doorw4,'4s04_east_opening_width_m':.9,'roof_opening_dimensions_m':[3.2,2.7],'4s04_landing_bounds_xy':[8.8,34.15,10.4,36.25],'evidence':'Printed p.45 room labels 401 / 401A / 4S04 and areas; location maps by adjacent-floor p.44 affine and is explicitly approximate.'}
(D/'round6_penthouse_layout_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
