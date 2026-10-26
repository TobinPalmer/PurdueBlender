import json, math
from shapely.geometry import Polygon,box
p=json.load(open('audit/tarkington_hall/gis_feature_662.json',encoding='utf8'))['feature']
o=(-591.6124877929688,348.0); sx=111412.84*math.cos(math.radians(40.4274)); sy=111040
rings=p['geometry']['rings']; r=[[((x+86.9137)*sx-o[0],(y-40.4274)*sy-o[1]) for x,y in q] for q in rings]
g=Polygon(r[0],r[1:])
for lo,hi in [(17,64),(-54,-7)]:
 for side in [-1,1]:
  q=g.intersection(box(-100,lo,0,hi) if side==-1 else box(0,lo,100,hi))
  print(lo,hi,side,q.bounds,q.area)
  for y in [lo+2,(lo+hi)/2,hi-2]:
   s=q.intersection(box(-100,y-.05,100,y+.05))
   print(' ',y,s.bounds)
