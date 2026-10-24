import json
j=json.load(open('audit/official_purdue_buildings_wgs84.json',encoding='utf-8'))
f=next(f for f in j['features'] if f['attributes']['FID']==604)
r=f['geometry']['rings'][0]
p=[((x+86.9137)*84810.60416539927,(y-40.4274)*111040) for x,y in r]
for i in range(0,len(p),5): print(i, ' '.join(f'{a:.1f}' for a in p[i]))
