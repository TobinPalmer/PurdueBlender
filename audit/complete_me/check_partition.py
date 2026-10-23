import sys,json
from pathlib import Path
sys.path.insert(0,'audit/walc_review/deps')
from shapely.geometry import Polygon,LineString
p=Path('audit/complete_me/partitions.py');s=p.read_text();ns={};exec(s[s.index('def pt'):s.index('count=0')],ns);d=json.load(open('audit/official_building_references.json'));poly=Polygon(next(a['rings_xy_m'][0] for a in d['buildings'] if a['fid']==857));bad=[]
for i,line in enumerate(ns['lines']):
 q=LineString([ns['pt'](*v) for v in line]);outside=q.difference(poly).length
 if outside>.1:bad.append([i,outside,q.length])
print(bad)
