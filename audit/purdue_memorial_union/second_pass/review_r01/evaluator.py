"""Independent exterior assessment of PMU r01; visual evidence, not mesh density.

The awarded points below are the reviewer's documented visual judgments. The
function validates the fixed rubric, sums awards, and applies score AND gates.
It never modifies the asset or manufactures acceptance from geometry counts.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
ASSET=ROOT/'modular/buildings/purdue_memorial_union.blend'
EXPECTED='65f7a027c6b9ecf7e53b6d4706e83c850db2276a53f8baaa9f8d351cc8214533'

def evaluate():
    reopen=json.loads((HERE/'fresh_reopen.json').read_text())
    actual=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    assert actual==EXPECTED==reopen['asset_sha256'], 'Saved revision changed; re-review required'
    criteria=[
        dict(id='windows',maximum=3.0,awarded=.9,
             citations=['S1','S2','S3','S4','M1','M2','M3','M4','M9'],
             deductions=['North, east and west are largely blind walls; S4 directly shows tall north opening groups absent from M2.',
                         'South visible five-bay run is represented, but cardinal/terminal registration and opposing-wing counts are unresolved.',
                         'Tower middle/upper small-light tiers, recessed panels and curved central tracery differ; lower door assemblies use repetitive horizontal grids.']),
        dict(id='signature_architecture',maximum=2.5,awarded=1.1,
             citations=['S1','S2','S3','M1','M5','M6','M9'],
             deductions=['Four mostly opaque entry leaves with individual glazed upper panels have become one visually glazed grid.',
                         'Nested curved tracery, carved corbels, surround profiles and relief carving remain schematic.',
                         'Frontal entry apron reads as a tall blank block rather than the photographed exposed stairs; gabled terminal registration remains provisional.']),
        dict(id='massing_roof',maximum=2.0,awarded=1.15,
             citations=['S4','S5','S6','M5','M6','M7','M8','M10','G1'],
             deductions=['Current inventory wall ring is retained and the tower/flat-vs-slate distinction is present, but the broad central plate lacks the roof articulation/services visible in S5.',
                         'North pitched roof/dormers visible in S4 are missing from r01.',
                         'Regional cloud distributions constrain investigation but do not certify chosen eaves/ridges or uniform wall heights.']),
        dict(id='materials_depth',maximum=1.5,awarded=.95,
             citations=['S1','S2','S3','M1','M3','M4','M9'],
             deductions=['Warm brick/cream stone/dark glazing/charcoal roof families are plausible, but slate lacks photographed coursing and ornate trim depth is simplified.',
                         'East/west base strips have dark coincident patches; base strips offset only in Y remain coplanar on X-facing brick walls.',
                         'Uncalibrated photographs and non-matched lighting do not establish exact colors.']),
        dict(id='whole_building',maximum=1.0,awarded=.15,
             citations=['S1','S4','S5','M1','M2','M3','M4','M5','M6','M10'],
             deductions=['Front is articulated while three other elevations are largely blank, so fidelity is not consistent around the building.',
                         'Original top and entry render framing clipped important geometry; reviewer supplied uncropped replacements.',
                         'Current inner/service coverage and complete matched-view schedules remain inadequate.'])
    ]
    assert [c['maximum'] for c in criteria]==[3,2.5,2,1.5,1]
    assert all(0<=c['awarded']<=c['maximum'] for c in criteria)
    gates={
        'correct_identity':dict(passed=True,basis='FID644, PMU collection, south tower/wing identity and stable asset path inspected.'),
        'adequate_exterior_reference_coverage':dict(passed=False,basis='Current north/service/inner and complete flank schedules missing; 2009 north view adds concrete discrepancy evidence, not current full coverage.'),
        'no_unresolved_material_exterior_discrepancies':dict(passed=False,basis='Blind elevations, door/tracery/stone-step discrepancies, missing north roof and coplanar base artifacts remain.'),
        'saved_file_reopen':dict(passed=True,basis='Independent Blender 5.2.3 reopen and pre/post-render SHA256 confirm exact r01.'),
        'expected_collection_export':dict(passed=reopen['expected_collection'],basis='Asset_purdue_memorial_union present; identity root; hidden first-pass interior child retained.'),
        'portable_dependencies':dict(passed=not reopen['external_unpacked_images'] and not reopen['libraries'],basis='No external libraries or unpacked file-image dependencies on fresh reopen.'),
        'no_regression_to_verified_footprint_orientation_scale':dict(passed=reopen['root_identity'] and reopen['unit_scale']==1 and reopen['inventory_wall_first_vertex_max_xy_error_m']<.001,basis='262 wall first vertices independently compared to FID644 project conversion, max XY error 2.1493e-6 m; identity root/metre scale. This verifies source registration, not survey truth or vertical dimensions.'),
        'master_integration':dict(passed=False,basis='Separate Tobin-owned gate; not performed or claimed by this reviewer.')
    }
    evidence={
        'S1':'audit/purdue_memorial_union_refine/official_centenary_exterior_2024.jpg — Purdue 2024 front photo',
        'S2':'research/second_pass/buildings/purdue_memorial_union/sources/rea_main.jpg — REA/Hadley Fruits south terrace/frontage',
        'S3':'research/second_pass/buildings/purdue_memorial_union/sources/rea_gallery2.jpg and rea_gallery13.jpg — opposing terrace/terminal obliques',
        'S4':'research/second_pass/buildings/purdue_memorial_union/sources/maps_north_2009.png and .txt — Google June2009 north view, historical condition',
        'S5':'research/second_pass/buildings/purdue_memorial_union/sources/aerial_world_imagery.png — north-up overhead, exposure date unknown',
        'S6':'research/second_pass/buildings/purdue_memorial_union/sources/lidar_regions.json — 2018 unclassified-return regional distributions, not fitted planes',
        'G1':'audit/purdue_memorial_union/second_pass/review_r01/fresh_reopen.json — independent saved-file and wall-registration measurements'
    }
    for number,name in enumerate(['south','north','east','west','southwest','southeast','roof','entry'],1):
        evidence['M'+str(number)]='audit/purdue_memorial_union/second_pass/revision_r01/'+name+'.png'
    evidence['M9']='audit/purdue_memorial_union/second_pass/review_r01/entry.png — independent uncropped tower/entry view'
    evidence['M10']='audit/purdue_memorial_union/second_pass/review_r01/roof.png — independent full top view'
    score=sum(c['awarded'] for c in criteria)
    visual_gates=[g for name,g in gates.items() if name!='master_integration']
    return dict(building_id='purdue_memorial_union',revision='r01',asset_path='modular/buildings/purdue_memorial_union.blend',asset_sha256=actual,reviewer='/root/pmu_exterior_review',reviewed_at=datetime.now(timezone.utc).isoformat(),score=score,max_score=10,criteria=criteria,evidence=evidence,reviewed_views=[evidence['M'+str(i)] for i in range(1,11)],findings=[
        dict(id='F1',face='North/east/west',required_correction='Research and model actual openings, doors, trim and roof changes. Prioritize clearly observed north groups/pitched roof in S4; do not invent grids for unresolved faces.'),
        dict(id='F2',face='South tower/entry',required_correction='Match the four solid door-leaf lower panels/upper glass, separate small-light upper rows, rising curved tracery, recessed stone panels and carved surround/relief depth.'),
        dict(id='F3',face='South approach',required_correction='Remove the tall frontal apron obstruction and expose stepped approach/rails consistent with source photographs and plan classification.'),
        dict(id='F4',face='East/west base',required_correction='Offset base strips along each edge outward normal and give supported wall/trim thickness; eliminate coplanar overlap and re-render grazing angles.'),
        dict(id='F5',face='Roof/all elevations',required_correction='Register roof masses/voids and verify north pitched roof/dormers; add evidence-supported membrane/slate transitions and preserve unknown equipment instead of a generic plate.'),
        dict(id='F6',face='Review evidence',required_correction='Use full roof framing and unclipped entry detail, and provide cardinal registration/complete per-face opening schedules and matched source/model views.')
    ],uncertainties=['Current north condition beyond dated 2009 photo','Current inner/service elevations and hotel-interface details','Exact facade/terminal registration and full opposing-wing counts','Survey eave/ridge heights, roof profiles and equipment','Fine sculptural relief and calibrated material finishes','Hidden prior interior remains unreviewed and is excluded from exterior point awards'],gates=gates,acceptance_threshold=9.9,threshold_approval=None,accepted=score>=9.9 and all(g['passed'] for g in visual_gates))

if __name__=='__main__':
    result=evaluate();(HERE/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'score':result['score'],'accepted':result['accepted'],'asset_sha256':result['asset_sha256']},indent=2))
