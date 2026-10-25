import bpy, json, hashlib, pathlib, collections
from mathutils import Vector
asset=pathlib.Path(bpy.data.filepath)
coll=bpy.data.collections.get('Asset_stewart_center')
objs=list(coll.all_objects) if coll else []
mesh=[o for o in objs if o.type=='MESH']
matless=[o.name for o in mesh if not o.data.materials or all(m is None for m in o.data.materials)]
missing=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:
        f=pathlib.Path(bpy.path.abspath(im.filepath))
        if not f.exists(): missing.append({'image':im.name,'path':im.filepath})
points=[o.matrix_world@Vector(c) for o in objs if o.type in {'MESH','CURVE','FONT'} for c in o.bound_box]
bounds=[[min(v[i] for v in points),max(v[i] for v in points)] for i in range(3)]
# Transform the cached GIS ring into the manifest-local frame.
root=pathlib.Path(__file__).parent
gis=json.loads((root/'purdue_gis_feature_615.json').read_text())
ring=gis['features'][0]['geometry']['rings'][0]
xy=[]
for lon,lat in ring:
    x=(lon+86.9137)*84810.60416539927-91.04999828338623
    y=(lat-40.4274)*111040+253.375
    xy.append((x,y))
def inside(pt):
    x,y=pt; odd=False
    for i,(ax,ay) in enumerate(xy):
        bx,by=xy[(i+1)%len(xy)]
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax: odd=not odd
    return odd
# Coarse list of objects with bounding-box center outside GIS polygon, largest first.
outs=[]
for o in objs:
    if o.type not in {'MESH','CURVE','FONT'}: continue
    qs=[o.matrix_world@Vector(c) for c in o.bound_box]
    lo=[min(v[i] for v in qs) for i in range(3)]; hi=[max(v[i] for v in qs) for i in range(3)]
    c=((lo[0]+hi[0])/2,(lo[1]+hi[1])/2)
    if not inside(c): outs.append({'name':o.name,'type':o.type,'center_xy':list(c),'size_xy':[hi[0]-lo[0],hi[1]-lo[1]],'z':[lo[2],hi[2]]})
outs.sort(key=lambda q:q['size_xy'][0]*q['size_xy'][1],reverse=True)
# Named modules, walls, roof and entrances for transparent review.
terms=('AssetRoot','STEW_R1_Wall','STEW_Ext_Wall','Stew','Fowler','Loeb','HSSE','Ringel','Roof','Entrance','Portico')
selected=[]
for o in objs:
    if any(t.lower() in o.name.lower() for t in terms):
        qs=[o.matrix_world@Vector(c) for c in o.bound_box] if o.type in {'MESH','CURVE','FONT'} else []
        if qs:
            selected.append({'name':o.name,'type':o.type,'loc':list(o.location),'world':list(o.matrix_world.translation),'bbox':[[min(v[i] for v in qs),max(v[i] for v in qs)] for i in range(3)]})
report={'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'scene':bpy.context.scene.name,'collection':coll.name if coll else None,'objects':len(objs),'mesh_count':len(mesh),'materialless_meshes':matless,'missing_external_images':missing,'root':[{'name':o.name,'loc':list(o.location),'world':list(o.matrix_world.translation)} for o in objs if o.name=='AssetRoot_stewart_center'],'bounds_world':bounds,'type_counts':dict(collections.Counter(o.type for o in objs)),'outside_gis_centroid_count':len(outs),'largest_outside_gis_centroids':outs[:35],'selected_objects':selected}
out=root/'independent_reopen_r1.json'; out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); print(json.dumps({k:report[k] for k in ['sha256','scene','collection','objects','mesh_count','materialless_meshes','missing_external_images','root','bounds_world','type_counts','outside_gis_centroid_count','largest_outside_gis_centroids']},indent=2))
