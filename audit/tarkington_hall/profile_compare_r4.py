import json,math
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
p=json.load(open('audit/tarkington_hall/gis_feature_662.json',encoding='utf8'))['feature']; o=(-591.6124877929688,348); sx=111412.84*math.cos(math.radians(40.4274)); sy=111040
rr=[ [((x+86.9137)*sx-o[0],(y-40.4274)*sy-o[1]) for x,y in ring] for ring in p['geometry']['rings'] ]; g=Polygon(rr[0],rr[1:])
d=json.load(open('audit/tarkington_hall/shell_vertices_r4.json',encoding='utf8'))
m=unary_union([MultiPoint(q['vertices_xy']).convex_hull for q in d['objects']])
def ints(poly,y):
 s=poly.intersection(box(-100,y-.05,100,y+.05))
 out=[]
 for a in (s.geoms if hasattr(s,'geoms') else [s]):
  if a.area>0:out.append((round(a.bounds[0],1),round(a.bounds[2],1)))
 return out
for y in range(-30,36):
 gi=ints(g,y); mi=ints(m,y)
 if gi!=mi: print(y,'GIS',gi,'MODEL',mi)

