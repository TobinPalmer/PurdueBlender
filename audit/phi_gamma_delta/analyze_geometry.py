import json, math
from pathlib import Path
root=Path('.')
def mercator_local(p):
    x,y=p; R=6378137.0
    lon=math.degrees(x/R)
    lat=math.degrees(2*math.atan(math.exp(y/R))-math.pi/2)
    X=(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))
    Y=(lat-40.4274)*111040.0
    return X,Y
f=json.load(open(root/'audit/phi_gamma_delta/sources/purdue_fid787.geojson',encoding='utf-8'))['features'][0]
pts=[mercator_local(p) for p in f['geometry']['rings'][0]]
print('FID787 ATTRS',json.dumps(f['attributes'],indent=2))
print('FID787 local bounds',min(p[0] for p in pts),max(p[0] for p in pts),min(p[1] for p in pts),max(p[1] for p in pts))
print('FID787 local ring',[[round(x,3),round(y,3)] for x,y in pts])
lcc=json.load(open(root/'audit/latino_cultural_center_5f0d139/sources/purdue_building_shapes_fid743.json',encoding='utf-8'))
print('FID743 keys',lcc.keys())
print(json.dumps(lcc,indent=2)[:500])
