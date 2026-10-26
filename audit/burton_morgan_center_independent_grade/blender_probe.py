import bpy, json, math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset_path=root/'modular/buildings/burton_morgan_center.blend'
gis_path=root/'audit/burton_morgan_center/sources/gis_feature_80_query_2026-10-25.json'
manifest=json.loads((root/'modular/manifest.json').read_text(encoding='utf-8'))
contract=next(a for a in manifest['assets'] if a['id']=='burton_morgan_center')
gis=json.loads(gis_path.read_text(encoding='utf-8'))['features'][0]
ring=gis['geometry']['rings'][0]
lon0,lat0=-86.9137,40.4274
ox,oy=contract['placement_origin_xy_m']
expected=[((lon-lon0)*111412.84*math.cos(math.radians(lat0))-ox,(lat-lat0)*111040.0-oy) for lon,lat in ring]
if len(expected)>1 and math.dist(expected[0],expected[-1])<.001: expected.pop()
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
col=bpy.data.collections.get('Asset_burton_morgan_center')
assert col is not None
objs=list(col.all_objects)
meshes=[o for o in objs if o.type=='MESH']
world=[]
for o in meshes:
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
    world.extend([ev.matrix_world @ v.co for v in me.vertices]); ev.to_mesh_clear()
assert world
mins=[min(v[i] for v in world) for i in range(3)]; maxs=[max(v[i] for v in world) for i in range(3)]
name=contract['objects'][0]
shell=next((o for o in objs if o.get('manifest_object_name')==name or o.name==name),None)
assert shell and shell.type=='MESH', f'Missing shell: {name}'
shell_xy=[(v.co.x,v.co.y) for v in shell.data.vertices]
def nearest(p, points): return min(math.dist(p,q) for q in points)
ring_to_shell=[nearest(p,shell_xy) for p in expected]
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file: external.append(im.filepath)
report={'building_id':'burton_morgan_center','asset_path':'modular/buildings/burton_morgan_center.blend','stable_collection':col.name,'manifest_collection':contract['collection'],'object_count':len(objs),'mesh_count':len(meshes),'manifest_object_count':contract['object_count'],'manifest_names_match':set(o.get('manifest_object_name',o.name) for o in objs)==set(contract['objects']),'source_feature_id':gis['attributes'].get('FID'),'source_name':gis['attributes'].get('BUILDING_N'),'source_ring_vertex_count_including_close':len(ring),'source_ring_vertex_count_used':len(expected),'shell_vertex_count':len(shell_xy),'shell_bounds_local_m':{'min':[min(p[i] for p in shell_xy) for i in range(2)],'max':[max(p[i] for p in shell_xy) for i in range(2)]},'gis_ring_to_shell_vertex_nearest_m':{'max':max(ring_to_shell),'mean':sum(ring_to_shell)/len(ring_to_shell)},'asset_bounds_local_m':{'min':mins,'max':maxs,'dimensions':[maxs[i]-mins[i] for i in range(3)]},'gis_origin_xy_m':[-775.751,-404.568],'manifest_origin_xy_m':contract['placement_origin_xy_m'],'unpacked_external_images':external,'asset_opened':True}
(root/'audit/burton_morgan_center_independent_grade/blender_probe.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))


