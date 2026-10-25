import json
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
root=r'C:/Users/Tobin/Documents/Blender/PurdueMap'
marker=(-282.5,44.0)
g=json.load(open(root+'/modular/buildings/target_buildings_gis.json'))['LWSN']
G=Polygon([(x-marker[0],y-marker[1]) for x,y in g['world_polygon']])
geo=json.load(open(root+'/audit/batch2_lawson/r7_shell_edges.json'))
lines=[]
for key in ('LWSN_Exterior_Brick','LWSN_Rotunda_Curtain_Glass'):
 lines.extend(LineString(e) for e in geo[key]['edges'])
S=unary_union(lines)
print('GIS bounds',G.bounds,'area',round(G.area,3),'perimeter',round(G.length,3))
print('structural wall baseline bounds',S.bounds,'length',round(S.length,3))
print('GIS boundary to structural line Hausdorff m',round(G.boundary.hausdorff_distance(S),4))
print('GIS boundary length outside 0.1m wall buffer',round(G.boundary.difference(S.buffer(.1)).length,3))
print('GIS boundary length outside 0.01m wall buffer',round(G.boundary.difference(S.buffer(.01)).length,3))
print('wall baseline length within 0.1m GIS boundary',round(S.intersection(G.boundary.buffer(.1)).length,3),'of',round(S.length,3))
print('structural segments',len(lines),'GIS boundary points',len(g['world_polygon']))
print('gis to structure median distance',round(sum(G.boundary.distance(p) for p in G.boundary.geoms)/len(G.boundary.geoms),4) if hasattr(G.boundary,'geoms') else '')
ring=[(x-marker[0],y-marker[1]) for x,y in g['world_polygon']]
from shapely.geometry import LineString
bad=[]
for i in range(len(ring)):
 seg=LineString([ring[i],ring[(i+1)%len(ring)]])
 d=seg.distance(S)
 if d>.1: bad.append({'i':i,'length_m':round(seg.length,2),'distance_m':round(d,2),'a':ring[i],'b':ring[(i+1)%len(ring)]})
print('unrepresented GIS segments',bad)
