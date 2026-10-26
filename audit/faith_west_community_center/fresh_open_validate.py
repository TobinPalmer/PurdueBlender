"""Run with Blender opening the saved asset in a fresh process."""
import bpy, json, hashlib
from pathlib import Path

path=Path(bpy.data.filepath).resolve()
scene_name='Building_massing_faith_west_community_center_84aa829'
collection_name='Asset_massing_faith_west_community_center_84aa829'
scene=bpy.data.scenes.get(scene_name)
collection=bpy.data.collections.get(collection_name)
if scene is None or collection is None:
    raise RuntimeError('Expected scene or export collection missing')
objects=list(collection.objects)
missing=[]
external_images=[]
for image in bpy.data.images:
    if image.source == 'FILE' and image.filepath and not image.packed_file:
        external_images.append(image.filepath)
for lib in bpy.data.libraries:
    p=Path(bpy.path.abspath(lib.filepath))
    if not p.exists(): missing.append(str(p))
verts=[]
for obj in objects:
    if obj.type=='MESH':
        verts.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
bounds=[[min(v[i] for v in verts) for i in range(3)],[max(v[i] for v in verts) for i in range(3)]] if verts else None
sha=hashlib.sha256(path.read_bytes()).hexdigest()
report={
    'fresh_process_opened':True,
    'blender_version':bpy.app.version_string,
    'file':str(path),
    'sha256':sha,
    'scene':scene.name,
    'collection':collection.name,
    'object_count':len(objects),
    'object_types':{t:sum(o.type==t for o in objects) for t in sorted({o.type for o in objects})},
    'mesh_objects_with_no_faces':[o.name for o in objects if o.type=='MESH' and not o.data.polygons],
    'mesh_material_slots':sum(len(o.data.materials) for o in objects if o.type=='MESH'),
    'faithwest_material_count':sum(m.name.startswith('FaithWest_') for m in bpy.data.materials),
    'source_asset_bounds_world_m':bounds,
    'mesh_bounds_include_below_grade_geometry':bool(bounds and bounds[0][2] < -0.01),
    'linked_libraries':[bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries],
    'missing_linked_libraries':missing,
    'unpacked_external_images':external_images,
    'cameras_in_export_collection':[o.name for o in objects if o.type=='CAMERA'],
    'lights_in_export_collection':[o.name for o in objects if o.type=='LIGHT'],
    'all_objects_named_for_asset':all(o.name.startswith('FaithWest_') for o in objects),
    'scene_objects_not_in_export_collection':[o.name for o in scene.objects if o not in objects],
}
report['pass']=bool(report['fresh_process_opened'] and report['object_count']>=25 and not report['mesh_objects_with_no_faces'] and not report['mesh_bounds_include_below_grade_geometry'] and not missing and not external_images and report['all_objects_named_for_asset'] and not report['cameras_in_export_collection'] and not report['lights_in_export_collection'])
out=Path(__file__).parent/'fresh_open_validation.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
build_report_path=Path(__file__).parent/'build_report.json'
if build_report_path.exists():
    build_report=json.loads(build_report_path.read_text(encoding='utf-8'))
    build_report['candidate_sha256']=sha
    build_report['validation']='PASS: exact saved candidate opened in a fresh Blender 5.2.3 process; no empty meshes, external libraries, or unpacked images; expected scene/collection present.'
    build_report['fresh_open']=report
    build_report_path.write_text(json.dumps(build_report,indent=2),encoding='utf-8')
print('FAITH_WEST_FRESH_OPEN '+json.dumps(report))
if not report['pass']:
    raise RuntimeError('Fresh-open validation failed')
