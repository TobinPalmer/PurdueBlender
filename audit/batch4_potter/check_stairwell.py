import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];levels=['POTR_Interior_Slab_Level_1_EstimatedElevation','POTR_Interior_Slab_Level_2_EstimatedElevation','POTR_Interior_Slab_Level_3_EstimatedElevation','POTR_Official_864_Roof'];cores=[(49.8,1.5),(49.9,53.4),(10.5,35.2)];checks=[]
for nm in levels:
 o=c.objects[nm];z=(min(v.co.z for v in o.data.vertices)+max(v.co.z for v in o.data.vertices))/2
 for i,(x,y) in enumerate(cores,1):
  hit=o.ray_cast(Vector((x,y,z+1)),Vector((0,0,-1)),distance=2)[0];checks.append({'slab':nm,'core':i,'center_ray_blocked':bool(hit)})
def bounds(o):
 pts=[o.matrix_world@v.co for v in o.data.vertices];return [min(p[j] for p in pts) for j in range(3)],[max(p[j] for p in pts) for j in range(3)]
interfaces=[]
for i in range(1,4):
 pairs=[(f'POTR_2016_StairCore{i}_Basement_Landing_Estimate',f'POTR_2016_StairCore{i}_Level0_Flight')]
 for l in range(4):
  f=c.objects.get(f'POTR_2016_StairCore{i}_Level{l}_Flight');u=c.objects.get(f'POTR_2016_StairCore{i}_Level{l}_UpperLanding')
  if f and u:pairs.append((f.name,u.name))
 for an,bn in pairs:
  a0,a1=bounds(c.objects[an]);b0,b1=bounds(c.objects[bn]);g=[max(0,b0[j]-a1[j],a0[j]-b1[j]) for j in range(3)];interfaces.append({'a':an,'b':bn,'aabb_gap_m':g,'bounds_overlap_or_contact':max(g)<1e-4})
# 4S04 doorway is open in both wall meshes at its center and blocked at either side of the opening.
mass=c.objects['POTR_Historic2016_Room401_Penthouse_Massing'];wallx=min(v.co.x for v in mass.data.vertices);en=[o for o in c.all_objects if o.name.startswith('POTR_4S04_')];door=[]
for y in (35.3,34.7,35.9):
 origin=Vector((wallx-1,y,14.4));d=Vector((1,0,0));room=mass.ray_cast(origin,d,distance=3)[0];eh=[]
 for o in en:
  inv=o.matrix_world.inverted();eh.append(o.ray_cast(inv@origin,(inv.to_3x3()@d).normalized(),distance=3)[0])
 door.append({'y':y,'room401_wall_blocks':bool(room),'4S04_wall_blocks':any(eh)})
objs=list(c.all_objects);data={'reopened':True,'object_count':len(objs),'root':list(c.objects['AssetRoot_potter_engineering'].location),'shell_xy_dimensions':list(c.objects['POTR_Official_864_Structural_Envelope'].dimensions[:2]),'stair_flight_meshes':len([o for o in objs if '_Level' in o.name and o.name.endswith('_Flight')]),'upper_landings':len([o for o in objs if '_UpperLanding' in o.name]),'basement_landings':len([o for o in objs if 'Basement_Landing' in o.name]),'handrail_assemblies':len([o for o in objs if o.name.endswith('_Handrails')]),'4S04_enclosure_parts':len(en),'slab_aperture_center_ray_checks':checks,'landing_flight_aabb_checks':interfaces,'4S04_doorway_ray_checks':door,'missing_external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]};(D/'stairwell_checks.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))
