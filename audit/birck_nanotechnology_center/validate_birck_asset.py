"""Reopen and validate the Birck project and collection-only library export."""
import bpy, json, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT/'modular'/'buildings'/'birck_nanotechnology_center.blend'
EXPORT=ROOT/'audit'/'birck_nanotechnology_center'/'birck_asset_collection_export.blend'
REPORT=ROOT/'audit'/'birck_nanotechnology_center'/'validation.json'
RENDER=ROOT/'audit'/'birck_nanotechnology_center'/'reopened_validation.png'
COLLECTION='Asset_birck_nanotechnology_center'
def check_loaded(label):
    c=bpy.data.collections.get(COLLECTION)
    assert c is not None, f'{label}: required collection absent'
    objects=list(c.objects)
    assert len(objects)==110, f'{label}: expected 110 objects, found {len(objects)}'
    assert all(o.name in bpy.data.objects for o in objects)
    assert not any(o.type in {'CAMERA','LIGHT'} for o in objects)
    assert all(o.library is None for o in objects), f'{label}: linked external object found'
    assert all(not im.filepath or im.packed_file or im.source=='GENERATED' for im in bpy.data.images), 'unpacked external image dependency'
    coords=[]
    for o in objects:
        if o.type not in {'MESH','CURVE','FONT'}: continue
        coords.extend(o.matrix_basis @ Vector(corner) for corner in o.bound_box)
    bounds={'min':[min(v[i] for v in coords) for i in range(3)],'max':[max(v[i] for v in coords) for i in range(3)]}
    return {'collection':COLLECTION,'object_count':len(objects),'geometry_object_count':sum(o.type in {'MESH','CURVE','FONT'} for o in objects),'bounds_m':bounds,'external_image_dependencies':0}
bpy.ops.wm.open_mainfile(filepath=str(MAIN))
main=check_loaded('main')
scene=bpy.context.scene
scene.render.resolution_percentage=65
scene.render.filepath=str(RENDER)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(EXPORT))
export=check_loaded('collection export')
assert all(abs(main['bounds_m'][side][axis]-export['bounds_m'][side][axis])<0.01 for side in ('min','max') for axis in range(3))
assert main['object_count']==export['object_count']
report={'status':'PASS','blender_version':bpy.app.version_string,'main_project':str(MAIN.relative_to(ROOT)).replace('\\','/'),'collection_export':str(EXPORT.relative_to(ROOT)).replace('\\','/'),'main_project_validation':main,'collection_export_validation':export,'reopened_render':str(RENDER.relative_to(ROOT)).replace('\\','/')}
REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
