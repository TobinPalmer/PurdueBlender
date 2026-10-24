import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GIS_RAW = ROOT / 'audit/batch2_krannert/krannert_gis_fid54_4326.json'
GIS_PROJECTED = ROOT / 'modular/buildings/target_buildings_gis.json'
MANIFEST = ROOT / 'modular/manifest.json'
STRUCT = ROOT / 'audit/batch2_krannert/structural_bounds_round3.json'
OUT = ROOT / 'audit/batch2_krannert/krannert_geometry_review_r3.json'

raw = json.loads(GIS_RAW.read_text(encoding='utf-8'))
proj = json.loads(GIS_PROJECTED.read_text(encoding='utf-8'))['KRAN']
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
asset = next(x for x in manifest['assets'] if x['id'] == 'krannert_building')
struct = json.loads(STRUCT.read_text(encoding='utf-8'))
feature = raw['features'][0]
attrs = feature['attributes']
ring = feature['geometry']['rings'][0]
origin = asset['placement_origin_xy_m']

# Use only the project's documented approximate WGS84 -> local campus formula.
lat0, lon0 = 40.4274, -86.9137
def project(lon, lat):
    x = (lon - lon0) * 111412.84 * math.cos(math.radians(lat0))
    y = (lat - lat0) * 111040.0
    return [x, y]

raw_xy = [project(p[0], p[1]) for p in ring]
raw_local = [[p[0] - origin[0], p[1] - origin[1]] for p in raw_xy]
target_ring_world = proj['world_polygon']
target_local = [[p[0] - origin[0], p[1] - origin[1]] for p in target_ring_world]

def bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)]
def area(points):
    pts = points[:-1] if points and points[0] == points[-1] else points
    return abs(sum(pts[i][0] * pts[(i+1)%len(pts)][1] - pts[(i+1)%len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2)
def perimeter(points):
    pts = points[:-1] if points and points[0] == points[-1] else points
    return sum(math.hypot(pts[(i+1)%len(pts)][0]-pts[i][0], pts[(i+1)%len(pts)][1]-pts[i][1]) for i in range(len(pts)))
def nearest_errors(a, b):
    return [min(math.hypot(p[0]-q[0], p[1]-q[1]) for q in b) for p in a]

gis_b = bounds(raw_local)
wall_b = [struct['KRAN_Exterior_Masonry_Walls']['bounds'][0], struct['KRAN_Exterior_Masonry_Walls']['bounds'][1]]
wire_b = [struct['KRAN_Footprint_Reference_Wire']['bounds'][0], struct['KRAN_Footprint_Reference_Wire']['bounds'][1]]
wire_world = struct['KRAN_Footprint_Reference_Wire']['vertices_xy']
wire_local = [[p[0] - origin[0], p[1] - origin[1]] for p in wire_world]
errors = nearest_errors(raw_local[:-1], target_local[:-1])
wire_errors = nearest_errors(raw_local[:-1], wire_local)

floor_names = ['KRAN_FloorSlab_Ground_L0'] + [f'KRAN_FloorSlab_Floor_L{i}' for i in range(1,8)] + ['KRAN_FloorSlab_Roof_Deck']
model_levels = {}
for name in floor_names:
    obj = struct.get(name)
    if obj:
        model_levels[name] = obj['bounds'][2]

result = {
    'building_id': 'krannert_building',
    'review_date': '2026-10-24',
    'source': {
        'provider': 'Purdue University campus GIS, ArcGIS BuildingShapesZip4 FeatureServer layer 0',
        'feature_id_fid': attrs.get('FID'),
        'feature_name': attrs.get('BUILDING_N'),
        'feature_global_id': attrs.get('GlobalID'),
        'feature_query_url': 'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D54&outFields=*&returnGeometry=true&outSR=4326&f=pjson',
        'raw_snapshot': 'audit/batch2_krannert/krannert_gis_fid54_4326.json',
        'layer_metadata_snapshot': 'audit/batch2_krannert/krannert_gis_layer_metadata.json',
        'gis_layer_native_crs': 'EPSG:3857 (Web Mercator) from FeatureServer layer metadata; query geometry exported as EPSG:4326',
        'source_crs': 'EPSG:4326 (WGS84) in raw feature response',
        'comparison_projection': 'Project approximate campus-local formula: X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040; then subtract manifest placement origin. Not a surveyed CRS.',
        'service_shape_area_web_mercator_units_m2': attrs.get('Shape__Area'),
        'service_shape_length_web_mercator_units_m': attrs.get('Shape__Length'),
        'service_shape_units_note': 'Layer-native spatial reference is EPSG:3857; scale distortion means these shape metrics exceed local ground estimates near latitude 40.4 N.',
        'floor_and_height_fields': {k: attrs.get(k) for k in ['NUM_LEVELS','CountOfFLO','G','F01','F02','F03','F04','F05','F06','F07','R','Extrution','Elevation']},
        'field_semantics_limit': 'The feature layer schema provides field names but no descriptions/units; project manifest previously interprets Extrution and R as feet. Treat floor/roof values as reported GIS attributes, not surveyed vertical datums.'
    },
    'placement': {
        'manifest_origin_xy_m': origin,
        'coordinator_readonly_master_marker': {'location_m':[234.5345001,-412.7189941,0.0], 'rotation_deg':[0,0,0], 'scale':[1,1,1], 'reported_by_coordinator':'2026-10-24', 'difference_from_manifest_xy_m':[0.000000022,0.0000154]},
        'source_asset_root_transform': 'identity (validated previously in source round2)',
        'note': 'The marker check is coordinator-side; this agent did not edit the master.'
    },
    'footprint_screening': {
        'raw_feature_ring_vertex_count_including_closure': len(ring),
        'projected_feature_bounds_local_m': gis_b,
        'projected_feature_area_local_m2_approx': area(raw_local),
        'projected_feature_perimeter_local_m_approx': perimeter(raw_local),
        'target_buildings_gis_bounds_world_m': proj['world_polygon'] and [[min(p[i] for p in target_ring_world),max(p[i] for p in target_ring_world)] for i in range(2)],
        'source_footprint_wire_bounds_local_m': wire_b,
        'structural_exterior_wall_bounds_local_m': wall_b,
        'wall_bounds_excess_each_side_m_approx': [
            (gis_b[0][0]-wall_b[0][0]), (wall_b[0][1]-gis_b[0][1]),
            (gis_b[1][0]-wall_b[1][0]), (wall_b[1][1]-gis_b[1][1])
        ],
        'raw_wgs84_to_projected_json_nearest_vertex_error_m': {'mean':sum(errors)/len(errors),'max':max(errors)},
        'raw_wgs84_to_asset_wire_nearest_vertex_error_m': {'mean':sum(wire_errors)/len(wire_errors),'max':max(wire_errors)},
        'interpretation': 'The source footprint wire is derived from this GIS feature, so wire/GIS overlap is a construction alignment check, not independent validation. Structural wall bounds extend about 0.2 m per side, consistent with wall thickness; AABB is not a polygon-shape score.'
    },
    'vertical_screening': {
        'source_model_level_bounds_z_m': model_levels,
        'model_parapet_bounds_z_m': struct['KRAN_Limestone_Parapet_Coping']['bounds'][2],
        'model_penthouse_bounds_z_m': struct['KRAN_Rooftop_Mechanical_Penthouse']['bounds'][2],
        'GIS_extrusion_field_value': attrs.get('Extrution'),
        'GIS_roof_field_R_value': attrs.get('R'),
        'generator_constants_from_build_krannert_building_py': {
            'main_parapet_top_m': 32.918,
            'mechanical_penthouse_roof_m': 35.662,
            'elevator_overrun_top_m': 36.8,
            'overrun_trim_top_m': 37.05
        },
        'interpretation': 'The source generator maps GIS Extrution=108 to the 32.918 m parapet and R=117 to the 35.662 m main penthouse roof. The separate 36.8 m elevator overrun and 37.05 m trim are generator estimates without a direct elevation source. Floor-field names are not described in the service schema; no roof geometry was changed.'
    },
    'site_grade': {
        'former_asset_plaza_object': 'KRAN_Surrounding_Plaza_Paving',
        'former_asset_plaza_bounds_local_m': struct['KRAN_Surrounding_Plaza_Paving']['bounds'],
        'current_asset_plaza_present': False,
        'action': 'Removed in round 3 from the saved asset and removed from the dedicated builder script. It was a 88 x 61.53 m flat rectangle that extended about 6 m beyond the building footprint; the GIS footprint does not support its extent or grade.',
        'status': 'The current source asset has no site grade, roadway, sidewalk or planting model. The master campus terrain/roads must supply site context. A neutral z=0 plane appears only in the exterior audit renders and is not saved in the asset.'
    }
}
OUT.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(OUT)
