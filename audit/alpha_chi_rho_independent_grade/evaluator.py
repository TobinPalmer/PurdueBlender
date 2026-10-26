import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'audit/alpha_chi_rho_independent_grade'
probe = json.loads((OUT / 'independent_probe.json').read_text(encoding='utf-8'))
evidence = (ROOT / 'audit/alpha_chi_rho/evidence.md').read_text(encoding='utf-8')

criteria = [
    {
        'criterion': 'Identity and source-backed footprint', 'points': 1.9, 'max_points': 2,
        'evidence': [
            f"Purdue BuildingShapes FID {probe['gis']['feature_id']} identifies {probe['gis']['building_name']} ({probe['gis']['abbreviation']}) at {probe['gis']['address']}.",
            f"All {probe['gis_ring_count']} GIS ring corners match ground-level mesh vertices within {probe['max_source_ring_vertex_nearest_error_m']:.6f} m.",
            'The independent check uses the same official GIS snapshot that informed construction; it does not independently verify the real-world survey or parcel-to-building match.'
        ],
        'deduction': 'Minor: no second independent footprint/survey source.'
    },
    {
        'criterion': 'Position, orientation, and scale', 'points': 1.7, 'max_points': 2,
        'evidence': [
            'Model footprint bounds and GIS bounds are consistent with the same polygon and project local-coordinate conversion.',
            'The project explicitly labels its lon/lat-to-campus-meters conversion as an approximation rather than a surveyed projection.'
        ],
        'deduction': 'Small: no independent geodetic control or site survey confirms absolute placement and scale.'
    },
    {
        'criterion': 'Height, floors, and roof', 'points': 1.1, 'max_points': 2,
        'evidence': [
            f"The GIS feature reports {probe['gis']['num_levels']} level; the mesh spans Z={probe['bounds_world_m'][2][0]:.2f}–{probe['bounds_world_m'][2][1]:.2f} m.",
            'Evidence identifies the 3.8 m wall and 0.35 m flat roof cap as modeling estimates; GIS Extrution=12 has no documented unit or method.'
        ],
        'deduction': 'Height and roof profile are not source-backed; elevation field lacks a vertical datum.'
    },
    {
        'criterion': 'Facade, entrances, and distinctive architecture', 'points': 0.8, 'max_points': 2,
        'evidence': [
            'The asset includes horizontal siding, openings, a door, trim, and a small entrance canopy; the preview reads as a simple low one-story mass.',
            'The 1978 Purdue Debris photo supports only historical siding/window language, not the present facade.'
        ],
        'deduction': 'Current exterior, opening pattern, roof, and entrance dimensions are explicitly unverified; no current dated photograph or measured elevation substantiates these features.'
    },
    {
        'criterion': 'Modular export, portability, and evidence', 'points': 2.0, 'max_points': 2,
        'evidence': [
            f"The expected asset collection contains {probe['asset_object_count']} mesh object with {probe['mesh_vertices']} vertices, {probe['mesh_polygons']} polygons, and {len(probe['material_names'])} material slots.",
            'The independent Blender open probe succeeded; builder evidence records saved-file reopen validation and clean-scene append/save/reopen validation as PASS.',
            f"No external image dependencies; {len(probe['asset_collections'])} Asset_ collection is present, and the named scene/collection conventions are satisfied."
        ],
        'deduction': None
    }
]
score = round(sum(c['points'] for c in criteria), 2)
assert score == 7.5, score
assert all(c['points'] <= c['max_points'] for c in criteria)
assert probe['asset_file_opens'] and probe['expected_collection_present'] and probe['mesh_object_count'] == 1
assert probe['max_source_ring_vertex_nearest_error_m'] < 0.0001

result = {
    'asset': 'modular/buildings/massing_alpha_chi_rho_0cb591a.blend',
    'independent_grade': True,
    'score': score,
    'max_score': 10,
    'pass_threshold': 8,
    'status': 'FAIL',
    'criteria': criteria,
    'findings': [
        {'severity':'major','finding':'Present-day architecture is not verified. Roof form, height, current facade rhythm, windows, and entrance geometry rely on illustration or estimates.', 'recommended_evidence':'Add dated current exterior photos (multiple facades/roofline) or dimensioned elevations and cite the sources.'},
        {'severity':'moderate','finding':'The excellent footprint match is internally consistent with the official FID 775 geometry but is not independent validation of geospatial registration.', 'recommended_evidence':'Cross-check against a campus survey, orthophoto/building outline from a separate authoritative source, or surveyed control points.'},
        {'severity':'minor','finding':'The 625 elevation attribute has no documented vertical datum; the model correctly leaves the origin at local Z=0.'}
    ],
    'remaining_uncertainty': [
        'Whether the queried GIS outline precisely represents the current above-ground building perimeter.',
        'Absolute horizontal registration accuracy of the project-specific local coordinate approximation.',
        'Current height, roof geometry, facade openings/materials, and entrance placement.'
    ],
    'evidence_files': [
        'audit/alpha_chi_rho_independent_grade/independent_probe.json',
        'audit/alpha_chi_rho/evidence.md',
        'audit/alpha_chi_rho/reopen_validation.json',
        'audit/alpha_chi_rho/export_reopen_probe.json',
        'audit/alpha_chi_rho/alpha_chi_rho_preview.png'
    ],
    'rubric_note': 'Scores reflect source-backed correctness, not visual finish alone. Evidence assertions in the asset audit were treated as documentary evidence; geometric checks were independently repeated against the saved blend but necessarily share the builder source polygon.'
}
(OUT / 'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'score': score, 'max_score':10, 'status':result['status'], 'criteria':[{k:c[k] for k in ('criterion','points','max_points')} for c in criteria], 'findings':len(result['findings'])}, indent=2))
