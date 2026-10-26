"""Fresh-process structural, dependency and hash check for the R5 WALC asset."""
import bpy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/walc.blend'
asset=bpy.data.collections.get('Asset_walc')
root=bpy.data.objects.get('AssetRoot_walc')
foliage=[lib.filepath for lib in bpy.data.libraries if 'engineering_foliage_library.blend' in lib.filepath]
missing=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        p=Path(bpy.path.abspath(im.filepath,library=im.library))
        if not p.exists(): missing.append(str(p))
trace=bpy.data.objects.get('WALC_Official_906_Roof')
trace_bounds=None
if trace:
    pts=[trace.matrix_world@v.co for v in trace.data.vertices]
    trace_bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
root_state={'location':list(root.location),'rotation':list(root.rotation_euler),'scale':list(root.scale)} if root else None
expected='71dd7f551168b9940db616c2bdde548f4df0835a8bf496037e8100e3f0f6cd5e'
result={
    'asset_path':str(ASSET),
    'sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    'hash_matches_expected':hashlib.sha256(ASSET.read_bytes()).hexdigest()==expected,
    'blender_version':bpy.app.version_string,
    'collection_exists':bool(asset),
    'object_count':len(asset.all_objects) if asset else None,
    'mesh_count':sum(o.type=='MESH' for o in asset.all_objects) if asset else None,
    'root_transform':root_state,
    'roof_trace':{'vertices':len(trace.data.vertices),'bounds':trace_bounds,'hidden_render':trace.hide_render,'hidden_viewport':trace.hide_get()} if trace else None,
    'r5_objects':[n for n in ('WALC_R5_Roof_West_Hip','WALC_R5_Roof_East_Hip','WALC_R5_Roof_South_Transition','WALC_R5_Roof_North_Transition','WALC_R5_Central_Glazed_Pavilion','WALC_R5_Central_Roof_Monitor') if bpy.data.objects.get(n)],
    'foliage_libraries':foliage,
    'relative_foliage_resolves':all(Path(bpy.path.abspath(p)).exists() for p in foliage),
    'missing_external_images':missing,
    'material_slotless_meshes':[o.name for o in asset.all_objects if o.type=='MESH' and len(o.data.materials)==0] if asset else None,
}
out=ROOT/'audit/walc_refine/independent_reopen_r5.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
