import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];ASSET=ROOT/'modular/buildings/rawls_hall.blend';OUT=Path(__file__).with_name('round9_sewall_rays.json');bpy.ops.wm.open_mainfile(filepath=str(ASSET));wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];pane=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass'];verts=[wall.matrix_world@v.co for v in wall.data.vertices];polys=[tuple(p.vertices) for p in wall.data.polygons];tree=BVHTree.FromPolygons(verts,polys,all_triangles=False);rows=[]
for p in pane.data.polygons:
 pts=[pane.matrix_world@pane.data.vertices[i].co for i in p.vertices];c=sum(pts,Vector())/len(pts);n=(pane.matrix_world.to_3x3()@p.normal).normalized();res=[]
 for sign in (-1,1):
  start=c+n*(sign*.5);direction=-n*sign
  hit,normal,fi,d=tree.ray_cast(start,direction,5)
  res.append({'sign':sign,'hit':hit is not None,'distance':round(d,4) if d else None,'world_loc':[round(v,4) for v in hit] if hit else None,'face':fi})
 rows.append({'polygon':p.index,'center':[round(v,3) for v in c],'normal':[round(v,3) for v in n],'rays':res})
OUT.write_text(json.dumps(rows,indent=2));print(json.dumps(rows[:3],indent=2));print('any hits',sum(any(r['hit'] for r in x['rays']) for x in rows),'of',len(rows))
