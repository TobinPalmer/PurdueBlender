import bpy,json,shutil
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter')
shutil.copy2(P,D/'round5_before_round6_stair_levels.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
# Stair geometry was measured from slab undersides. Regrade each run to the actual slab top walk surfaces.
for i in range(1,4):
 for level in range(3):
  ob=c.objects.get(f'POTR_2016_StairCore{i}_Level{level}_Flight')
  rail=c.objects.get(f'POTR_2016_StairCore{i}_Level{level}_Handrails')
  if not ob: continue
  for v in ob.data.vertices:v.co.z += .15
  ob.data.update();ob['walk_surface_alignment']='Raised 0.15 m from slab-underside datum to finished floor surfaces on both connected levels; exact stair layout remains estimated from 2016 core labels.'
  if rail and rail.type=='CURVE':
   for spline in rail.data.splines:
    for p in spline.points:p.co.z += .15
   rail['walk_surface_alignment']='Rail geometry shifted with stair to slab-top walk-surface elevations.'
# The penthouse flight starts at floor 3 slab top and meets the penthouse floor at the roof opening.
ob=c.objects.get('POTR_2016_StairCore3_Level3_Flight');rail=c.objects.get('POTR_2016_StairCore3_Level3_Handrails')
if ob:
 lo,hi=9.144,13.4112;lo2,hi2=9.294,13.4112;scale=(hi2-lo2)/(hi-lo)
 for v in ob.data.vertices:v.co.z=lo2+(v.co.z-lo)*scale
 ob.data.update();ob['walk_surface_alignment']='Vertically regraded from floor 3 slab top (z=9.294 m) to estimated penthouse floor at roof opening (z=13.4112 m). Plan registration and stair profile are approximate.'
 if rail and rail.type=='CURVE':
  for spline in rail.data.splines:
   for p in spline.points:p.co.z=lo2+(p.co.z-lo)*scale
  rail['walk_surface_alignment']='Vertically regraded with stair from floor 3 finished surface to estimated penthouse floor.'
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
# Report post-save endpoint tread heights against the walkable surface datums.
rows=[]
for i in range(1,4):
 for level,(lower,upper) in enumerate([(-3.914,.7596),(.7596,5.0268),(5.0268,9.294)]):
  ob=c.objects.get(f'POTR_2016_StairCore{i}_Level{level}_Flight')
  if not ob:continue
  faces=[]
  for f in ob.data.polygons:
   if f.normal.z>.99 and f.area>.08:
    z=sum(ob.data.vertices[k].co.z for k in f.vertices)/len(f.vertices); faces.append((z,f.area))
  rows.append({'core':i,'transition':level,'lower_walk_surface_z':lower,'first_tread_top_z':round(min(faces)[0],5),'first_tread_offset_from_floor':round(min(faces)[0]-lower,5),'upper_walk_surface_z':upper,'last_tread_top_z':round(max(faces)[0],5),'last_tread_riser_to_landing':round(upper-max(faces)[0],5)})
ob=c.objects['POTR_2016_StairCore3_Level3_Flight'];faces=[sum(ob.data.vertices[k].co.z for k in f.vertices)/len(f.vertices) for f in ob.data.polygons if f.normal.z>.99 and f.area>.08]
rows.append({'core':3,'transition':'level3_to_4S04','lower_walk_surface_z':9.294,'first_tread_top_z':round(min(faces),5),'first_tread_offset_from_floor':round(min(faces)-9.294,5),'upper_walk_surface_z':13.4112,'last_tread_top_z':round(max(faces),5),'last_tread_riser_to_landing':round(13.4112-max(faces),5)})
(D/'stair_walk_surface_round6.json').write_text(json.dumps({'reopened':True,'evidence':'Interior slab upper surface bounds from POTR_Interior_Slab_Level_0..3; 2016 plan supports approximate S01-S03 core locations and Room401/4S04 connection.','interfaces':rows},indent=2));print(json.dumps(rows,indent=2))
