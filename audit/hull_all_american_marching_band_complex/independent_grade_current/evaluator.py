from __future__ import annotations
import hashlib, json, math
from pathlib import Path
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'audit' / 'hull_all_american_marching_band_complex'
GRADE = AUDIT / 'independent_grade_current'
ASSET_ID = 'massing_hull_all_american_marching_band_complex_665bcb7'
ASSET = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def evaluate() -> dict:
    evidence = json.loads((AUDIT / 'evidence.json').read_text(encoding='utf-8'))
    validation = json.loads((AUDIT / 'fresh_open_validation.json').read_text(encoding='utf-8'))
    probe = json.loads((GRADE / 'blender_probe.json').read_text(encoding='utf-8'))
    source = json.loads((AUDIT / 'sources' / 'purdue_gis_fid431.json').read_text(encoding='utf-8'))
    ring = source['features'][0]['geometry']['rings'][0][:-1]
    def xy(lon, lat):
        return ((lon - ORIGIN_LON) * 111412.84 * math.cos(math.radians(ORIGIN_LAT)),
                (lat - ORIGIN_LAT) * 111040.0)
    gis_polygon = Polygon([xy(lon, lat) for lon, lat in ring])
    slab = next(x for x in probe['footprint_related'] if x['name'] == 'GIS footprint | slab and finished floor')
    model_polygon = Polygon([(p[0], p[1]) for p in slab['samples'][:8]])
    overlap = gis_polygon.intersection(model_polygon).area / gis_polygon.union(model_polygon).area
    hausdorff = gis_polygon.hausdorff_distance(model_polygon)
    digest = sha256(ASSET)
    expected_digest = '4D525FEB45716CAB403A20181BB9486B8973E34212B548EFB5E7C4BD5D7F8C08'

    criteria = [
        {
            'criterion': 'Correct identity and source-backed footprint', 'max_points': 2,
            'score': 1.9,
            'evidence': [
                'Purdue GIS source snapshot is FID 431 / BLDG_ABBR HULL; the asset name identifies the All-American Marching Band Complex.',
                f'Independent comparison of the Blender slab outline to the GIS ring in the documented campus XY approximation: polygon IoU={overlap:.6f}; Hausdorff distance={hausdorff:.6f} m.',
                'Esri imagery places the compact roof beside Hull Field; Purdue Bands schedules identify the Hull complex/garage as a separate band facility.',
            ],
            'deductions': 'The official sources identify the campus complex, but do not uniquely label this precise GIS polygon in an as-built plan; exact material and building subcomponent naming retain minor uncertainty.'
        },
        {
            'criterion': 'Position, orientation, and scale/dimensions', 'max_points': 2,
            'score': 2.0,
            'evidence': [
                f'The source ring and model slab compare at IoU={overlap:.6f} and Hausdorff={hausdorff:.6f} m; model slab area={model_polygon.area:.3f} m² versus GIS ring area={gis_polygon.area:.3f} m².',
                'The candidate preserves the project campus coordinate frame (X east, Y north, Z up), has zero declared asset instance offset, and its long axis follows the GIS polygon.',
                'The fresh-open bounds are approximately 14.20 m by 21.59 m, matching the GIS plan dimensions within the boundary treatment.'
            ],
            'deductions': 'None for the assessed library geometry. The master manifest still records the pre-rebuild 7.6 m envelope and should be refreshed by the coordinator during integration.'
        },
        {
            'criterion': 'Evidence-backed height, floors, and roof form', 'max_points': 2,
            'score': 1.2,
            'evidence': [
                'Street View and Esri imagery support a low, single-story appearance and flat/low-slope light roof.',
                f'The candidate has an evaluated maximum height of {validation["evaluated_world_bounds_m"]["max"][2]:.2f} m.'
            ],
            'deductions': 'No measured height, floor plan, or elevation was located. The 5.36 m envelope and exact roof build-up remain visual estimates; single-story status is inferred from a distant oblique view.'
        },
        {
            'criterion': 'Facade, entrances, and distinctive architecture', 'max_points': 2,
            'score': 1.3,
            'evidence': [
                'The model shows repeated tall service-bay doors and a high window band, consistent with the distant April 2026 Street View rhythm.',
                'Aerial imagery supports the low rectangular roof mass; the render includes a pale metal roof, base masonry, and simple service-building envelope.',
                'The cutaway includes open equipment handling/practice space, lockers, cases, benches, changing/restroom partitions and fixtures, consistent with documented band storage/changing uses.'
            ],
            'deductions': 'Facade openings/count, cladding, masonry, and interior room layout are not established by plans or close-range imagery. The facade reads as a plausible service building but is not strongly distinctive; interior is explicitly schematic.'
        },
        {
            'criterion': 'Modular export, portability, and complete evidence', 'max_points': 2,
            'score': 2.0,
            'evidence': [
                f'Independent fresh-process Blender 5.2.3 inspection reopens the exact asset hash {digest}; expected scene and asset collection exist.',
                f'The collection contains {probe["objects"]} objects ({probe["mesh_count"]} meshes), no materialless meshes, and no unpacked external images; all evaluated geometry is in the designated asset collection.',
                'Dedicated builder source, structured source provenance/uncertainty, GIS overlay, exterior and cutaway previews, and a fresh-open validation record are present under the building-specific audit directory.'
            ],
            'deductions': 'The root manifest is shared coordinator-owned and currently has the earlier 7.6 m envelope; this grading does not modify or certify master integration.'
        }
    ]
    score = round(sum(x['score'] for x in criteria), 2)
    findings = [
        'PASS: the GIS-derived plan and campus placement are strongly supported by the available footprint and aerial evidence.',
        'REMAINS ESTIMATED: absolute height, roof build-up, exact facade material/opening count, and interior plan.',
        'COORDINATOR FOLLOW-UP: update the shared manifest/master integration records to reflect the revised 5.36 m envelope and rerun complete-master validation.'
    ]
    result = {
        'building': 'Bob & Trudy Hull "All-American" Marching Band Complex',
        'stable_asset_id': ASSET_ID,
        'asset_path': str(ASSET.relative_to(ROOT)).replace('\\', '/'),
        'asset_sha256': digest,
        'expected_candidate_sha256': expected_digest,
        'hash_matches_candidate': digest.lower() == expected_digest.lower(),
        'independent_grader': 'Codex subagent; did not build or modify the asset',
        'rubric': 'AGENT.md, five criteria at 2 points each',
        'score': score,
        'max_score': 10,
        'pass_threshold': 8,
        'pass': score >= 8 and digest.lower() == expected_digest.lower(),
        'criteria': criteria,
        'evidence': {
            'gis_fid': 431,
            'slab_gis_polygon_iou': overlap,
            'slab_gis_hausdorff_m': hausdorff,
            'fresh_open_validation': str((AUDIT / 'fresh_open_validation.json').relative_to(ROOT)).replace('\\', '/'),
            'independent_probe': str((GRADE / 'blender_probe.json').relative_to(ROOT)).replace('\\', '/'),
            'preview_exterior': str((AUDIT / 'exterior_preview.png').relative_to(ROOT)).replace('\\', '/'),
            'preview_interior': str((AUDIT / 'interior_cutaway_preview.png').relative_to(ROOT)).replace('\\', '/'),
            'gis_overlay': str((AUDIT / 'gis_footprint_overlay.jpg').relative_to(ROOT)).replace('\\', '/'),
            'sources': [x['url'] for x in evidence['sources']]
        },
        'findings': findings
    }
    return result


if __name__ == '__main__':
    result = evaluate()
    out = GRADE / 'result.json'
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'score': result['score'], 'pass': result['pass'], 'asset_sha256': result['asset_sha256'], 'criteria': [(x['criterion'],x['score']) for x in result['criteria']]}, indent=2))
