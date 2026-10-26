import bpy, json, math, sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
out=Path(sys.argv[sys.argv.index('--')+2]).resolve()
asset=root/'modular/buildings/massing_phi_delta_theta_258cddd.blend'
gis_path=root/'audit/massing_phi_delta_theta_258cddd/sources/purdue_gis_fid_796_current.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
data=json.loads(gis_path.read_text(encoding='utf-8-sig'))['features'][0]
ring=data['geometry']['rings'][0][:-1]
def xy(lon,lat):
    return ((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0)
src=[xy(p[0],p[1]) for p in ring]
scene=bpy.data.scenes.get('Building_massing_phi_delta_theta_258cddd')
coll=bpy.data.collections.get('Asset_massing_phi_delta_theta_258cddd')
objs=list(coll.objects) if coll else []
shell=bpy.data.objects.get('Phi Delta Theta')
base=[]
if shell and shell.type=='MESH':
    for v in shell.data.vertices:
        if abs(v.co.z)<1e-5: base.append((float(v.co.x),float(v.co.y)))
def nearest(a,b): return max(min(math.hypot(x-u,y-v) for u,v in b) for x,y in a) if a and b else None
# Check collection/object transformations and evaluated geometry bounds.
mesh_objs=[o for o in objs if o.type=='MESH']
all_world=[]
for o in mesh_objs:
    deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh()
    try:
        all_world.extend([ev.matrix_world @ v.co for v in me.vertices])
    finally: ev.to_mesh_clear()
bounds=None
if all_world:
    bounds=[[min(v[i] for v in all_world),max(v[i] for v in all_world)] for i in range(3)]
images=[i.filepath for i in bpy.data.images if i.source=='FILE']
external=[p for p in images if p and not p.startswith('//')]
result={
 'blender_version':bpy.app.version_string,'asset_path':str(asset.relative_to(root)).replace('\\','/'),
 'scene_present':scene is not None,'collection_present':coll is not None,
 'collection_object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),
 'curve_count':sum(o.type in {'CURVE','FONT'} for o in objs),
 'other_count':sum(o.type not in {'MESH','CURVE','FONT'} for o in objs),
 'shell_present':shell is not None,'shell_base_vertices':len(base),
 'source_vertices':len(src),'source_to_shell_hausdorff_xy_m':nearest(src,base),
 'shell_to_source_hausdorff_xy_m':nearest(base,src),
 'source_xy_bounds_m':[[min(x for x,y in src),max(x for x,y in src)],[min(y for x,y in src),max(y for x,y in src)]],
 'asset_evaluated_bounds_m':bounds,
 'scene_asset_direct_link_count':sum(1 for c in (scene.collection.children if scene else []) if c==coll),
 'external_image_paths':external,
 'temporary_render_objects':[o.name for o in objs if 'camera' in o.name.lower() or 'preview' in o.name.lower() or 'render' in o.name.lower()],
 'gis_identity':{k:data['attributes'].get(k) for k in ['FID','BLDG_ABBR','BUILDING_N','ADDRESS','OWNER','Extrution']}
}
out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
