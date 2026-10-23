import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils import Matrix
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];deps=bpy.context.evaluated_depsgraph_get();bvh=BVHTree.FromObject(wall,deps)
dirs={'North':Vector((0,1,0)),'South':Vector((0,-1,0)),'East':Vector((1,0,0)),'West':Vector((-1,0,0)),'SE_Diagonal':Vector((.7,-.7,0))}
for o in bpy.data.objects:
 if o.type=='MESH' and 'Windows_Glass' in o.name or o.type=='MESH' and 'CurtainWall_Glass' in o.name:
  d=next((v for k,v in dirs.items() if k in o.name),None)
  if not d:continue
  hits=[]
  mw=o.matrix_world
  for p in o.data.polygons:
   center=mw @ p.center
   loc,normal,idx,dist=bvh.ray_cast(center+d*.03,d,5)
   if loc is not None:hits.append(round(dist,3))
  print(o.name,'faces',len(o.data.polygons),'hit',len(hits),'median',sorted(hits)[len(hits)//2] if hits else None,'range', (min(hits),max(hits)) if hits else None)
