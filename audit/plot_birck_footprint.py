import json, matplotlib.pyplot as plt
j=json.load(open('audit/official_purdue_buildings_wgs84.json',encoding='utf-8'))
f=next(f for f in j['features'] if f['attributes']['FID']==604)
ring=f['geometry']['rings'][0]
pts=[((x+86.9137)*84810.60416539927,(y-40.4274)*111040) for x,y in ring]
xs,ys=zip(*pts)
plt.figure(figsize=(8,7)); plt.plot(xs,ys,'k-'); plt.fill(xs,ys,color='#c8b9a0',alpha=.4)
plt.gca().set_aspect('equal'); plt.xlabel('X east project m'); plt.ylabel('Y north project m'); plt.grid(); plt.savefig('audit/birck_gis_footprint.png',dpi=140)
