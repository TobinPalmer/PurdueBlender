"""Independent r3 Horticulture review; saved asset is reopened and never modified."""
import bpy
import json
import sys
import importlib.util
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
EXPECTED_SHA256 = '20aed83e827c75d57c12e7dfc417bc6d1e4ccaebf5336b4e96c6121e13297cb7'


def evaluate():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('hort_r2_metrics', OUT.parent/'independent_grade_r2/evaluate_horticulture.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.evaluate()  # Opens current asset and recomputes all geometry/material metrics.
    assert report['evidence']['asset_sha256'] == EXPECTED_SHA256, 'Frozen candidate changed'
    report['reviewer'] = 'independent grader r3'
    text = bpy.data.objects['West entry | carved HORTICULTURE inscription']
    block = bpy.data.objects['West entry | carved flush entablature']
    n = Vector((*report['evidence']['photo_edge_outward_normal_xy'],0))
    tangent = Vector((-n.y,n.x,0))
    graph = bpy.context.evaluated_depsgraph_get()
    def extent(obj):
        evaluated = obj.evaluated_get(graph)
        pts = [evaluated.matrix_world @ Vector(p) for p in evaluated.bound_box]
        return [min(v.dot(tangent) for v in pts),max(v.dot(tangent) for v in pts)]
    text_extent, block_extent = extent(text),extent(block)
    fits = text_extent[0]>=block_extent[0] and text_extent[1]<=block_extent[1]
    report['evidence']['portal_text_extent_along_facade_m'] = text_extent
    report['evidence']['portal_block_extent_along_facade_m'] = block_extent
    report['evidence']['portal_text_fits_block'] = fits
    assert fits
    rows = report['evidence']['principal_facade_windows_by_center_height_and_distance_along_edge_m']
    report['evidence']['principal_window_count'] = sum(len(v) for v in rows.values())
    assert report['evidence']['principal_window_count'] == 26
    report['evidence']['direct_visual_review'] = {
        'sources_inspected':'Raw Purdue Events Horticulture photo and fresh exterior, entry, top renders inspected directly for r3. Prior r2 source map/article/metadata findings remain applicable and are not upgraded to stronger certainty.',
        'facade_changes_verified':'Previously absent central single-pair-single groups now appear on both upper floors; actual reopened glazing has26 west-facing polygons (6 ground,10 per upper row). Shallow portal/rail sits below central sash group. Inscription centered inside panel; evaluated text bounds fit entablature. Projecting canopy/piers absent. Brick bed joints now visible.',
        'remaining_architectural_limits':'Facade has estimated window spacing and fewer outer flanking singles than shown in cropped source. Central second-row windows are shortened/raised to clear portal whereas photo arrangement is more regular. Source carved portal moldings/base and masonry are simplified; large blank door transom/portal head space remains. Hidden elevations are generalized. These remain deducted rather than represented as accurate measured details.',
        'horizontal_geometry':'Top render and source-corresponding evaluated floor vertices preserve GIS reentrant plan. Manifest origin remains exact. West geographic normal supported; exact photo door registration remains inference.',
        'vertical':'10.69848m roof uses conditional feet interpretation ofR35.1, with10.70–14.63m as scenario range. Units/field semantics and measured height unresolved. Three visible rows/flat cornice supported by photo.',
        'integration':'No master changes or master reopen done by grader; Tobin integration still required.'
    }
    # Same rubric and unchanged deductions for horizontal, vertical, integration.
    # Only the facade score changes after checking the actual r3 improvements.
    report['criteria'][3] = {
        'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2,
        'status':'source-supported principal details substantially represented; dimensions estimated',
        'evidence':[
            'Direct source-versus-r3 render comparison verifies tall sash/pairs, upper central single-pair-single, brick pilasters/base, shallow portal, inscription and rail.',
            'Reopened principal glazing now totals26 openings; blank upper center removed. Text evaluated extent fits stone inscription block.',
            'No unsupported projecting canopy/freestanding portal piers; bed joints improve masonry reading.'
        ],
        'deduction':'0.5: exact bay spacing/count and door/portal proportions simplified, central second-row opening heights differ, unseen elevations generalized without corroborating imagery.'
    }
    report['criteria'][4]['evidence'][0] = 'Expected collection,39 objects, all assigned materials connected, no unpacked external images/linked libraries.'
    report['findings'] = [
        {'priority':'retained uncertainty','action':'Height10.69848m is conditional estimate, not measured;10.70–14.63m is not a verified bound. Retain units/semantics/five-level conflict disclosure.'},
        {'priority':'retained uncertainty','action':'West facade registration and exact door offset are inferred. Principal window/portal dimensions and hidden elevations remain estimated/generalized.'},
        {'priority':'optional refinement','action':'Additional geolocated elevations could resolve outer flanking openings, regular second-row window heights and portal molding/door proportion differences.'},
        {'priority':'integration handoff','action':'Tobin/coordinator must confirm master link once, massing replacement, correct placement and neighbor context; grading pass concerns source asset and disclosed evidence limits.'}
    ]
    report['score'] = round(sum(c['score'] for c in report['criteria']),2)
    report['passed'] = report['score']>=8
    report['grade_scope'] = 'Modular source asset pass with explicit height/facade/integration limitations; not a claim of fully surveyed building accuracy.'
    return report


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    result = evaluate()
    (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('INDEPENDENT_GRADE',json.dumps({'score':result['score'],'max_score':10,'passed':result['passed'],'asset_sha256':result['evidence']['asset_sha256']}),flush=True)
