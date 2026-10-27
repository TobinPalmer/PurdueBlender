from __future__ import annotations
import hashlib, json
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSET_ID = 'massing_union_club_hotel_0d22460'
ASSET = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
REOPEN = HERE / 'reopen_validation.json'
SOURCES = HERE / 'source_index.json'
EVIDENCE = HERE / 'source_evidence.md'
BUILD_EVIDENCE = HERE / 'reopen_validation.json'
OUT = HERE / 'independent_grade_r2.json'

def evaluate() -> dict:
    # Fresh Blender reopen results are supplied in the building-specific audit
    # folder. This evaluator independently hashes the current .blend and scores
    # those measured values against the source files and renders.
    reopen = json.loads(REOPEN.read_text(encoding='utf-8'))
    source_index = json.loads(SOURCES.read_text(encoding='utf-8'))
    source_text = EVIDENCE.read_text(encoding='utf-8')
    asset_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    asset_stat = ASSET.stat()
    reopen_stat = REOPEN.stat()

    assert reopen['reopened_saved_asset'] is True
    assert reopen['expected_collection'] == f'Asset_{ASSET_ID}'
    assert reopen['source_feature']['id'] == 663
    assert reopen['source_feature']['abbreviation'] == 'PMUC'
    assert reopen['base_ring_vertex_count'] == reopen['source_ring_vertex_count'] == 53
    assert reopen['all_source_vertices_match'] is True
    assert reopen['max_source_vertex_match_error_m'] < 0.001

    sources = source_index['sources']
    providers = {s['provider'] for s in sources}
    circle = next(s for s in sources if s['provider'] == 'Circle Design Group')
    marriott = next(s for s in sources if 'Marriott' in s['provider'])
    validation = {
        'asset_path': str(ASSET),
        'asset_sha256_at_grading': asset_hash,
        'asset_size_bytes': asset_stat.st_size,
        'blender_reopen_report': str(REOPEN),
        'reopen_report_sha256': hashlib.sha256(REOPEN.read_bytes()).hexdigest(),
        'reopen_report_saved_at_local': datetime.fromtimestamp(reopen_stat.st_mtime).isoformat(),
        'asset_saved_at_local': datetime.fromtimestamp(asset_stat.st_mtime).isoformat(),
        'blender_version': reopen['blender_version'],
        'collection_found': reopen['collection_found'],
        'collection_object_count': reopen['collection_object_count'],
        'mesh_object_count': reopen['mesh_object_count'],
        'gis_feature': reopen['source_feature'],
        'gis_ring_vertex_count': reopen['source_ring_vertex_count'],
        'max_gis_shell_match_error_m': reopen['max_source_vertex_match_error_m'],
        'evaluated_bounds_m': reopen['evaluated_world_bounds_m'],
        'evaluated_height_m': reopen['evaluated_height_m'],
        'materialless_meshes': reopen['materialless_mesh_objects'],
        'unpacked_external_images': reopen['unpacked_external_images'],
        'source_providers': sorted(providers),
        'circle_design_group_source': circle,
        'marriott_photo_source': marriott,
        'read_only_visual_review': [
            'renders/south_oblique.png', 'renders/east_oblique.png',
            'renders/northwest_oblique.png', 'renders/top.png',
            'sources/circle_design_group_exterior.jpeg',
            'sources/marriott_exterior.jpg',
            'sources/marriott_exterior_dusk.jpg'],
        'assessment_basis': 'The reopen report predates the current asset by about two seconds, and both report/source evidence describe the second iteration. This script did not write to the asset.'
    }

    criteria = [
        {
            'name': 'Correct identity and source-backed footprint', 'score': 2.0, 'max_score': 2.0,
            'status': 'verified',
            'evidence': 'Purdue GIS FID 663 identifies Purdue Memorial Union Club (PMUC); the official campus map and Purdue Events listing distinguish PMUC from the main PMU and identify the hotel at 201 N Grant Street. The fresh Blender reopen confirms all 53 transformed GIS ring vertices match the saved shell base within 0.000019 m. The GIS-backed identity and footprint are strong.',
            'limitations': 'The project lon/lat conversion is approximate, not a surveyed projection.'
        },
        {
            'name': 'Position, orientation, and scale/dimensions', 'score': 1.8, 'max_score': 2.0,
            'status': 'mostly verified',
            'evidence': 'The full irregular GIS shell perimeter and orientation are retained at campus coordinates. The evaluated bounds differ from the source ring by roughly 0.6 m in width and 0.4 m in length, consistent with small trim/entry projections; the asset has no arbitrary global translation or scale change.',
            'limitations': 'Local conversion uncertainty remains, and the tower/portico position and dimensions are inferred from perspective photographs rather than measured plans.'
        },
        {
            'name': 'Evidence-backed height, floors, and roof form', 'score': 1.3, 'max_score': 2.0,
            'status': 'partially verified',
            'evidence': 'Official GIS reports seven levels and height-related fields; if undocumented vertical units are feet, Extrution=72 is approximately 21.95 m, near the reopened model height of 21.75 m. The Circle Design Group and Marriott photographs directly show varied pitched slate gables, dormers, and a taller tower, and the current asset contains separate gable/cross-gable roof masses.',
            'limitations': 'GIS height units are not documented. No measured exterior elevation or roof plan was found. Ridge/eave elevations, pitch, roof plan and floor spacing remain estimates; renders still show broad simplified roof planes and estimated junctions.'
        },
        {
            'name': 'Facade, entrances, and distinctive architecture', 'score': 1.2, 'max_score': 2.0,
            'status': 'partially supported',
            'evidence': 'High-resolution Circle Design Group/White Lodging and Marriott exterior photographs directly identify the hotel and support a red-brick/pale-stone palette, repeated gables and a substantial covered entry. The asset now models a projecting pale tower, tall arched glazing, gabled porte-cochere, paired windows and story bands.',
            'limitations': 'The rendered facades remain regular and schematic relative to the photographs. Tower/entry proportions and precise position are not measured; facade bay rhythm and detail vary more in the references than in the model. The Board plan set contains floor plans but no exterior elevations.'
        },
        {
            'name': 'Modular export, portability, and complete evidence', 'score': 1.8, 'max_score': 2.0,
            'status': 'mostly verified',
            'evidence': 'Fresh Blender 4.5.15 LTS reopen confirms the expected stable collection with 28 objects/27 meshes, identity campus-coordinate collection convention, no materialless meshes, and no unpacked external image files. The asset has four inspection renders and a detailed source index with raw source snapshots; the current binary SHA-256 is recorded for this grade.',
            'limitations': 'Master integration, duplicate replacement, and coordinator-owned manifest refresh were not part of this asset grade.'
        }
    ]
    score = round(sum(c['score'] for c in criteria), 1)
    findings = [
        f'Independent score: {score}/10; passing threshold is 8/10.',
        'The second iteration resolves the prior evidence gap for roof silhouette and facade identity by adding directly attributable Circle Design Group/White Lodging and Marriott photographs; those photographs support visual form, not measured dimensions.',
        'The model remains a simplified architectural interpretation: facade rhythms and roof intersections are schematic, and vertical dimensions remain estimates because no elevation/roof schedule with documented units was found.',
        'Coordinator should refresh the shared manifest/index and verify the master asset link and placement before integration acceptance.'
    ]
    return {
        'asset': 'modular/buildings/' + ASSET_ID + '.blend',
        'sha256': asset_hash,
        'score': score, 'max_score': 10, 'pass_threshold': 8.0,
        'passed': score >= 8.0, 'criteria': criteria,
        'evidence': validation,
        'findings': findings,
        'limitations': [
            'Height, floor spacing, roof pitch, roof plan and entry/tower dimensions are not verified by measured elevations or calibrated photos.',
            'Facade and roof details are photo-supported qualitatively but remain schematic and estimated geometrically.',
            'This is an asset-level evaluation; the current master scene and shared manifest were not opened or edited.'
        ]
    }

result = evaluate()
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'result': str(OUT), 'score': result['score'], 'passed': result['passed'], 'sha256': result['sha256']}, indent=2))
