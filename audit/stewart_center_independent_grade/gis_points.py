import json,math
p=json.load(open('audit/stewart_center_independent_grade/purdue_gis_feature_615.json'))['features'][0]['geometry']['rings'][0]
lat0,lon0=40.4274,-86.9137; ox,oy=91.04999828338623,-253.375
q=[((lon-lon0)*111412.84*math.cos(math.radians(lat0))+ox,(lat-lat0)*111040+oy) for lon,lat in p]
a=sum(q[i][0]*q[(i+1)%len(q)][1]-q[(i+1)%len(q)][0]*q[i][1] for i in range(len(q)))/2
print('n',len(q),'area',a)
for i,(x,y) in enumerate(q): print(f'{i}: {x:.2f}, {y:.2f}')
