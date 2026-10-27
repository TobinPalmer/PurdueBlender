import bpy, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular'/'buildings'/'massing_hull_all_american_marching_band_complex_665bcb7.blend'
out=root/'audit'/'hull_all_american_marching_band_complex'/'fresh_open_validation.json'
expected_collection='Asset_massing_hull_all_american_marching_band_complex_665bcb7'
expected_scene='Building_massing_hull_all_american_marching_band_complex_665bcb7'
bpy.ops.wm.open_mainfile(filepath=str(asset))
collection=bpy.data.collections.get(expected_collection)
scene=bpy.data.scenes.get(expected_scene)
if collection is None or scene is None:
    raise RuntimeError('Expected asset collection or scene missing after fresh open')
objects=list(collection.objects)
meshes=[o for o in objects if o.type=='MESH']
missing_materials=[o.name for o in meshes if not o.data.materials]
lo=[float('inf')]*3; hi=[float('-inf')]*3
for obj in objects:
    if obj.type!='MESH': continue
    deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); me=ev.to_mesh()
    for v in me.vertices:
        p=obj.matrix_world @ v.co
        for i in range(3): lo[i]=min(lo[i],p[i]); hi[i]=max(hi[i],p[i])
    ev.to_mesh_clear()
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
result={'asset_path':str(asset.relative_to(root)),'fresh_process_reopen':'PASS','blender_version':bpy.app.version_string,'scene':scene.name,'collection':collection.name,'collection_object_count':len(objects),'mesh_count':len(meshes),'non_mesh_types':sorted(set(o.type for o in objects if o.type!='MESH')),'materialless_meshes':missing_materials,'external_unpacked_images':external,'evaluated_world_bounds_m':{'min':[round(v,4) for v in lo],'max':[round(v,4) for v in hi]},'all_objects_in_designated_collection':all(collection in o.users_collection for o in objects),'camera_objects_in_asset_collection':[o.name for o in objects if o.type=='CAMERA'],'checks':'PASS' if not missing_materials and not external and len(meshes)>0 else 'FAIL'}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
if result['checks']!='PASS': raise RuntimeError('One or more portability/material checks failed')
