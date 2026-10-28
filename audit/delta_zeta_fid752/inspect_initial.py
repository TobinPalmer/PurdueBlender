import bpy,json,os,math
HERE=os.path.dirname(__file__); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841601_7ae6159.blend')
FEATURE=os.path.join(HERE,'sources','purdue_gis_fid752_2026-10-28_3857.json')
raw=json.load(open(FEATURE,encoding='utf-8-sig'))
bpy.ops.wm.open_mainfile(filepath=ASSET)
objs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  coords=[o.matrix_world@v.co for v in o.data.vertices]
  objs.append({'object':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'bounds_world_m':[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)],'materials':[m.name for m in o.data.materials if m]})
f=raw['features'][0]; ring=f['geometry']['rings'][0]
if ring[0]==ring[-1]:ring=ring[:-1]
R=6378137.0; lat0=40.4274; lon0=-86.9137; src=[]
for x,y in ring:
 lon=x/R*180/math.pi; lat=2*math.atan(math.exp(y/R))-math.pi/2; lat=lat*180/math.pi
 src.append([(lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0])
report={'asset':'modular/buildings/massing_house_301841601_7ae6159.blend','scene':bpy.context.scene.name,'collection_names':[c.name for c in bpy.data.collections],'objects':objs,'source_fid':f['attributes']['FID'],'source_attributes':f['attributes'],'source_ring_local_xy_m':src,'source_bounds_xy_m':[[min(p[i] for p in src),max(p[i] for p in src)] for i in (0,1)],'source_vertex_count':len(src),'projection':'Inverse Web Mercator WKID 102100/3857 then repository-local approximate conversion; not surveyed.'}
json.dump(report,open(os.path.join(HERE,'initial_inspection.json'),'w',encoding='utf-8'),indent=2)
print('DZ_INITIAL='+json.dumps({k:v for k,v in report.items() if k not in {'source_ring_local_xy_m'}}))
