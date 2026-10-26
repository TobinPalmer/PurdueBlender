import json,math
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
from shapely.validation import explain_validity
p=json.load(open('audit/tarkington_hall/gis_feature_662.json',encoding='utf8'))['feature']; o=(-591.6124877929688,348); sx=111412.84*math.cos(math.radians(40.4274)); sy=111040
rr=[[((x+86.9137)*sx-o[0],(y-40.4274)*sy-o[1]) for x,y in ring] for ring in p['geometry']['rings']]; g=Polygon(rr[0],rr[1:]); d=json.load(open('audit/tarkington_hall/independent_shell_vertices_r3.json',encoding='utf8')); m=unary_union([MultiPoint(q['vertices_xy']).convex_hull for q in d['objects']]);
for label,q in [('GIS_NOT_MODEL',g.difference(m)),('MODEL_NOT_GIS',m.difference(g))]:
 print('\n',label,'area',q.area,'bounds',q.bounds)
 parts=list(q.geoms) if hasattr(q,'geoms') else [q]
 for z in sorted(parts,key=lambda x:x.area,reverse=True)[:12]:print(' ',round(z.area,1),tuple(round(x,1) for x in z.bounds))
for lo,hi in [(-60,-43),(-43,-30),(-30,-15),(-15,0),(0,15),(15,28),(28,33),(33,45),(45,65)]:
 b=Polygon([(-100,lo),(100,lo),(100,hi),(-100,hi)])
 print('band',lo,hi,'gis',round(g.intersection(b).area,1),'model',round(m.intersection(b).area,1),'fn',round(g.difference(m).intersection(b).area,1),'fp',round(m.difference(g).intersection(b).area,1))
