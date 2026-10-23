import bpy,json,math
from pathlib import Path
from collections import deque
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');bpy.ops.wm.open_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];dg=bpy.context.evaluated_depsgraph_get()
def ray_obj(o,pt,direction,maxdist):
 inv=o.matrix_world.inverted();org=inv@Vector(pt);dire=(inv.to_3x3()@Vector(direction)).normalized();h,loc,n,idx=o.ray_cast(org,dire,distance=maxdist);return bool(h),loc,idx
# Person-clear tests: a nominal 0.8m-wide envelope on each 1.05m flight/landing and 2.0m vertical head envelope at every tread center.
clearance=[];slab_names=['POTR_Interior_Slab_Level_1_EstimatedElevation','POTR_Interior_Slab_Level_2_EstimatedElevation','POTR_Interior_Slab_Level_3_EstimatedElevation','POTR_Official_864_Roof'];
for core in range(1,4):
 for level in range(4 if core==3 else 3):
  nm=f'POTR_2016_StairCore{core}_Level{level}_Flight'; stair=bpy.data.objects.get(nm)
  if not stair:continue
  slab=bpy.data.objects[slab_names[level]];vals=[]
  for f in stair.data.polygons:
   if f.normal.z>.99 and f.area>.08:
    vs=[stair.data.vertices[i].co for i in f.vertices];cx=sum(v.x for v in vs)/len(vs);cy=sum(v.y for v in vs)/len(vs);z=sum(v.z for v in vs)/len(vs)
    hit,loc,idx=ray_obj(slab,(cx,cy,z+.001),(0,0,1),2.0)
    vals.append({'xy':[round(cx,3),round(cy,3)],'tread_z':round(z,4),'head_column_hit_within_2m':hit,'clearance_to_slab_m':round(loc.z-(z+.001),4) if hit else None})
  clearance.append({'core':core,'level':level,'nominal_clear_width_m':1.05-2*.018,'person_width_m':.8,'width_margin_total_m':1.05-2*.018-.8,'headroom_samples':len(vals),'headroom_pass':all(not q['head_column_hit_within_2m'] for q in vals),'headroom_sample_hits':[q for q in vals if q['head_column_hit_within_2m']],'slab':slab.name})
# 0.8m square-footprint BFS across the 4S04 floor around the cut roof aperture. The landing reaches both aperture side edges.
def inter_area(a,b):
 dx=max(0,min(a[2],b[2])-max(a[0],b[0]));dy=max(0,min(a[3],b[3])-max(a[1],b[1]));return dx*dy
hole=(8.9,33.85,12.1,36.55);landing=(8.8,33.85,10.4,36.55);room=(9.4,33.0,12.9,37.4);person=.8;step=.05
xs=[round(9.8+i*step,4) for i in range(55)];ys=[round(33.4+j*step,4) for j in range(73)];start=(0,36);goal=(54,36)
def valid(i,j):
 x,y=xs[i],ys[j];fp=(x-person/2,y-person/2,x+person/2,y+person/2)
 if fp[0]<room[0]-1e-6 or fp[1]<room[1]-1e-6 or fp[2]>room[2]+1e-6 or fp[3]>room[3]+1e-6:return False
 return inter_area(fp,hole)-inter_area(fp,landing)<1e-6
q=deque([start]);prev={start:None}
while q:
 cur=q.popleft()
 if cur==goal:break
 for nxt in [(cur[0]+1,cur[1]),(cur[0]-1,cur[1]),(cur[0],cur[1]+1),(cur[0],cur[1]-1)]:
  if 0<=nxt[0]<len(xs) and 0<=nxt[1]<len(ys) and nxt not in prev and valid(*nxt):prev[nxt]=cur;q.append(nxt)
path=[]
if goal in prev:
 cur=goal
 while cur is not None:path.append([xs[cur[0]],ys[cur[1]]]);cur=prev[cur]
 path.reverse()
# Wall openings and side controls.
checks=[]
for label,name,x0,x1,w in [('401-401A','POTR_Historic2016_Room401_Penthouse_Massing',16.3,16.9,.9),('S03-4S04','POTR_4S04_Enclosure_Walls_183sf_Estimate',9.0,9.6,1.2),('4S04-401A','POTR_4S04_Enclosure_Walls_183sf_Estimate',12.7,13.3,.9)]:
 ob=bpy.data.objects[name];center=35.2;side=center+w/2+.08;h0=13.4112;h1=13.4112+2.0
 checks.append({'interface':label,'estimated_width_m':w,'estimated_clear_height_m':2.0,'nominal_person_width_m':person,'center_ray_clear':not ray_obj(ob,(x0,center,h0+1),(1,0,0),x1-x0)[0],'side_control_hits_wall':ray_obj(ob,(x0,side,h0+1),(1,0,0),x1-x0)[0],'lintel_bottom_z':h1})
res={'reopened_twice':True,'stairs':clearance,'person_clear_width_headroom_all_pass':all(s['headroom_pass'] and s['width_margin_total_m']>=0 for s in clearance),'penthouse_floor_path':{'person_square_width_m':person,'grid_spacing_m':step,'start_xy':path[0] if path else None,'goal_xy':path[-1] if path else None,'connected_path_found':bool(path),'path_waypoints':path[::max(1,len(path)//12)] if path else [],'obstacle_rule':'Any 0.8m square footprint intersecting roof aperture outside the estimated stair landing is treated as unsupported.'},'doorways':checks,'root':[0,0,0],'shell_xy':list(bpy.data.objects['POTR_Official_864_Structural_Envelope'].dimensions[:2]),'missing_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]}
(D/'round7_person_clear_checks.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
