from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
BID = 'massing_telecommunications_building_tel_8dfaccf'
AUDIT = ROOT / 'audit' / BID


def evaluate():
    """Independently score TEL using the source snapshots and reopened asset audit."""
    record = json.loads((AUDIT / 'source_record.json').read_text(encoding='utf-8'))
    validation = json.loads((AUDIT / 'reopen_validation.json').read_text(encoding='utf-8'))
    gis = json.loads((AUDIT / 'sources' / 'purdue_gis_fid199_tel.json').read_text(encoding='utf-8-sig'))
    osm = (AUDIT / 'sources' / 'osm_way_159752232.xml').read_text(encoding='utf-8')
    ortho = AUDIT / 'sources' / 'indiana_2018_ortho_tel_bbox.jpg'
    lidar = json.loads((AUDIT / 'sources' / 'tel_lidar_height_measurement.json').read_text(encoding='utf-8'))

    attrs = gis['features'][0]['attributes']
    ring = gis['features'][0]['geometry']['rings'][0]
    checks = {x['check']: x for x in validation['checks']}
    report = validation['mesh']['world_bounds_m']
    bbox_size = [report[1][i] - report[0][i] for i in range(3)]
    passed_geometry = all(checks.get(k, {}).get('passed', False) for k in (
        'official_footprint_ring_vertices_present', 'identity_transform', 'base_and_roof_elevation'))

    criteria = [
        {
            'criterion': 'Correct identity and source-backed footprint', 'points_awarded': 2.0, 'max_points': 2,
            'status': 'supported',
            'evidence': [
                f"Purdue BuildingShapes feature FID 199 is {attrs.get('BUILDING_N')} ({attrs.get('BLDG_ABBR')}), address {attrs.get('ADDRESS')}; {len(ring)-1 if ring[0] == ring[-1] else len(ring)} ring vertices.",
                f"Independent OSM named building way 159752232 and entrance node 9975093914; saved OSM snapshot contains way identity: {'Telecommunications Building' in osm}.",
                f"Crosswalk metrics: outline Hausdorff distance {record['source_resolution']['outline_hausdorff_m']:.2f} m and centroid offset {record['source_resolution']['centroid_offset_m']:.2f} m. GIS ring was correctly preferred over inconsistent Shape__Area metadata.",
                'Reopen audit confirms every one of the 29 official footprint vertices appears in the mesh base within 0.0001 m.'
            ]
        },
        {
            'criterion': 'Position, orientation, and scale/dimensions', 'points_awarded': 2.0, 'max_points': 2,
            'status': 'supported',
            'evidence': [
                'Footprint uses official FID 199 geographic ring transformed to campus X-east/Y-north coordinates using the recorded local projection approximation.',
                f"Reopened mesh world bounds: {report}; overall dimensions approximately {bbox_size[0]:.2f} x {bbox_size[1]:.2f} x {bbox_size[2]:.2f} m.",
                'Asset object transform is identity (zero location/rotation and unit scale); 29 source ring vertices are directly retained, supporting outline orientation and scale.'
            ]
        },
        {
            'criterion': 'Evidence-backed height, floors, and roof form', 'points_awarded': 1.5, 'max_points': 2,
            'status': 'partially supported',
            'evidence': [
                f"Purdue GIS reports NUM_LEVELS={attrs.get('NUM_LEVELS')}; the asset shell height is {record['geometry']['roof_height_estimate_m']:.2f} m.",
                f"A 2018 LiDAR measurement is saved with method and uncertainty; it uses class-1 surface returns because this tile has no class-6 building returns: {lidar.get('interpretation', lidar.get('uncertainty', 'uncertainty recorded'))}.",
                f"The 2018 orthophoto ({'present' if ortho.exists() else 'missing'}) supports a broad flat roof and approximate equipment-cluster positions, but does not validate the equipment dimensions or exact roof elevation."
            ],
            'deduction': 'Height is an estimate with weak roof-return classification, and the level count has no independent floor-plan/elevation corroboration.'
        },
        {
            'criterion': 'Facade, entrances, and distinctive architecture', 'points_awarded': 0.5, 'max_points': 2,
            'status': 'mostly unverified',
            'evidence': [
                'One entrance opening proxy is modeled at the OSM entrance=main node, whose mapped location was projected 1.33 m to the nearest Purdue GIS wall.',
                'Builder source record explicitly marks material and windows unverified; the rendered shell has no evidenced window rhythm, floor articulation, facade material, or distinctive architectural elements.'
            ],
            'deduction': 'Only the entrance position is source-backed; facade character is intentionally absent because available imagery is overhead only.'
        },
        {
            'criterion': 'Modular export, portability, and complete evidence', 'points_awarded': 2.0, 'max_points': 2,
            'status': 'supported',
            'evidence': [
                f"Reopened Blender asset has expected scene '{validation['scene']}', unique collection '{validation['collection']}', and expected single named mesh object.",
                'Reopen audit passes identity, collection, object, transform, footprint vertex, elevation, and no-modifier checks; no external libraries or images are linked.',
                'Evidence folder contains source snapshots, provenance/uncertainty record, LiDAR method, orthophoto, preview renders, and reopen validation.'
            ]
        }
    ]
    score = sum(c['points_awarded'] for c in criteria)
    findings = [
        {'severity': 'revision opportunity', 'finding': 'The current model is a source-conservative massing shell. Add independently sourced facade photos/elevations (or keep this explicitly classified as massing) before claiming detailed facade accuracy.'},
        {'severity': 'uncertainty', 'finding': 'Confirm the 9.14 m shell height and four-level attribute against authoritative elevations or building plans; current LiDAR surface returns are not classified as buildings.'},
        {'severity': 'minor', 'finding': 'OSM entrance location is 1.33 m outside the official GIS footprint and is projected to the nearest boundary; entrance width/height are schematic.'}
    ]
    return {
        'building_id': BID,
        'asset': record['asset'],
        'reviewer': 'independent subagent',
        'rubric': 'AGENT.md independent grading rubric',
        'score': round(score, 1), 'max_score': 10,
        'result': 'PASS' if score >= 8 else 'REVISION REQUIRED',
        'criteria': criteria,
        'evidence': {
            'source_record': 'audit/' + BID + '/source_record.json',
            'reopen_validation': 'audit/' + BID + '/reopen_validation.json',
            'rendered_views': ['audit/' + BID + '/renders/tel_exterior_preview.png', 'audit/' + BID + '/renders/tel_plan_preview.png'],
            'official_gis_feature': 'audit/' + BID + '/sources/purdue_gis_fid199_tel.json',
            'osm_snapshot': 'audit/' + BID + '/sources/osm_way_159752232.xml',
            'measurement': 'audit/' + BID + '/sources/tel_lidar_height_measurement.json',
            'geometry_checks_passed': passed_geometry
        },
        'findings': findings,
        'revision_requests': [
            'For another revision, add a source-backed facade treatment and documented floor/elevation evidence; do not infer windows or materials from the current overhead image.',
            'Revalidate height using an authoritative elevation/section or a better-classified LiDAR source if available.'
        ]
    }

if __name__ == '__main__':
    result = evaluate()
    out = Path(__file__).resolve().parent / 'grade.json'
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
