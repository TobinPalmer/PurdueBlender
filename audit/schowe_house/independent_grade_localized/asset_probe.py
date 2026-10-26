import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ASSET=Path(bpy.data.filepath).resolve(); ROOT=ASSET.parents[2]
AID='massing_purdue_center_for_regional_development_scho_a2375c9'
COLL='Asset_'+AID
EXPECTED='43fbc9e65e24e93710b38d868ce21e0162d5493b0a9fb0d2d64353ce5ea1837d'
OUT=Path(__file__).resolve().parent/'asset_probe.json'
m=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
rec=next(x for x in m['assets'] if x['id']==AID)
anchor=rec['placement_origin_xy_m']
scene=bpy.context.scene; col=bpy.data.collections.get(COLL)
objs=list(col.all_objects) if col else []; meshes=[o for o in objs if o.type=='MESH']
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest(); deps=bpy.context.evaluated_depsgraph_get()
pts=[]
for o in meshes:
    ev=o.evaluated_get(deps)
    pts.extend(ev.matrix_world@Vector(c) for c in ev.bound_box)
local_bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else []
world_bounds=[[local_bounds[i][0]+(anchor[i] if i<2 else 0),local_bounds[i][1]+(anchor[i] if i<2 else 0)] for i in range(3)] if local_bounds else []
raw=json.loads((ROOT/'audit/schowe_house/sources/purdue_gis_fid295_schowe_house_2026-10-26.json').read_text(encoding='utf-8'))
f=raw['features'][0]; attrs=f['attributes']; ring=f['geometry']['rings'][0]
lat0=40.4274; lon0=-86.9137; sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
poly=[((lon-lon0)*sx,(lat-lat0)*sy) for lon,lat in ring[:-1]]
source_segs=list(zip(poly,poly[1:]+poly[:1]))
wall=next((o for o in meshes if o.name.endswith('_Perimeter_Brickwork')),None)
wall_segs=[]
if wall:
    ev=wall.evaluated_get(deps); me=ev.to_mesh(); co=[ev.matrix_world@v.co for v in me.vertices]
    for e in me.edges:
        a,b=co[e.vertices[0]],co[e.vertices[1]]
        if abs(a.z)<.005 and abs(b.z)<.005 and math.hypot(a.x-b.x,a.y-b.y)>1e-5:
            wall_segs.append(((a.x+anchor[0],a.y+anchor[1]),(b.x+anchor[0],b.y+anchor[1])))
    ev.to_mesh_clear()
def dseg(p,s):
    a,b=s; dx=b[0]-a[0]; dy=b[1]-a[1]; q=dx*dx+dy*dy
    if q==0:return math.dist(p,a)
    t=max(0.,min(1.,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/q))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def sample(s,step=.25):
    a,b=s;n=max(1,math.ceil(math.dist(a,b)/step));return [(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1)]
gis_samples=[p for s in source_segs for p in sample(s)]
wall_samples=[p for s in wall_segs for p in sample(s)]
g2w=[min(dseg(p,s) for s in wall_segs) for p in gis_samples]
w2g=[min(dseg(p,s) for s in source_segs) for p in wall_samples]
imgs=[{'name':im.name,'packed':bool(im.packed_file),'path':im.filepath} for im in bpy.data.images if im.name!='Render Result']
result={'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),'asset_sha256':sha,'expected_sha256':EXPECTED,'sha_matches':sha==EXPECTED,
 'blender_version':bpy.app.version_string,'scene':scene.name,'collection':COLL if col else None,'object_count':len(objs),'mesh_count':len(meshes),
 'placement_origin_xy_m':anchor,'local_bounds_m':local_bounds,'reconstructed_world_bounds_m':world_bounds,
 'gis_feature_id':attrs.get('OBJECTID'),'gis_name':attrs.get('Name'),'gis_address':attrs.get('ADDRESS'),'gis_area_m2':attrs.get('Shape.STArea()'),
 'gis_to_wall_max_m':max(g2w) if g2w else None,'wall_to_gis_max_m':max(w2g) if w2g else None,'gis_to_wall_mean_m':sum(g2w)/len(g2w) if g2w else None,
 'wall_segment_count':len(wall_segs),'material_names':sorted({mat.name for o in meshes for mat in o.data.materials if mat}),
 'meshes_without_material':[o.name for o in meshes if not o.data.materials],'images':imgs,'linked_libraries':[c.library.filepath for c in bpy.data.collections if c==col and c.library]}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if sha!=EXPECTED: raise RuntimeError('asset SHA mismatch')
if not col or not wall or scene.name!='Building_'+AID: raise RuntimeError('expected asset scene, collection, or wall missing')
if not rec.get('local_coordinates'): raise RuntimeError('manifest does not mark asset local')
