"""Fresh independent reopen details for the R5 review."""
import bpy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/walc.blend'
EXPECTED='71dd7f551168b9940db616c2bdde548f4df0835a8bf496037e8100e3f0f6cd5e'
digest=hashlib.sha256(ASSET.read_bytes()).hexdigest()
coll=bpy.data.collections.get('Asset_walc')
root=bpy.data.objects.get('AssetRoot_walc')
missing_images=[]; image_nodes=[]
for im in bpy.data.images:
    if im.source!='FILE' or not im.filepath: continue
    resolved=Path(bpy.path.abspath(im.filepath,library=im.library))
    image_nodes.append({'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file),'exists':resolved.exists() if not im.packed_file else True})
    if not im.packed_file and not resolved.exists(): missing_images.append(str(resolved))
libraries=[]
for lib in bpy.data.libraries:
    if 'engineering_foliage_library.blend' not in lib.filepath: continue
    path=Path(bpy.path.abspath(lib.filepath))
    libraries.append({'name':lib.name,'filepath':lib.filepath,'resolved_path':str(path),'exists':path.exists()})
def mesh_bounds(obj):
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]] if pts else None
trace=bpy.data.objects.get('WALC_Official_906_Roof')
roof_names=('WALC_R5_Roof_West_Hip','WALC_R5_Roof_East_Hip','WALC_R5_Roof_South_Transition','WALC_R5_Roof_North_Transition')
roofs=[]
for n in roof_names:
    o=bpy.data.objects.get(n)
    if o: roofs.append({'object':n,'bounds_local_m':mesh_bounds(o),'material_slots':[m.name if m else None for m in o.data.materials]})
root_state={'location':list(root.location),'rotation':list(root.rotation_euler),'scale':list(root.scale),'matrix_world':[list(row) for row in root.matrix_world]} if root else None
result={
 'asset':str(ASSET),'sha256':digest,'hash_matches_requested':digest==EXPECTED,
 'blender_version':bpy.app.version_string,'scene':'Building_walc' if bpy.data.scenes.get('Building_walc') else None,
 'export_collection':'Asset_walc' if coll else None,'collection_object_count':len(coll.all_objects) if coll else None,
 'mesh_count':sum(o.type=='MESH' for o in coll.all_objects) if coll else None,
 'materialless_meshes':[o.name for o in coll.all_objects if o.type=='MESH' and not o.data.materials] if coll else None,
 'invalid_material_slot_meshes':[o.name for o in coll.all_objects if o.type=='MESH' and any(m is None for m in o.data.materials)] if coll else None,
 'root_transform':root_state,
 'gis_roof_trace':{'object':'WALC_Official_906_Roof','vertices':len(trace.data.vertices),'bounds_local_m':mesh_bounds(trace),'hidden_render':trace.hide_render,'hidden_viewport':trace.hide_get()} if trace else None,
 'r5_roof_masses':roofs,
 'entry_pavilion_bounds':mesh_bounds(bpy.data.objects['WALC_R5_Central_Glazed_Pavilion']) if bpy.data.objects.get('WALC_R5_Central_Glazed_Pavilion') else None,
 'linked_libraries':libraries,'missing_external_images':missing_images,'image_datablocks':image_nodes,
 'limitations':['Standalone check does not verify master Placement_walc or adjacent campus alignment.','Roof shape and dimensions remain image-estimated; GIS roof trace is not roof-form evidence.','Interior remains schematic.']
}
out=ROOT/'audit/walc_refine/independent_grade_r5_reopen.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
