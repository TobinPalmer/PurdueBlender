import bpy,json,math,os,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'modular';ID='massing_purdue_fire_department_520430b';ASSET=MOD/'buildings'/f'{ID}.blend';BASE=ROOT/'audit'/'purdue_fire_department';MAN=json.loads((MOD/'manifest.json').read_text(encoding='utf-8'));REC=next(x for x in MAN['assets'] if x['id']==ID);origin=REC['placement_origin_xy_m']
gj=json.loads((BASE/'sources'/'dmnt_feature_211.geojson').read_text(encoding='utf-8'));feat=gj['features'][0];props=feat['properties'];coords=feat['geometry']['coordinates'][0][:-1]
lat0,lon0=40.4274,-86.9137
source=[((lon-lon0)*111412.84*math.cos(math.radians(lat0))-origin[0],(lat-lat0)*111040.0-origin[1]) for lon,lat in coords]
assetsha=hashlib.sha256(ASSET.read_bytes()).hexdigest();assert assetsha=='6a20209ae3db99c028a16d7df11e42a87577b8bee29afc5e0ead98a779b03817'
bpy.ops.wm.open_mainfile(filepath=str(ASSET));col=bpy.data.collections.get(REC['collection']);obj=bpy.data.objects.get('DMNT | GIS-footprint brick station shell');assert col and obj and obj.type=='MESH'
verts=[tuple(obj.matrix_world@v.co) for v in obj.data.vertices];lower=[(x,y) for x,y,z in verts if abs(z)<1e-5]
def nd(p,arr):return min(math.hypot(p[0]-q[0],p[1]-q[1]) for q in arr)
se=[nd(p,lower) for p in source];re=[nd(p,source) for p in lower]
out={'asset_sha256':assetsha,'feature_id':feat['id'],'building_name':props['BUILDING_N'],'abbr':props['BLDG_ABBR'],'address':props['ADDRESS'],'placement_origin_xy_m':origin,'source_local_vertex_count':len(source),'model_lower_vertex_count':len(lower),'source_to_model_max_vertex_error_m':max(se),'model_to_source_max_vertex_error_m':max(re),'model_local_shell_bounds_m':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]}
Path(__file__).with_name('localized_footprint_probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
