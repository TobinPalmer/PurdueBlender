import bpy, json, math, os

HERE=os.path.dirname(__file__)
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301840872_582df9d.blend')
FEATURE=os.path.join(HERE,'sources','purdue_gis_fid783_2026-10-28_3857.json')
with open(FEATURE,encoding='utf-8-sig') as f: raw=json.load(f)
bpy.ops.wm.open_mainfile(filepath=ASSET)
obj=bpy.data.objects['House_301840872']; mesh=obj.data
R=6378137.0; lat0=40.4274; lon0=-86.9137
ring=raw['features'][0]['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
local=[]
for mx,my in ring:
    lon=mx/R*180/math.pi; lat=(2*math.atan(math.exp(my/R))-math.pi/2)*180/math.pi
    local.append([(lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0])
base=[]
for v in mesh.vertices:
    if abs(v.co.z)<1e-6: base.append([v.co.x,v.co.y])
report={
  'asset_id':'massing_house_301840872_582df9d','feature_id':783,
  'live_gis_source':'sources/purdue_gis_fid783_2026-10-28_3857.json',
  'crs':'WKID 102100/latestWkid 3857 to longitude/latitude to repository local approximation; not surveyed',
  'source_ring_xy_m':local,
  'existing_asset_base_xy_m':base,
  'existing_asset_bounds_xy_m':[[min(v.co.x for v in mesh.vertices),max(v.co.x for v in mesh.vertices)],[min(v.co.y for v in mesh.vertices),max(v.co.y for v in mesh.vertices)]],
  'existing_asset_bounds_z_m':[min(v.co.z for v in mesh.vertices),max(v.co.z for v in mesh.vertices)],
  'existing_asset_vertex_count':len(mesh.vertices),'existing_asset_polygon_count':len(mesh.polygons),
  'existing_materials':[m.name for m in mesh.materials if m],
  'source_ring_unique_vertices':len(local),
  'initial_limit':'The legacy asset is an eight-vertex rectangular box with 8 faces. Bounds alone look close to the FID ring but do not capture its stepped/concave shape.'
}
with open(os.path.join(HERE,'legacy_geometry.json'),'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('LEGACY_GEOMETRY='+json.dumps({k:v for k,v in report.items() if k not in {'source_ring_xy_m','existing_asset_base_xy_m'}}))
