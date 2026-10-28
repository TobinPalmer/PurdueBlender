import bpy,json,math,os
from mathutils import Vector
HERE=os.path.dirname(__file__);ROOT=os.path.abspath(os.path.join(HERE,'..','..'));cfg=json.load(open(os.path.join(HERE,'build_config.json'),encoding='utf-8'))
raw=json.load(open(os.path.join(HERE,cfg['source_feature_file']),encoding='utf-8-sig'));ASSET=os.path.join(ROOT,'modular','buildings','massing_house_301841601_7ae6159.blend');bpy.ops.wm.open_mainfile(filepath=ASSET);obj=bpy.data.objects[cfg['object_name']]
ring=raw['features'][0]['geometry']['rings'][0];ring=ring[:-1] if ring[0]==ring[-1] else ring;R=6378137.;lat0=40.4274;lon0=-86.9137;src=[]
for x,y in ring:
 lon=x/R*180/math.pi;lat=(2*math.atan(math.exp(y/R))-math.pi/2)*180/math.pi;src.append([(lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.])
bounds=[[min(p[i] for p in src),max(p[i] for p in src)] for i in (0,1)];base=[]
for v in obj.data.vertices:
 if abs(v.co.z)<1e-5 and bounds[0][0]-1<=v.co.x<=bounds[0][1]+1 and bounds[1][0]-1<=v.co.y<=bounds[1][1]+1:base.append([v.co.x,v.co.y])
errors=[min(math.hypot(v[0]-p[0],v[1]-p[1]) for v in base) for p in src]
out={'feature_id':752,'source_ring_unique_vertices':len(src),'source_ring_xy_m':src,'model_wall_base_vertices_xy_m':base,'nearest_model_vertex_error_each_source_corner_m':errors,'max_source_corner_error_m':max(errors),'geometry_check':'The official GIS ring vertices are used to define the structural wall base. This compares transformed XY only and does not validate source horizontal/vertical accuracy or roof/facade dimensions.','transform':'Inverse Web Mercator WKID 102100/latestWkid 3857 followed by repository-local approximate campus transform; not surveyed.'}
json.dump(out,open(os.path.join(HERE,'final_geometry.json'),'w',encoding='utf-8'),indent=2);print('DZ_GEOMETRY='+json.dumps({k:v for k,v in out.items() if k not in {'source_ring_xy_m','model_wall_base_vertices_xy_m'}}))
