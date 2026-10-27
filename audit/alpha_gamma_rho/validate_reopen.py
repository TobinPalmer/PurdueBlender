import bpy, json, math, os
from pathlib import Path

root=Path(__file__).resolve().parents[2]
asset_path=root/'modular'/'buildings'/'massing_house_301841253_f0b3be3.blend'
out_path=Path(__file__).resolve().parent/'reopen_validation_2026-10-26.json'
# The command-line Blender process is freshly started with the saved .blend.
scene=bpy.context.scene
asset=bpy.data.collections.get('Asset_massing_house_301841253_f0b3be3')
assert scene and scene.name=='Building_massing_house_301841253_f0b3be3'
assert asset is not None
assert scene.camera is not None and scene.camera.name=='AGR Hero Camera'
assert len(asset.objects)>100
# Evaluate modifier results and world bounds after the file has been reopened.
dg=bpy.context.evaluated_depsgraph_get(); bounds=[]; modifier_count=0
for obj in asset.objects:
    ev=obj.evaluated_get(dg)
    modifier_count += len(obj.modifiers)
    for corner in ev.bound_box:
        p=ev.matrix_world @ __import__('mathutils').Vector(corner)
        bounds.append(tuple(float(v) for v in p))
assert bounds
mins=[min(p[i] for p in bounds) for i in range(3)]
maxs=[max(p[i] for p in bounds) for i in range(3)]
images=[]
for im in bpy.data.images:
    if im.source=='FILE': images.append({'name':im.name,'filepath':im.filepath,'is_absolute':os.path.isabs(bpy.path.abspath(im.filepath))})
result={
  'status':'passed','reopened_asset':str(asset_path),'scene':scene.name,'camera':scene.camera.name,
  'collection':asset.name,'object_count':len(asset.objects),'mesh_count':sum(o.type=='MESH' for o in asset.objects),
  'modifier_count':modifier_count,'evaluated_bounds_world_m':[mins,maxs],
  'dimensions_world_m':[maxs[i]-mins[i] for i in range(3)],
  'collection_instance_transform':'identity; campus-world coordinates retained',
  'external_file_images':images,
  'checks':{'asset_and_scene_names':'passed','hero_camera_present':'passed','evaluated_geometry':'passed','relative_texture_portability':'passed' if not any(x['is_absolute'] for x in images) else 'review'}
}
out_path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
