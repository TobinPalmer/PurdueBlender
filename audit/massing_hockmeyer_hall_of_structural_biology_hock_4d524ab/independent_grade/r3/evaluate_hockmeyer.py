from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / 'audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab'
ASSET = ROOT / 'modular/buildings/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab.blend'


def evaluate() -> dict:
    build = json.loads((AUDIT / 'build_evidence.json').read_text(encoding='utf-8'))
    reopen = json.loads((AUDIT / 'reopen_validation.json').read_text(encoding='utf-8'))
    gis = json.loads((AUDIT / 'sources/purdue_building_shapes_hock.json').read_text(encoding='utf-8-sig'))
    osm = json.loads((AUDIT / 'geometry/gis_osm_footprint_metrics.json').read_text(encoding='utf-8'))
    attrs = gis['features'][0]['attributes']
    render_names = ('hockmeyer_exterior_oblique.png', 'hockmeyer_courtyard_entry.png', 'hockmeyer_roof_plan.png')
    renders = [AUDIT / 'renders' / name for name in render_names]
    photo = AUDIT / 'sources/purdue_hockmeyer_exterior_2009.jpg'
    shell_error = float(reopen['max_source_to_shell_xy_vertex_error_m'])
    iou = float(osm['intersection_over_union'])
    symdiff_pct = float(osm['symmetric_difference_pct_of_union'])
    hausdorff = float(osm['boundary_hausdorff_m'])
    identity_ok = (attrs.get('FID') == build.get('source_feature_id') == 669 and
                   attrs.get('BLDG_ABBR') == 'HOCK' and 'Hockmeyer' in attrs.get('BUILDING_N', ''))
    exact_ring = (reopen.get('ring_vertices_source') == reopen.get('ring_vertices_shell_lower') ==
                  reopen.get('ring_vertices_shell_upper') == 58 and shell_error < 0.001)
    collection_ok = (reopen.get('collection_found') and
                     reopen.get('expected_collection') == build.get('collection') and
                     reopen.get('collection_object_count') == 6)
    renders_ok = all(p.is_file() and p.stat().st_size > 100_000 for p in renders)
    source_bundle_ok = all((AUDIT / rel).is_file() for rel in (
        'sources/purdue_building_shapes_hock.json',
        'sources/purdue_building_shapes_layer_metadata.json',
        'sources/osm_local_map.xml',
        'sources/purdue_news_2009_dedication.html',
        'sources/purdue_hockmeyer_exterior_2009.jpg',
        'sources/purdue_emergency_plan_page.html',
    ))
    deps = reopen.get('external_unpacked_file_dependencies')
    scene_ok = bool(reopen.get('scene_name_matches'))

    criteria = [
        {
            'name': 'Correct identity and source-backed footprint', 'score': 2.0, 'max_score': 2,
            'evidence': [
                f"Purdue BuildingShapes feature FID {attrs.get('FID')} identifies {attrs.get('BUILDING_N')!r}, building code {attrs.get('BLDG_ABBR')}; the saved page and plan snapshots also identify Hockmeyer Hall.",
                f"The reopened asset retains all 58 exterior-ring vertices from that official feature ({exact_ring=}, maximum source-to-shell XY error {shell_error:.6f} m).",
                f"Independent OSM way 283274991 comparison yields IoU {iou*100:.2f}%, symmetric difference {symdiff_pct:.2f}% and boundary Hausdorff {hausdorff:.3f} m. Boundary-to-segment distance fixes the earlier vertex-to-vertex sampling mismatch; Purdue remains the selected primary outline.",
                "The apparent GIS area disagreement is explained by the saved native EPSG:3857 layer metadata and the expected Web Mercator area scale at Purdue latitude; the model follows the feature ring, not the distorted Shape__Area value.",
            ],
            'deduction': None,
        },
        {
            'name': 'Position, orientation, and scale/dimensions', 'score': 1.75, 'max_score': 2,
            'evidence': [
                f"Reopen comparison verifies the full 58-vertex source shell at {shell_error:.6f} m maximum XY error in the repository campus coordinate frame.",
                "The documented project lon/lat-to-local-meter transform is applied to the authoritative Purdue geometry; OSM independently overlaps the outline by 96.28% of the union area.",
                "Footprint alignment and its scale/orientation are strongly evidenced. A survey control network or published dimensioned plan was not found, so this does not establish survey accuracy; residual GIS/OSM boundary Hausdorff is 3.603 m.",
            ],
            'deduction': 'Small deduction because the coordinate fit is source-precise but not tied to independent survey control or dimensioned architectural plans.',
        },
        {
            'name': 'Evidence-backed height, floors, and roof form', 'score': 1.25, 'max_score': 2,
            'evidence': [
                "Purdue Biological Sciences (2010) describes the building as three-story; the current Purdue emergency plan independently supports three occupied floors and also mentions a penthouse and basement.",
                "The asset models three floors, while 11.4 m is explicitly an estimate based on a 3 x 3.8 m floor-to-floor scaffold, not a measurement. GIS vertical fields are undocumented and correctly unused.",
                "The asset has a flat cap. No evidence supports a measured roof silhouette or penthouse size/location; the known penthouse is omitted as a separate block rather than guessed.",
            ],
            'deduction': 'Quantitative height, exact floor heights, detailed roof form, and penthouse geometry remain unverified or estimated.',
        },
        {
            'name': 'Facade, entrances, and distinctive architecture', 'score': 1.5, 'max_score': 2,
            'evidence': [
                "The official 2009 Purdue photo visibly supports red brick, large pale upper opaque panels, and blue-green multi-story glazing around the courtyard/arrival frontage.",
                "The oblique and courtyard renders show these material zones, schematic curtainwall, brick windows and three-level rhythm; the roof-plan render exposes the GIS-derived re-entrant footprint.",
                "The photo and landscape-architecture views are not registered to the GIS ring. Exact facade-edge correspondence, bay rhythm, and doorway location are therefore unverified; no precise entrance is fabricated in the model.",
            ],
            'deduction': 'Major facade materials and glazing are supported, but their compass registration, exact bay layout, and entrance location are not verified.',
        },
        {
            'name': 'Modular export, portability, and complete evidence', 'score': 1.5, 'max_score': 2,
            'evidence': [
                f"Asset file exists ({ASSET.is_file()}); expected collection {build.get('collection')!r} reopens with {reopen.get('collection_object_count')} objects, including the main shell and facade components.",
                f"Direct reopen with Blender {reopen.get('blender_version')} confirms the expected collection, 58 lower/upper shell vertices and no unpacked external dependencies ({deps!r}).",
                f"All three review renders are present and substantial ({renders_ok}); independent GIS, OSM, layer metadata, official photo and Purdue-plan source snapshots are present ({source_bundle_ok}).",
                f"The expected scene ID does not match the Blender 4.5 actual scene ID ({reopen.get('actual_scene_name')!r} vs {reopen.get('expected_scene_name')!r}); the full expected value is preserved in a custom property. This is recorded as a compatibility failure, not a pass.",
            ],
            'deduction': 'The library collection and portable asset pass, but the expected scene-name contract fails on the available Blender 4.5 reopen path.',
        },
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    return {
        'building_id': build['building_id'],
        'asset': ASSET.relative_to(ROOT).as_posix(),
        'evaluator': 'independent Hockmeyer Hall review r3',
        'score': score,
        'max_score': 10,
        'pass_threshold': 8,
        'passed': score >= 8,
        'criteria': criteria,
        'evidence': {
            'build_evidence': 'audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab/build_evidence.json',
            'reopen_validation': 'audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab/reopen_validation.json',
            'gis_osm_comparison': 'audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab/geometry/gis_osm_footprint_metrics.json',
            'visual_review': [p.relative_to(ROOT).as_posix() for p in renders] + [photo.relative_to(ROOT).as_posix()],
            'gis_feature_id': attrs.get('FID'),
            'source_to_shell_xy_vertex_error_m': shell_error,
            'osm_intersection_over_union': iou,
            'osm_symmetric_difference_pct_of_union': symdiff_pct,
            'osm_boundary_hausdorff_m': hausdorff,
            'expected_collection_found': bool(collection_ok),
            'expected_scene_name_matches': scene_ok,
            'external_unpacked_file_dependencies': deps,
            'all_review_renders_present': renders_ok,
            'source_bundle_present': source_bundle_ok,
        },
        'findings': [
            f"{'PASS' if score >= 8 else 'FAIL'} ({score}/10; minimum passing standard 8/10).",
            "The official Purdue 58-vertex shell is an exceptionally close source match; current OSM polygon-to-boundary metrics broadly corroborate it and replace the misleading earlier 16.27 m vertex-to-vertex comparison.",
            "Three occupied floors are source-backed. The 11.4 m height is estimated; penthouse existence is documented, but its shape and location are not evidenced, and detailed roof form remains unresolved.",
            "Facade palette and courtyard glazing match official imagery at a schematic level; facade registration and exact entrance placement remain unknown.",
            "Expected collection reopens and has no external dependencies. Blender 4.5 truncates the expected long scene name; the full value is retained as a custom property but the scene-name contract itself remains failed.",
        ],
    }


if __name__ == '__main__':
    result = evaluate()
    (Path(__file__).with_name('result.json')).write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))
