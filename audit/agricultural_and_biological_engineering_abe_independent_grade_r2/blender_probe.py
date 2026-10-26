"""Independent read-only Blender measurements for the repaired ABE asset."""
from pathlib import Path
import json, math
import bpy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/agricultural_and_biological_engineering_abe.blend'
GIS=ROOT/'audit/abe/evidence/purdue_abe_gis_feature_406.json'
MANIFEST=ROOT/'modular/manifest.json'
OUT=HERE/'blender_probe.json'
ID='agricultural_and_biological_engineering_abe'
COL='Asset_'+ID
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
root=bpy.data.collections.get(COL)
assert root is not None
assert bpy.context.scene.name=='Scene'
assert root.get('building_id')==ID and root.get('source_feature_id')==406
objs=list(root.all_objects)
shell=next(o for o in objs if o.type=='MESH' and o.get('source_geometry')=='Purdue GIS feature 406 outer ring')
manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
e=next(x for x in manifest['assets'] if x['id']==ID)
gis=json.loads(GIS.read_text(encoding='utf-8'))
ring=max(gis['feature']['geometry']['rings'],key=len)
sx=111412.84*math.cos(math.radians(40.4274)); sy=111040.0
world=[((lon+86.9137)*sx,(lat-40.4274)*sy) for lon,lat in ring[:-1]]
origin=e['placement_origin_xy_m']
local=[(x-origin[0],y-origin[1]) for x,y in world]
dg=bpy.context.evaluated_depsgraph_get(); eval_shell=shell.evaluated_get(dg); mesh=eval_shell.to_mesh()
actual=[(shell.matrix_world @ v.co).to_tuple() for v in mesh.vertices]; eval_shell.to_mesh_clear()
def bounds(ps): return [[min(p[i] for p in ps),max(p[i] for p in ps)] for i in range(len(ps[0]))]
def area_centroid(ps):
    a2=cx=cy=0.0
    for a,b in zip(ps,ps[1:]+ps[:1]):
        cross=a[0]*b[1]-b[0]*a[1]; a2+=cross; cx+=(a[0]+b[0])*cross; cy+=(a[1]+b[1])*cross
    return [cx/(3*a2),cy/(3*a2)]
def seg_dist(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; q=dx*dx+dy*dy
    t=0 if q==0 else min(1,max(0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/q))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def directed(points,poly): return max(min(seg_dist(p,a,b) for a,b in zip(poly,poly[1:]+poly[:1])) for p in points)
actual2=[p[:2] for p in actual]
source_cent=area_centroid(world); local_cent=area_centroid(local); actual_cent=area_centroid(actual2)
imgs=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
libs=[x.filepath for x in bpy.data.libraries if x.filepath]
result={
 'asset':str(ASSET.relative_to(ROOT)),'scene':bpy.context.scene.name,'collection':root.name,
 'building_id':root.get('building_id'),'source_feature_id':root.get('source_feature_id'),
 'collection_object_count':len(objs),'mesh_object_count':sum(o.type=='MESH' for o in objs),
 'shell_name':shell.name,'shell_bounds_local_m':bounds(actual),
 'source_bounds_project_m':bounds(world),'source_bounds_local_m':bounds(local),
 'source_ring_vertices':len(world),'shell_vertices':len(actual),
 'shell_to_source_hausdorff_m':directed(actual2,local),'source_to_shell_hausdorff_m':directed(local,actual2),
 'source_centroid_project_xy_m':source_cent,'source_centroid_local_xy_m':local_cent,
 'shell_centroid_local_xy_m':actual_cent,'shell_centroid_error_local_m':math.dist(actual_cent,local_cent),
 'shell_centroid_error_double_transform_m':math.dist([actual_cent[0]+origin[0],actual_cent[1]+origin[1]],source_cent),
 'placement_origin_xy_m':origin,'asset_local_frame_metadata':list(root.get('placement_origin_xy_m')) if root.get('placement_origin_xy_m') is not None else None,
 'manifest_collection_matches':e.get('collection')==COL,'manifest_object_count':e.get('object_count'),
 'manifest_objects_length':len(e.get('objects',[])),
 'collection_object_names':sorted(o.name for o in objs),
 'manifest_object_names_match':sorted(e.get('objects',[]))==sorted(o.name for o in objs),
 'unpacked_file_images':imgs,'linked_library_paths':libs,
 'collection_object_types':{t:sum(o.type==t for o in objs) for t in sorted({o.type for o in objs})},
 'all_collection_objects_in_scene':all(o.name in bpy.context.scene.objects for o in objs)
}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
