import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
path=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=path)
asset=bpy.data.collections.get('Asset_knoy_hall')
coll=bpy.data.collections.get('KNOY_TypicalPlan_StairRuns_L2-L4')
def bounds(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [[round(min(v[i] for v in p),3),round(max(v[i] for v in p),3)] for i in range(3)]
def bvh(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
    v=[o.matrix_world@x.co for x in m.vertices]
    t=BVHTree.FromPolygons(v,[f.vertices[:] for f in m.polygons],all_triangles=False)
    ev.to_mesh_clear();return t
stairs=list(coll.objects) if coll else []
walls=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('KNOY_Ground_TracePartition_') or '_TypicalPlan_InteriorPartitions' in o.name)]
wall_bvhs={o.name:bvh(o) for o in walls}
results=[]
for s in stairs:
    hits=[];tree=bvh(s)
    for n,t in wall_bvhs.items():
        pairs=tree.overlap(t)
        if pairs:hits.append({'wall':n,'face_pairs':len(pairs)})
    results.append({'name':s.name,'bounds':bounds(s),'vertices':len(s.data.vertices),'faces':len(s.data.polygons),'material_count':len(s.data.materials),'collisions':hits})
report={'saved_asset':path,'asset_collection_present':asset is not None,'stair_collection_present':coll is not None,'stair_count':len(stairs),'stair_assemblies':results,'reopen_validation_pass':bool(asset and coll and len(stairs)==6 and all(not x['collisions'] and x['material_count'] for x in results))}
with open(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\stair_reopen_validation.json','w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
