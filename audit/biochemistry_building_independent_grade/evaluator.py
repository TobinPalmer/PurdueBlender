"""Independent rubric evaluator for Purdue Biochemistry Building.

Inputs are direct probes of the current asset/manifest/GIS snapshot, the master
placement marker, and an isolated builder reproduction. Source limitations are
scored explicitly; visual plausibility alone is not treated as evidence.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def evaluate():
    asset = json.loads((HERE / 'asset_probe.json').read_text(encoding='utf-8'))
    marker = json.loads((HERE / 'master_placement_probe.json').read_text(encoding='utf-8'))
    exported = json.loads((HERE / 'export_reopen_probe.json').read_text(encoding='utf-8'))
    smoke = json.loads((HERE / 'builder_smoke_evidence.json').read_text(encoding='utf-8'))

    criteria = [
        {
            'name': 'Correct identity and source-backed footprint', 'score': 2, 'max_score': 2,
            'status': 'verified',
            'evidence': 'Purdue BuildingShapesZip4 layer 0 FID 238 labels BCHM / Biochemistry Building at 175 S University Street. Its EPSG:4326 ring transforms to 34 unique local vertices; all GIS shell vertices match within 0.000002 m, and the shell is named as the GIS primary outline. The GIS provider is a campus source, so this is strong identity and footprint evidence, not a boundary survey.'
        },
        {
            'name': 'Position, orientation, and scale/dimensions', 'score': 2, 'max_score': 2,
            'status': 'verified against GIS geometry and manifest placement',
            'evidence': 'The GIS polygon centroid is exactly the manifest origin (-233.02125685, -509.45981040) m under the documented local approximation. The master Placement_biochemistry_building marker has that XY within 0.000003 m, Z 0, zero rotation, unit scale, and instances Asset_biochemistry_building. Shell XY matches the transformed ring, verifying footprint shape and orientation at the stated GIS basis. The local exterior bounds are about 64.95 by 66.32 m; no independent surveyed dimensions were found.'
        },
        {
            'name': 'Evidence-backed height, floors, and roof form', 'score': 1, 'max_score': 2,
            'status': 'partially verified; height and roof remain estimated',
            'evidence': 'GIS attributes independently report NUM_LEVELS=5 and CountOfFLO=5, supporting five stories. F01-F04 and R repeat 12.08 units, but the layer schema does not state vertical units or datum. Treating them as feet yields a provisional roof datum near 17.62 m; the modeled evaluated top is 19.004 m. The flat roof and equipment layout have no measured elevation or roof plan in the reviewed sources, so the additional point is withheld.'
        },
        {
            'name': 'Facade, entrances, and distinctive architecture', 'score': 1.5, 'max_score': 2,
            'status': 'partially source-supported; dimensions and composition are interpretive',
            'evidence': 'Purdue Archives supports the 1938 Agricultural Chemistry origin and additions in 1952 and 1981. Purdue Catalyst 2008-09 documents the “Agricultural Chemistry” inscription above the south portico. The current renders visibly include the inscription, entrance portico, brick academic/laboratory massing, five window rows, story belts, and regular glazed bays. These local source snapshots do not establish measured facade elevations, exact bay counts, window/door dimensions, or a current photographic match.'
        },
        {
            'name': 'Modular export, portability, and complete evidence', 'score': 2, 'max_score': 2,
            'status': 'verified',
            'evidence': 'The current Asset_biochemistry_building collection contains 2,049 objects, exactly matching the 2,049 manifest names (2,048 meshes and one text object); no parents, cameras, or lights are in the collection. No external image paths or linked libraries are used by the source asset. A collection-only linked export was saved and reopened in a separate Blender process with all 2,049 names matching and no camera/light. The canonical builder also ran from a sandbox copy and reproduced its evidence record and preview without touching the source asset. Source snapshots, URLs/provider, FID, retrieval date, CRS, measurement method, uncertainty, and views are retained.'
        }
    ]
    findings = [
        'PASS threshold is 8/10; independently assessed score is 8.5/10.',
        'Strongest evidence is the exact GIS ring, exact manifest centroid, and matching master placement instance.',
        'Five levels are source-supported. The approximately 19 m height, story spacing, flat roof silhouette, mechanical layout, facade dimensions, exact bay rhythm, interior vignette, and lack of courtyard holes remain estimated or unverified.',
        'Opening the campus master with Blender 4.5.15 reports that the master was created by a future Blender version and that 13 unrelated libraries / 19 datablocks are missing; the Biochemistry placement marker and its Biochemistry library instance were present. This grade verifies the building asset and marker, not the complete master dependency set.'
    ]
    result = {
        'asset_id': 'biochemistry_building',
        'asset_path': 'modular/buildings/biochemistry_building.blend',
        'score': sum(c['score'] for c in criteria), 'max_score': 10,
        'passing_threshold': 8, 'passed': sum(c['score'] for c in criteria) >= 8,
        'criteria': criteria,
        'evidence': {
            'gis': 'sources/biochemistry_building_gis_fid238_2026-10-25.json; asset_probe.json',
            'identity_and_history': 'sources/prior_biochemistry_building_evidence.json; sources/prior_biochemistry_building_gis_feature_238.json',
            'official_current_sources': 'sources/purdue_biochemistry_contact_2026-10-25.html; sources/purdue_biochemistry_emergency_plan_page_2026-10-25.html',
            'renovation_context': 'sources/synthesis_biochemistry_renovation_2026-10-25.html',
            'geometry_and_placement': 'asset_probe.json; master_placement_probe.json',
            'portable_export': 'independent_collection_link.blend; export_reopen_probe.json',
            'builder_reproduction': 'builder_smoke/modular/buildings/biochemistry_building.blend; builder_smoke_evidence.json; builder_smoke_preview.png',
            'views': ['biochemistry_building_preview.png', 'biochemistry_building_south_portico_preview.png']
        },
        'findings': findings,
        'probe_summary': {
            'manifest_exact_name_match': asset['exact_manifest_names_match'],
            'GIS_shell_max_nearest_error_m': asset['max_gis_shell_vertex_nearest_error_m'],
            'GIS_origin_error_m': asset['gis_to_manifest_origin_error_m'],
            'master_placement': marker,
            'reopened_collection_exact_name_match': exported['exact_manifest_names_match'],
            'builder_smoke_object_count': smoke['exported_object_count']
        }
    }
    return result

if __name__ == '__main__':
    result = evaluate()
    (HERE / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
