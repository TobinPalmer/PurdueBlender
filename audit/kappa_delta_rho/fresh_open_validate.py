import bpy, hashlib, json
from pathlib import Path

asset = Path('modular/buildings/massing_house_1089876362_14ecd2c.blend').resolve()
report_path = Path('audit/kappa_delta_rho/fresh_open_report.json').resolve()
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.context.scene
coll = bpy.data.collections.get('Asset_massing_house_1089876362_14ecd2c')
house = bpy.data.objects.get('House_1089876362')
assert scene.name == 'Building_massing_house_1089876362_14ecd2c'
assert coll is not None and house is not None and house.name in coll.objects
assert house.type == 'MESH' and len(house.data.vertices) == 40 and len(house.data.polygons) == 22
assert house.data.uv_layers.get('KDR_Wall_UV_Metric') is not None
assert len(house.data.materials) == 2
assert not any(o.name.startswith('KDRPreview_') for o in bpy.data.objects)
assert len([o for o in coll.objects if o.name.startswith('KDRDetail_')]) >= 5
assert len([o for o in coll.objects if o.name.startswith('KDRInterior_')]) >= 3
external = [im.filepath for im in bpy.data.images if im.source == 'FILE' and not im.packed_file]
data = {
    'fresh_open': True,
    'asset': str(asset),
    'sha256': hashlib.sha256(asset.read_bytes()).hexdigest(),
    'scene': scene.name,
    'asset_collection': coll.name,
    'stable_house_object': house.name,
    'house_mesh_vertices': len(house.data.vertices),
    'house_mesh_faces': len(house.data.polygons),
    'house_uv_layers': [u.name for u in house.data.uv_layers],
    'house_materials': [m.name for m in house.data.materials],
    'detail_objects': sorted(o.name for o in coll.objects if o.name.startswith('KDRDetail_')),
    'interior_objects': sorted(o.name for o in coll.objects if o.name.startswith('KDRInterior_')),
    'preview_rig_objects_in_asset': sorted(o.name for o in bpy.data.objects if o.name.startswith('KDRPreview_')),
    'unpacked_external_file_textures': external,
}
report_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
print(json.dumps(data, indent=2))
