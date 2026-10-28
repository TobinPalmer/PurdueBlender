import bpy, json, os, math
from mathutils import Vector
HERE=os.path.dirname(__file__); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
CFG=json.load(open(os.path.join(HERE,'build_config.json'),encoding='utf-8'))
FEATURE=os.path.join(HERE,CFG['source_feature_file'])
ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301840872_582df9d.blend')
raw=json.load(open(FEATURE,encoding='utf-8-sig'))
bpy.ops.wm.open_mainfile(filepath=ASSET)
obj=bpy.data.objects[CFG['object_name']]
ring=raw['features'][0]['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
R=6378137.0; lat0=CFG['coordinate_origin']['latitude']; lon0=CFG['coordinate_origin']['longitude']
src=[]
for mx,my in ring:
 lon=mx/R*180/math.pi; lat=(2*math.atan(math.exp(my/R))-math.pi/2)*180/math.pi
 src.append([(lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0])
# For every official GIS ring corner, record the nearest projected exterior
# wall-base vertex. A low error verifies the mesh footprint registration while
# excluding decorative steps and porches.
wallbase=[]
for v in obj.data.vertices:
 if abs(v.co.z)<1e-5: wallbase.append([v.co.x,v.co.y])
nearest=[min(math.hypot(x-p[0],y-p[1]) for x,y in wallbase) for p in src]
report={'feature_id':783,'source_ring_unique_vertices':len(src),'source_ring_xy_m':src,
 'model_z0_xy_m':wallbase,'nearest_model_vertex_to_each_gis_corner_m':nearest,
 'max_gis_corner_nearest_error_m':max(nearest),
 'measurement':'XY coordinates after inverse Web Mercator then repository local approximate transform; comparison uses source ring corners to nearest model vertices at z=0. This is not a survey and does not validate vertical source accuracy.'}
json.dump(report,open(os.path.join(HERE,'final_geometry.json'),'w',encoding='utf-8'),indent=2)
print('FINAL_GEOMETRY='+json.dumps({k:v for k,v in report.items() if k not in {'source_ring_xy_m','model_z0_xy_m'}}))
