import json, math
from pathlib import Path
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT.parents[1] / 'modular' / 'manifest.json'
GIS = ROOT / 'sources' / 'purdue_owen_gis_feature_38.json'
INSPECTION = ROOT / 'asset_inspection.json'


def evaluate(manifest_path=MANIFEST, gis_path=GIS, inspection_path=INSPECTION):
    manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    entry = next(a for a in manifest['assets'] if a['id'] == 'owen_hall')
    gis = json.loads(Path(gis_path).read_text(encoding='utf-8'))
    inspection = json.loads(Path(inspection_path).read_text(encoding='utf-8'))
    feature = next(f for f in gis['features'] if f['attributes']['OBJECTID'] == 38)
    ring = feature['geometry']['rings'][0]
    x_scale = 111412.84 * math.cos(math.radians(40.4274))
    y_scale = 111040.0
    px, py = entry['placement_origin_xy_m']
    gis_local = Polygon([((lon + 86.9137) * x_scale - px,
                          (lat - 40.4274) * y_scale - py) for lon, lat in ring])
    structural_shapes = []
    for item in inspection['structural_rectangles']:
        if 'Limestone_Base' not in item['name'] and '_GF_Wall_' not in item['name']:
            continue
        b = item['bounds']
        structural_shapes.append(box(b[0][0], b[1][0], b[0][1], b[1][1]))
    model_local = unary_union(structural_shapes)
    overlap = model_local.intersection(gis_local).area
    iou = overlap / model_local.union(gis_local).area
    gm = gis_local.bounds
    mm = model_local.bounds
    gis_center = ((gm[0]+gm[2])/2, (gm[1]+gm[3])/2)
    model_center = ((mm[0]+mm[2])/2, (mm[1]+mm[3])/2)
    envelope_center_error = math.dist(gis_center, model_center)
    gis_size = (gm[2]-gm[0], gm[3]-gm[1])
    model_size = (mm[2]-mm[0], mm[3]-mm[1])
    size_error_pct = tuple(abs(m-g)/g*100 for m,g in zip(model_size,gis_size))
    attrs = feature['attributes']
    id_ok = attrs.get('ABBR') == 'OWEN' and 'Owen' in attrs.get('Name', '')
    expected = (entry['file'] == 'buildings/owen_hall.blend' and
                entry['collection'] == inspection['collection_name'] and
                entry['object_count'] == inspection['collection_object_count'])
    portable = not inspection['image_or_library_references'] and inspection['modifier_object_count'] == 0

    criteria = [
      {"criterion":"Correct identity and source-backed footprint", "max_score":2, "score":1,
       "evidence":["Purdue GIS feature OBJECTID 38 identifies ABBR OWEN / Richard Owen Residence Hall at 1160 W. Stadium Avenue.", f"Projected GIS polygon and the model structural rectangles have IoU {iou:.3f} and model coverage of source polygon {overlap/gis_local.area:.3f}."],
       "finding":"Identity is verified. The coarse footprint-shape comparison is weak despite similar overall envelope dimensions; model and source shape cannot both earn full credit."},
      {"criterion":"Position, orientation, and scale/dimensions", "max_score":2, "score":2 if envelope_center_error <= 2 and max(size_error_pct) <= 5 else 1,
       "evidence":[f"GIS envelope center vs model structural envelope center error: {envelope_center_error:.2f} m.", f"GIS envelope: {gis_size[0]:.2f} m east-west by {gis_size[1]:.2f} m north-south; model: {model_size[0]:.2f} m by {model_size[1]:.2f} m.", f"Envelope dimension errors: {size_error_pct[0]:.1f}% and {size_error_pct[1]:.1f}%; both outlines are essentially axis-aligned in the project frame."],
       "finding":"Campus position, cardinal orientation, and overall plan envelope are verified within the project coordinate approximation. The footprint-shape discrepancy remains under criterion 1."},
      {"criterion":"Evidence-backed height, floors, and roof form", "max_score":2, "score":1,
       "evidence":[f"Reopened model evaluated bounds reach {inspection['evaluated_mesh_bounds_local'][2][1]:.2f} m; repeated floor bands are modeled at about 3.8 m intervals.", "Official Purdue exterior photo supports a flat roof edge / parapet profile, but no official measured height or clear floor-count specification was found."],
       "finding":"Roof silhouette is broadly supported. Model height and exact floor count remain estimates, so this criterion is uncertain and loses one point."},
      {"criterion":"Facade, entrances, and distinctive architecture", "max_score":2, "score":1,
       "evidence":["Official Purdue Housing exterior photograph shows a long red-brick residential facade, pale concrete / stone base and vertical window bays.", "Reopened model shows brick wall fields, pale horizontal trim, repeated windows, and entrance pavilions/portico; see owen_hall_facade.png."],
       "finding":"Broad materials and repetitive residential facade rhythm are represented. The modeled facade is simplified: source photo's tall glazed bays, concrete paneling, detailed window divisions, entry stairs and rails are absent or generalized."},
      {"criterion":"Modular export, portability, and complete evidence", "max_score":2, "score":2 if expected and portable else 1,
       "evidence":[f"Saved file reopens as scene {inspection['scene_names']} with collection {inspection['collection_name']} containing {inspection['collection_object_count']} objects.", "AssetRoot is at local origin; evaluated geometry bounds are recorded. No external image or library paths, modifiers, or missing mesh data were found.", "This folder contains source snapshots, provenance, an inspection script and JSON, the evaluator, a scorecard, and a rendered view."],
       "finding":"Export structure and portability passed inspection. The evidence package explicitly retains the remaining uncertainties."}
    ]
    score = sum(c['score'] for c in criteria)
    result = {
      "score":score, "max_score":10, "criteria":criteria,
      "evidence":{
        "feature_id":attrs['OBJECTID'], "official_building_name":attrs['Name'], "official_address":attrs['ADDRESS'],
        "gis_crs":"EPSG:4326; transformed with documented approximate project conversion",
        "gis_area_sq_m":round(gis_local.area,2), "model_structural_union_area_sq_m":round(model_local.area,2),
        "footprint_intersection_over_union":round(iou,4), "model_coverage_of_source_polygon":round(overlap/gis_local.area,4),
        "envelope_center_error_m":round(envelope_center_error,2),
        "gis_envelope_dimensions_m":[round(v,2) for v in gis_size],
        "model_envelope_dimensions_m":[round(v,2) for v in model_size],
        "envelope_dimension_error_percent":[round(v,2) for v in size_error_pct],
        "model_evaluated_local_bounds_m":inspection['evaluated_mesh_bounds_local'],
        "asset_path":entry['file'], "collection":inspection['collection_name'],
        "object_count":inspection['collection_object_count'], "portable":portable
      },
      "findings":[
        "Below passing threshold: the detailed structural footprint shape has low overlap with the official GIS footprint proxy (IoU 0.27), even though the outer envelope and placement center align closely.",
        "No authoritative height measurement or documented floor count was found; the 19.1 m top elevation and 3.8 m floor rhythm remain model estimates.",
        "Facade materials and broad massing match the official photo, while window assemblies, concrete panels, and entrance detailing are simplified."
      ],
      "threshold":8, "passed":score>=8,
      "paths":{"source_provenance":"source_provenance.json", "asset_inspection":"asset_inspection.json", "render":"owen_hall_facade.png"}
    }
    return result


if __name__ == '__main__':
    result = evaluate()
    (ROOT / 'evaluator_result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
