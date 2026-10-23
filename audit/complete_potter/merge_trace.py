import sys,json
sys.path.insert(0,'audit/walc_review/deps')
from shapely.geometry import LineString
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
D='audit/complete_potter/';a=json.load(open(D+'historic_walls.json'));out={}
for k,v in a.items():
 p=unary_union([LineString(x).buffer(.08,cap_style=2) for x in v['lines']]).buffer(.13,join_style=2).buffer(-.13,join_style=2).simplify(.015,preserve_topology=True);verts=[];faces=[];lookup={}
 def idx(x,y,z):
  key=(round(x,5),round(y,5),z)
  if key not in lookup:lookup[key]=len(verts);verts.append(key)
  return lookup[key]
 for poly in getattr(p,'geoms',[p]):
  for tri in constrained_delaunay_triangles(poly).geoms:
   pts=list(tri.exterior.coords)[:3];faces.append([idx(x,y,0) for x,y in reversed(pts)]);faces.append([idx(x,y,2.7) for x,y in pts])
  for ring in [poly.exterior,*poly.interiors]:
   pts=list(ring.coords)
   for u,w in zip(pts,pts[1:]):faces.append([idx(*u,0),idx(*w,0),idx(*w,2.7),idx(*u,2.7)])
 out[k]={'vertices':verts,'faces':faces,'registration_iou':v['registration_iou']};print(k,len(verts),len(faces))
json.dump(out,open(D+'merged_interior.json','w'))
