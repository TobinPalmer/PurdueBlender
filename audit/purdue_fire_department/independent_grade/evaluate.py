from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'audit' / 'purdue_fire_department'
EXPECTED_SHA = '25cfbd3b81e61c614d4d4f49c3cd7e7525e16bc9b5d55dcb27e82ac8bb191f59'

def evaluate():
    probe = json.loads((BASE / 'independent_grade' / 'footprint_probe.json').read_text(encoding='utf-8'))
    validation = json.loads((BASE / 'asset_validation.json').read_text(encoding='utf-8'))
    evidence = json.loads((BASE / 'evidence.json').read_text(encoding='utf-8'))
    geo = json.loads((BASE / 'sources' / 'dmnt_feature_211.geojson').read_text(encoding='utf-8'))
    feature = geo['features'][0]
    props = feature['properties']

    assert probe['asset_sha256'] == EXPECTED_SHA
    assert validation['asset_sha256'] == EXPECTED_SHA
    assert validation['verified_after_fresh_open'] is True
    assert probe['gis_feature_id'] == 211 and props['BLDG_ABBR'] == 'DMNT'
    assert probe['source_to_shell_max_vertex_error_m'] < 0.005
    assert probe['shell_to_source_max_vertex_error_m'] < 0.005
    assert validation['external_image_paths'] == []

    criteria = [
        {
            'criterion': 'Correct identity and source-backed footprint', 'score': 2.0, 'max_score': 2.0,
            'status': 'verified',
            'evidence': [
                'Purdue Archives identifies Clayton W. Dement Fire Station (DMNT) as Purdue’s fire station and describes it as a three-bay brick station: https://collections.lib.purdue.edu/campus/buildings/53',
                'Purdue Facilities Operations says Purdue University Fire Department is located at 1250 W Third Street: https://www.purdue.edu/operations/operations-maintenance/wp-content/uploads/sites/7/2025/12/bd-manual.pdf',
                'Official campus GIS FID 211 identifies Clayton W. Dement Fire Station, DMNT, 1250 3rd Street. Independent coordinate comparison found maximum vertex deviation from the model’s structural shell of %.6f m.' % probe['source_to_shell_max_vertex_error_m'],
            ],
            'reason': 'The naming mismatch is resolved by Purdue primary sources: this building is the home station of the Purdue University Fire Department.'
        },
        {
            'criterion': 'Position, orientation, and scale/dimensions', 'score': 2.0, 'max_score': 2.0,
            'status': 'verified against the project campus transform',
            'evidence': [
                'The model structural shell follows all 14 transformed GIS footprint vertices with maximum bidirectional nearest-vertex error %.6f m.' % max(probe['source_to_shell_max_vertex_error_m'], probe['shell_to_source_max_vertex_error_m']),
                'The model preserves the source campus-world coordinate convention and the exact stable asset ID/path; no rescaling or rotation was applied.',
                'Plan extent from source polygon is approximately %.3f m east-west by %.3f m north-south.' % (probe['shell_bounds_m'][0][1] - probe['shell_bounds_m'][0][0], probe['shell_bounds_m'][1][1] - probe['shell_bounds_m'][1][0]),
            ],
            'reason': 'Footprint placement, orientation, and scale agree with the project-transformed official GIS polygon. The project transform is explicitly an approximate local conversion, not a survey CRS.'
        },
        {
            'criterion': 'Evidence-backed height, floors, and roof form', 'score': 1.0, 'max_score': 2.0,
            'status': 'partially verified; total height estimated',
            'evidence': [
                'GIS record reports two levels and an Extrution value of 15, but its unit and meaning are not documented in the snapshot.',
                'The 14.6 m maximum model roof and split between low office wing and taller apparatus volume are estimates interpreted from street-level images; no surveyed/elevation drawing was found.',
                'The saved asset’s vertical bound is 0 to 14.6 m.'
            ],
            'reason': 'The low/raised roof silhouette is visible and the two-level attribute is source-backed, but the modeled heights are not measured or resolved quantitatively.'
        },
        {
            'criterion': 'Facade, entrances, and distinctive architecture', 'score': 1.4, 'max_score': 2.0,
            'status': 'mostly supported, some interpretation',
            'evidence': [
                'The archived Purdue source describes brick construction and a three-bay station; the 2013 Purdue fire-truck image is attributed to the station: https://www.purdue.edu/newsroom/archive/releases/2013/Q4/chief,-longest-serving-firefighter-reflect-on-pufds-50th-anniversary.html',
                'Current Street View directly shows red-brown brick, pale sectional doors, a red canopy/fascia, a personnel entrance, and a taller dark ribbed-metal attached hall. Saved 2026 panorama IDs and raw images are in the building sources folder.',
                'The model represents these features with nine assigned materials, including UV brick pattern, glazing, sectional panels, metal cladding, roof metal and trim. The preview was visually compared with the saved Street View frame.',
            ],
            'reason': 'The principal materials and silhouette read correctly. The current frontal image clearly exposes two vehicle doors; a third bay is supported only by the historic three-bay description, and its exact location/configuration is interpretive.'
        },
        {
            'criterion': 'Modular export, portability, and complete evidence', 'score': 2.0, 'max_score': 2.0,
            'status': 'verified',
            'evidence': [
                'Fresh Blender 5.2.3 background open verified expected scene and collection, 99 mesh objects, every mesh has an assigned material, no objects outside the export collection, and no external image paths.',
                'Asset SHA-256 is %s and matches the evidence record.' % EXPECTED_SHA,
                'The building-specific evidence folder contains raw GIS, official Purdue records, Street View panoramas, provenance, validator, and a rendered preview.'
            ],
            'reason': 'The asset opens cleanly, retains the stable export contract, and has portable self-contained materials plus source records.'
        }
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    return {
        'building': 'Clayton W. Dement Fire Station (Purdue University Fire Department)',
        'asset_id': 'massing_purdue_fire_department_520430b',
        'asset_path': 'modular/buildings/massing_purdue_fire_department_520430b.blend',
        'asset_sha256': EXPECTED_SHA,
        'grader': 'independent_grader_subagent',
        'grade_date': '2026-10-26',
        'score': score,
        'max_score': 10,
        'passing_threshold': 8,
        'status': 'PASS' if score >= 8 else 'FAIL',
        'criteria': criteria,
        'evidence': [
            'Independent Blender API probe: audit/purdue_fire_department/independent_grade/footprint_probe.json',
            'Fresh-open validation: audit/purdue_fire_department/asset_validation.json',
            'Source/provenance inventory: audit/purdue_fire_department/evidence.json',
            'Visual comparison: audit/purdue_fire_department/purdue_fire_department_preview.png against sources/google_streetview_dmnt_2026_yaw0.jpg and the yaw 90/270 views.'
        ],
        'findings': [
            'No identity mismatch: Purdue confirms PUFD’s base is the Clayton W. Dement Fire Station at 1250 W Third Street.',
            'The structural plan matches the source footprint to sub-millimeter tolerance in the project’s approximate coordinate frame.',
            'Roof heights remain estimates; no surveyed vertical data was located.',
            'The third apparatus bay is not clearly visible in the current straight-on panorama; its historic existence is sourced but exact facade placement remains an interpretation.',
            'No room layout or interior contents are modeled because the available source set does not establish them.'
        ]
    }

if __name__ == '__main__':
    result = evaluate()
    out = Path(__file__).with_name('result.json')
    out.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
