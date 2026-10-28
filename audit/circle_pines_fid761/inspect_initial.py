import bpy,json,os,math
from mathutils import Vector
HERE=os.path.dirname(__file__);ROOT=os.path.abspath(os.path.join(HERE,'..','..'));cfg={'asset':'massing_house_301841609_c6c9ac4','object':'House_301841609','feature':'sources/purdue_gis_fid761_2026-10-28_3857.json'}
ASSET=os.path.join(ROOT,'modular','buildings',cfg['asset']+'.blend');raw=json.load(open(os.path.join(HERE,cfg['feature']),encoding='utf-8-sig'));bpy.ops.wm.open_mainfile(filepath=ASSET)
objs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  co=[o.matrix_world@v.co for v in o.data.vertices];objs.append({'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'bounds_world_xyz_m':[[min(v[i] for v in co),max(v[i] for v in co)] for i in range(3)],'materials':[m.name for m in o.data.materials if m]})
f=raw['features'][0];r=f['geometry']['rings'][0];r=r[:-1] if r[0]==r[-1] else r;R=6378137.;pts=[]
for x,y in r:
 lon=x/R*180/math.pi;lat=(2*math.atan(math.exp(y/R))-math.pi/2)*180/math.pi;pts.append([(lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.])
out={'asset':f"modular/buildings/{cfg['asset']}.blend",'scene':bpy.context.scene.name,'objects':objs,'feature_id':f['attributes']['FID'],'attributes':f['attributes'],'gis_ring_xy_local_m':pts,'gis_unique_ring_vertex_count':len(pts),'gis_bbox_xy_m':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in (0,1)],'transform':'Inverse Web Mercator WKID 102100/latestWkid 3857 then repository approximate campus-local conversion; not survey control.'}
json.dump(out,open(os.path.join(HERE,'initial_inspection.json'),'w',encoding='utf-8'),indent=2);print('CP_INITIAL='+json.dumps({k:v for k,v in out.items() if k!='gis_ring_xy_local_m'}))
