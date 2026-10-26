import json
from pathlib import Path
from shapely.geometry import Polygon, Point

f=Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap\audit\south_hall_refine\gis_footprint_r1.json")
d=json.loads(f.read_text(encoding="utf-8"))
p=Polygon(d["local_outline_xy_m"])
safe=p.buffer(-4.0)
candidates=[(x/2,y/2) for x in range(-150,100,4) for y in range(-110,50,4) if safe.contains(Point(x/2,y/2))]
selected=[]
# Deterministic farthest-point samples distribute schematic labs across the safe footprint.
first=safe.representative_point(); selected.append((first.x,first.y))
while len(selected)<9:
    c=max((pt for pt in candidates if min((pt[0]-x)**2+(pt[1]-y)**2 for x,y in selected)>=64),key=lambda pt:min((pt[0]-x)**2+(pt[1]-y)**2 for x,y in selected),default=None)
    if c is None: break
    selected.append(c)
print("safe area",round(safe.area,2),"selected",len(selected))
for i,pnt in enumerate(selected,1): print(i,tuple(round(v,2) for v in pnt))
(f.parent/"schematic_lab_centers_r1.json").write_text(json.dumps({"purpose":"representative schematic room locations only; no floor plan available","building":"south_hall","outline_source_feature_id":528,"interior_clearance_m":4.0,"centers_xy_local_m":[[round(x,3),round(y,3)] for x,y in selected]},indent=2)+"\n",encoding="utf-8")
