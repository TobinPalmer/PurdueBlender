import bpy, json, math, hashlib, sys
from pathlib import Path

args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
asset = Path(args[0]).resolve()
out = Path(args[1]).resolve()
root = Path(args[2]).resolve()
manifest_path = root/'modular'/'manifest.json'
gis_path = root/'audit'/'benjamin_harrison_hall'/'sources'/'benjamin_harrison_hall_gis_feature_85_raw.json'
evidence_path = root/'audit'/'benjamin_harrison_hall'/'build_evidence.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.context.scene
entry = next(x for x in json.loads(manifest_path.read_text(encoding='utf-8'))['assets'] if x.get('id')=='benjamin_harrison_hall')
feature = next(f for f in json.loads(gis_path.read_text(encoding='utf-8'))['features'] if f.get('attributes',{}).get('FID')==85)
collection = bpy.data.collections.get('Asset_benjamin_harrison_hall')
if collection is None: raise RuntimeError('Export collection missing')
# Independently project the source polygon into the local frame documented by the repo.
coords = feature['geometry']['rings'][0][:-1]
lat0, lon0 = 40.4274, -86.9137
mx = 111412.84*math.cos(math.radians(lat0)); my = 111040.0
origin = tuple(entry['placement_origin_xy_m'])
gis_local = [((lon-lon0)*mx-origin[0],(lat-lat0)*my-origin[1]) for lon,lat,*_ in coords]
obj = collection.objects.get('HARR_Ground_Plinth_Base')
if not obj: raise RuntimeError('Structural GIS comparator missing')
dg=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(dg); mesh=ev.to_mesh()
try:
    pts=[ev.matrix_world@v.co for v in mesh.vertices]
finally: ev.to_mesh_clear()
basez=min(p.z for p in pts)
model_local=sorted(set((round(p.x,6),round(p.y,6)) for p in pts if abs(p.z-basez)<1e-4))
def directed(a,b): return max(min(math.dist(p,q) for q in b) for p in a)
haus=max(directed(model_local,gis_local),directed(gis_local,model_local))
# world placement reconstruction and structural dimensions
world_model=[(x+origin[0],y+origin[1]) for x,y in model_local]
world_gis=[(x+origin[0],y+origin[1]) for x,y in gis_local]
allpts=[]; mesh_objects=0; type_counts={}; mods=[]
for o in collection.objects:
    type_counts[o.type]=type_counts.get(o.type,0)+1
    if o.type=='MESH':
        mesh_objects+=1
        ee=o.evaluated_get(dg); mm=ee.to_mesh()
        try: allpts.extend([ee.matrix_world@v.co for v in mm.vertices])
        finally: ee.to_mesh_clear()
        if len(o.modifiers): mods.append({'object':o.name,'modifiers':[m.type for m in o.modifiers]})
mins=[min(p[i] for p in allpts) for i in range(3)]; maxs=[max(p[i] for p in allpts) for i in range(3)]
preview=bpy.data.collections.get('PreviewOnly_benjamin_harrison_hall')
scene_objects={o.name:o.type for o in scene.objects}
external_images=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
linked_libs=[lib.filepath for lib in bpy.data.libraries if lib.filepath]
# Fresh collection-only library export and reopen/link it in a blank file.
probe=out.with_name(out.stem+'_collection_export.blend')
bpy.data.libraries.write(str(probe), {collection}, path_remap='RELATIVE')
export_check={'path':str(probe),'exists':probe.is_file(),'bytes':probe.stat().st_size if probe.exists() else None}
# collect concise evidence from export source directly
export_check.update({'source_count':len(collection.objects),'types':type_counts,'camera_or_light':any(o.type in {'CAMERA','LIGHT'} for o in collection.objects),'external_unpacked_images':external_images,'linked_libraries':linked_libs})
# Check manifest exact names versus the actual export.
actual_names=set(o.name for o in collection.objects); listed=set(entry.get('objects',[]))
result={
 'asset_path':str(asset),'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,
 'scene':scene.name,'scene_metadata':{k:scene.get(k) for k in ('building_id','source_feature_id','source_provider','builder_script','height_status','roof_status','export_collection')},
 'manifest':{'id':entry.get('id'),'file':entry.get('file'),'collection':entry.get('collection'),'scene':entry.get('scene'),'origin_xy_m':origin,'object_count':entry.get('object_count'),'object_names_count':len(listed),'actual_object_count':len(actual_names),'names_exact':listed==actual_names,'listed_only_count':len(listed-actual_names),'actual_only_count':len(actual_names-listed),'listed_preview_objects':sorted(n for n in listed-actual_names if n.startswith(('Cam_','Sun_')))},
 'footprint':{'gis_feature_id':feature['attributes'].get('FID'),'gis_name':feature['attributes'].get('BUILDING_N'),'gis_address':feature['attributes'].get('ADDRESS'),'gis_distinct_vertices':len(gis_local),'model_base_distinct_vertices':len(model_local),'symmetric_nearest_vertex_error_m':haus,'model_base_z_local_m':basez,'projected_world_ring_bounds_m':[[min(p[i] for p in world_gis),max(p[i] for p in world_gis)] for i in (0,1)]},
 'evaluated_model_bounds_local_m':[[mins[i],maxs[i]] for i in (0,1,2)],'export_object_types':type_counts,'export_cameras_or_lights':[o.name for o in collection.objects if o.type in {'CAMERA','LIGHT'}],
 'preview_collection_names':sorted(o.name for o in preview.objects) if preview else None,'scene_camera_or_light_names':sorted(n for n,t in scene_objects.items() if t in {'CAMERA','LIGHT'}),
 'modifiers':mods,'unpacked_external_images':external_images,'linked_libraries':linked_libs,'collection_export_probe':export_check,
 'source_evidence_file_present':gis_path.is_file() and evidence_path.is_file(),'source_evidence_path':str(evidence_path)
}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('asset_path','asset_sha256','manifest','footprint','evaluated_model_bounds_local_m','export_object_types','export_cameras_or_lights','unpacked_external_images','linked_libraries','collection_export_probe')},indent=2),flush=True)
