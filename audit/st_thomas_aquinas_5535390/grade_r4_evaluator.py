from __future__ import annotations
import json
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
EXPECTED = 'a06977c0783442a0eb7561d23e294bfc65d11546b3aa4a0c13d9c9b62f68a330'

def read(name):
    return json.loads((AUDIT / name).read_text(encoding='utf-8'))

def evaluate_r4():
    reopen = read('independent_grade_r4_reopen.json')
    placement = read('independent_grade_r4_master_marker.json')
    footprint = read('footprint_match_r4.json')
    assert reopen['sha256'] == EXPECTED and reopen['hash_matches_expected']
    assert placement['asset_sha256'] == EXPECTED and placement['hash_matches']
    assert footprint['GIS_feature_id'] == 852 and footprint['intersection_over_union'] > 0.999
    assert placement['marker_position_error_m'] < 0.001
    criteria = [
        {
            'criterion': 'Correct identity and source-backed footprint', 'score': 1.9, 'max_score': 2.0,
            'status': 'Strong match; public-map limitation retained',
            'evidence': f"Purdue BuildingShapes FID {footprint['GIS_feature_id']} identifies St. Thomas Aquinas Center, {footprint['GIS_address']}. The saved foundation base perimeter independently polygonized from 43 horizontal mesh edges compares with the source outline at IoU {footprint['intersection_over_union']:.9f}, symmetric difference {footprint['symmetric_difference_area_m2']:.8f} m2, and boundary Hausdorff distance {footprint['boundary_hausdorff_distance_m']:.7f} m. The GIS outline is not a surveyed structural-wall line."
        },
        {
            'criterion': 'Position, orientation, and scale/dimensions', 'score': 1.9, 'max_score': 2.0,
            'status': 'Verified within project transform; survey limitation retained',
            'evidence': f"Fresh read-only master reopen confirms Placement_massing_st_thomas_aquinas_5535390 instances the expected library with zero rotation, unit scale, and {placement['marker_position_error_m']:.8f} m XY error from the documented local origin. The structural base is about 42.83 x 65.23 m and agrees with the transformed GIS outline. The project uses an approximate local conversion, not a survey CRS."
        },
        {
            'criterion': 'Evidence-backed height, floors, and roof form', 'score': 1.2, 'max_score': 2.0,
            'status': 'Partly supported; vertical dimensions estimated',
            'evidence': "The model separates a pitched sanctuary volume with bell tower/cross from connected flat-roof additions. The architect project page supports a 1965 sanctuary retained within a 2001 connection of three earlier campus structures and describes new narthex/classroom/church-related spaces. R4 gable infill and flashing improve the roof meeting, and exterior views show continuous volumes. No as-built elevation, measured roof pitch, floor-to-floor heights, or verified 20.10 m top-of-cross height was found; the roof/addition junction remains stylized."
        },
        {
            'criterion': 'Facade, entrances, and distinctive architecture', 'score': 1.3, 'max_score': 2.0,
            'status': 'Improved and legible; several details remain schematic',
            'evidence': "The model has red brick, limestone bands, repeated glazing, signed entry/canopy, pitched sanctuary roof, tower/cross, and separate office/classroom wing. R4 reduces brick contrast/relief and resolves the sanctuary framing: the exact asset contains 36 truss pieces forming six trusses on continuous wall plates. Classroom cutaways show boards/frames, lecterns, cabinets, tables and stairs. Wall/room plans are unavailable, furniture and trim are schematic, and the interior remains sparse/repetitive. Four narrow exterior downspouts are valid named corner downspouts (0.10 x 0.10 m, Z 0.75 to 8.40 m), not unsupported framing; they look detached only in the structure cutaway because the host walls are hidden."
        },
        {
            'criterion': 'Modular export, portability, and complete evidence', 'score': 1.9, 'max_score': 2.0,
            'status': 'Passes exact-file technical checks',
            'evidence': f"A new Blender 5.2.3 LTS process reopened the exact SHA and found the expected scene/export collection, {reopen['object_count']} collection objects ({reopen['object_type_counts'].get('MESH', 0)} meshes), identity root and local-origin properties; no empty meshes, materialless meshes, invalid material slots, missing images, or linked libraries. Eighteen used procedural materials are present. GIS/OSM raw snapshots, CRS/conversion details, architect/parish sources, uncertainty notes, fresh reopen and review renders are recorded in this building audit folder."
        }
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    return {
        'building': 'St. Thomas Aquinas Center', 'revision': 'R4',
        'asset': 'modular/buildings/massing_st_thomas_aquinas_5535390.blend',
        'sha256': EXPECTED, 'blender_version': reopen['blender_version'],
        'score': score, 'max_score': 10.0, 'pass_threshold': 8.0, 'passed': score >= 8.0,
        'criteria': criteria,
        'evidence': {
            'fresh_asset_reopen': 'independent_grade_r4_reopen.json',
            'fresh_master_marker': 'independent_grade_r4_master_marker.json',
            'foundation_vs_GIS_geometry': 'footprint_match_r4.json',
            'geometry_edge_extraction': 'footprint_extract_r4.json',
            'renders': ['exterior_north_entry_r4.png', 'exterior_southeast_r4.png', 'topdown_footprint_r4.png', 'interior_sanctuary_cutaway_r4.png', 'interior_sanctuary_structure_r4.png', 'interior_classroom_cutaway_r4.png']
        },
        'findings': [
            'R4 corrected the previous floating sanctuary framing: trusses now bear on continuous wall plates and are visible in the structure section.',
            'The 43-edge foundation footprint aligns with the named Purdue GIS outline to numerical precision under the approximate local transform; the outline is not a surveyed wall line.',
            'Main roof volumes read as connected in the exterior views; the pitched-to-flat junction still uses an estimated, simplified flashing/infill detail.',
            'Four thin vertical objects visible in the cutaway are named exterior downspouts at the original church corners. Their facade hosts are hidden for the cutaway, making them appear to float; they are not stray supports.',
            'Height, roof pitch, interior partitions, and classroom layout remain schematic or unverified because measured elevations and as-built plans were not found.'
        ],
        'sources': [
            {'provider': 'Purdue GIS BuildingShapesZip4', 'feature': 'FID 852, 535 STATE ST', 'url': 'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/852', 'source_crs': 'EPSG:3857 (WKID 102100 per service metadata); queried/projected using the project local approximate XY conversion', 'retrieved': '2026-10-25'},
            {'provider': 'OpenStreetMap', 'feature': 'way 117396617, St. Thomas Aquinas', 'url': 'https://www.openstreetmap.org/way/117396617', 'retrieved': '2026-10-25'},
            {'provider': 'J.W. McQuiston Architecture', 'feature': 'St. Thomas Aquinas project description and exterior photos', 'url': 'https://www.jwmcq.com/st-thomas-aquinas', 'reviewed': '2026-10-25'},
            {'provider': 'St. Thomas Aquinas Catholic Center at Purdue', 'feature': 'Project Renewal / three connected building components', 'url': 'https://www.boilercatholics.org/project-renewal', 'reviewed': '2026-10-25'}
        ]
    }

if __name__ == '__main__':
    result = evaluate_r4()
    (AUDIT / 'independent_grade_r4.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))
