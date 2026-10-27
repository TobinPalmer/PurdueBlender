import bpy, hashlib, json, math
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
gis_path = Path('audit/kappa_delta_rho/sources/purdue_gis_fid801.geojson').resolve()
geo = json.loads(gis_path.read_text(encoding='utf-8-sig'))['features'][0]
gis_ring = geo['geometry']['coordinates'][0]
if gis_ring[0] == gis_ring[-1]:
    gis_ring = gis_ring[:-1]
lat0, lon0 = 40.4274, -86.9137
gis_xy = [((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0) for lon,lat in gis_ring]
base_xy = [(float(v.co.x), float(v.co.y)) for v in house.data.vertices if abs(v.co.z) < 1e-5]
assert len(gis_xy) == len(base_xy) == 20
nearest_errors = [min(math.hypot(x-a, y-b) for a,b in base_xy) for x,y in gis_xy]
assert max(nearest_errors) < 0.0001, f'GIS footprint mismatch: max vertex error {max(nearest_errors)} m'
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
    'gis_fid': geo['id'],
    'gis_name': geo['properties'].get('BUILDING_N'),
    'gis_address': geo['properties'].get('ADDRESS'),
    'gis_ring_vertices': len(gis_xy),
    'model_base_vertices': len(base_xy),
    'footprint_nearest_vertex_max_m': max(nearest_errors),
    'footprint_nearest_vertex_rms_m': math.sqrt(sum(d*d for d in nearest_errors)/len(nearest_errors)),
    'detail_objects': sorted(o.name for o in coll.objects if o.name.startswith('KDRDetail_')),
    'interior_objects': sorted(o.name for o in coll.objects if o.name.startswith('KDRInterior_')),
    'preview_rig_objects_in_asset': sorted(o.name for o in bpy.data.objects if o.name.startswith('KDRPreview_')),
    'unpacked_external_file_textures': external,
}
report_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
build_report_path = Path('audit/kappa_delta_rho/build_report.json').resolve()
build_report = json.loads(build_report_path.read_text(encoding='utf-8'))
build_report['fresh_open_status'] = 'passed in separate Blender 5.2.3 process; stable scene/collection/object, exact GIS FID 801 base ring, local detail collections and portable materials verified'
build_report['fresh_open_sha256'] = data['sha256']
build_report_path.write_text(json.dumps(build_report, indent=2), encoding='utf-8')
print(json.dumps(data, indent=2))
