import bpy,math,json,bmesh
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
metal=bpy.data.materials.get('POTR_Stair_Rail_Metal')
# Add the upper landing and twin-side handrails to every estimated 2016-plan stair core/level.
rails_col=bpy.data.collections.get('POTR_Historic2016_StairRails_Estimate')
if not rails_col: rails_col=bpy.data.collections.new('POTR_Historic2016_StairRails_Estimate');c.children.link(rails_col)
def cube_mesh(name,loc,dim,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for q in list(o.users_collection):q.objects.unlink(o)
 rails_col.objects.link(o);o.data.materials.append(mat);o['source']='Estimated stair landing inferred from 2016 existing-plan stair core label; not measured';return o
for ci,(x,y) in enumerate([(49.8,1.5),(49.9,53.4),(10.5,35.2)],1):
 for level,(z0,z1) in enumerate([(-4.064,.6096),(.6096,4.8768),(4.8768,9.144),(9.144,13.4112)]):
  height=z1-z0;half=height/2;run=2.7;width=1.05
  # Upper west landing completes the return flight. Existing east landing is embedded in each flight mesh.
  land=cube_mesh(f'POTR_2016_StairCore{ci}_Level{level}_UpperLanding',(x-run/2-.62,y,z1-.08),(.62,2.10,.16),bpy.data.materials['POTR_Interior_Concrete_Stairs'])
  land['connects_levels']=f'{z0:.4f} to {z1:.4f}m'
  cu=bpy.data.curves.new(f'POTR_StairCore{ci}_Level{level}_Handrail_Curve','CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=.026;cu.bevel_resolution=3
  # Four continuous rails, one on each side of each flight.
  for yy in [y-width,y]:
   sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(x-run/2,yy,z0+.98,1);sp.points[1].co=(x+run/2,yy,z0+half+.98,1)
  for yy in [y,y+width]:
   sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(x+run/2,yy,z0+half+.98,1);sp.points[1].co=(x-run/2,yy,z1+.98,1)
  # Vertical balusters at approximately 0.9m spacing, standing on each flight's tread nosing.
  for yy in [y-width,y,y+width]:
   for i in range(4,13,4):
    if yy<=y:
     xx=x-run/2+run*i/12;zz=z0+half*i/12
    else:
     xx=x+run/2-run*i/12;zz=z0+half+half*i/12
    sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(xx,yy,zz+.08,1);sp.points[1].co=(xx,yy,zz+.98,1)
  ob=bpy.data.objects.new(f'POTR_2016_StairCore{ci}_Level{level}_Handrails',cu);rails_col.objects.link(ob);ob.data.materials.append(metal);ob['source']='Handrails/balusters estimated; 2016 plan supports core location only, not rail configuration.'
# Tag floor slabs and roof with opening dimensions/evidence.
for nm in ['POTR_Interior_Slab_Level_1_EstimatedElevation','POTR_Interior_Slab_Level_2_EstimatedElevation','POTR_Interior_Slab_Level_3_EstimatedElevation','POTR_Official_864_Roof']:
 c.objects[nm]['stair_openings']='Three Boolean apertures, 4.6 x 3.6m, aligned to estimated S01–S03 core centers on 2016 plans; dimensions and alignment remain approximate.'
bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];sc=bpy.context.scene
# Direct object-ray checks at each aperture center ensure slab geometry does not block the core.
checks=[]
for nm in ['POTR_Interior_Slab_Level_1_EstimatedElevation','POTR_Interior_Slab_Level_2_EstimatedElevation','POTR_Interior_Slab_Level_3_EstimatedElevation','POTR_Official_864_Roof']:
 slab=c.objects[nm];z=(min(v.co.z for v in slab.data.vertices)+max(v.co.z for v in slab.data.vertices))/2
 for i,(x,y) in enumerate([(49.8,1.5),(49.9,53.4),(10.5,35.2)],1):
  hit,loc,nor,face=slab.ray_cast(Vector((x,y,z+1)),Vector((0,0,-1)),distance=2)
  checks.append({'slab':nm,'core':i,'center_ray_blocked':bool(hit)})
print(json.dumps({'reopened':True,'root':list(c.objects['AssetRoot_potter_engineering'].location),'shell_xy':list(c.objects['POTR_Official_864_Structural_Envelope'].dimensions[:2]),'rails':len([o for o in c.all_objects if 'Handrails' in o.name]),'open_aperture_checks':checks},indent=2))
