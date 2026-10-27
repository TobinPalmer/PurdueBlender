"""Fresh r2 review; reuses r1's neutral reopen/geometric extraction, replaces all assessments."""
import bpy
import json
import importlib.util
import sys
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def evaluate():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('hort_r1_metrics', OUT.parent/'independent_grade_r1/evaluate_horticulture.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.evaluate()  # Reopens the frozen current .blend and independently measures it.
    asset = bpy.data.collections['Asset_horticulture_building']
    shell = bpy.data.objects['HORT structural shell | official GIS FID 232 outline']
    ring = [(shell.matrix_world @ v.co) for v in shell.data.vertices if abs(v.co.z)<0.00001]
    edge_index = int(asset['photo_elevation_edge_index'])
    a,b = ring[edge_index], ring[(edge_index+1)%len(ring)]
    tangent = (b-a).normalized()
    outward = Vector((tangent.y,-tangent.x,0))
    rows = {}
    for face in bpy.data.objects['Historic sash windows | glazing'].data.polygons:
        center = face.center
        offset = (center-a).dot(outward)
        if abs(offset-0.095)<0.002:
            z = round(center.z, 3)
            rows.setdefault(str(z), []).append(round((center-a).dot(tangent),3))
    report['reviewer'] = 'independent grader r2'
    report['evidence']['photo_edge_outward_normal_xy'] = list(outward)[:2]
    report['evidence']['photo_edge_length_m'] = (b-a).length
    report['evidence']['principal_facade_windows_by_center_height_and_distance_along_edge_m'] = rows
    report['evidence']['height_range_m'] = list(asset['height_range_m'])
    report['evidence']['direct_visual_review'] = {
        'sources_inspected':'Raw Purdue Events photo, official north-up campus map HORT crop, saved Agriculture Mall article paragraph and BuildingShapes metadata inspected directly; r1 report reread.',
        'map_context':'Map shows HORT east of NLSN and south of Agricultural Mall. Article says green strips between west Whistler/Nelson and east Horticulture/Forestry. This supports a west-facing facade inference, but photo vegetation alone cannot uniquely register exact side/door.',
        'improvements':'Tall dark sash, grouped pairs, shallow pilasters, pale base, shallow stone portal and balcony rail now replace uniform square windows/unsupported freestanding canopy. These improve source agreement.',
        'remaining_facade_mismatch':'Source photo clearly has central upper-floor windows above the doorway and flanking singles within grouped bays. Revised exterior has six openings per row and a large blank central strip. Builder omits central window group on every level. Source has more visible flanking openings and denser grouped rhythm. Portal is still narrower/sparser than source; entry render shows inscription extending beyond stone panel and a blank brick gap above door. Brick noise reads mottled plaster rather than coursed brick.',
        'vertical':'Layer JSON esriMeters pertains horizontal spatial reference, not custom vertical fields. F02/F03/R form coherent intervals; conditional feet-based10.69848m is more defensible than former14.63m selection, but nearby airport elevation is no proof. The10.70–14.63 interval is a conditional scenario range, not an independently established confidence bound.',
        'integration':'Master not opened or modified. Main asset geometry and portability measured from reopened saved library.'
    }
    report['criteria'] = [
        {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'status':'verified within source limits','evidence':['Official GIS FID232 identity and14 outline vertices remain correct.','Reopened structural shell and source vertices agree bidirectionally below0.001m.'],'uncertainty':'GIS tolerance/date and wall-versus-eave interpretation unavailable.'},
        {'criterion':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2,'status':'horizontal shell verified; west facade plausible inference','evidence':['Manifest and reopened local origin agree exactly; shell dimensions64.50x41.54m preserve geographic orientation.','North-up campus map and Agriculture Mall article corroborate neighborhood relationship; actual modeled facade points west.'],'deduction':'0.2: exact photo/door geographic registration remains an inference and master/neighbors uninspected.'},
        {'criterion':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2,'status':'three visible levels/flat edge supported; vertical dimension conditional estimate','evidence':['Reopened10.69848m roof derives explicitly fromR35.1 under feet hypothesis, with floors11.7/23.4.','Source photo supports three visible rows and flat corniced roof; field conflicts/units now disclosed.'],'deduction':'0.8: units/semantics not documented and no independent measured height; interval10.70–14.63m conditional, not surveyed. Five-level fields unresolved.'},
        {'criterion':'Facade, entrances, and distinctive architecture','score':1.0,'max_score':2,'status':'improved but conspicuous source-backed omissions remain','evidence':['Tall narrow sash/pairs, pilasters and shallow portal replace r1 square windows/projecting canopy.','Raw source shows central upper-story windows above door; revised render/actual glazing lacks central openings on all levels.','Photo bay grouping has more openings; portal proportions/details and text placement still visibly mismatch.'],'deduction':'1.0: missing central upper windows/denser grouping, oversimplified portal, unsupported hidden elevations and weak masonry articulation.'},
        {'criterion':'Modular export, portability, and complete evidence','score':1.8,'max_score':2,'status':'portable reopened asset; integration pending','evidence':['Expected collection,38 objects, all assigned materials connected, no unpacked external images/linked libraries.','Source GIS/photo/map/article snapshots, dedicated builder, provenance/uncertainty and rendered views available.'],'deduction':'0.2: master link/replacement/context check pending; airport unit plausibility claim lacks raw snapshot; prior detailed asset unavailable for before/after comparison.'}
    ]
    report['findings'] = [
        {'priority':'required','action':'Add photo-visible central sash groups on both upper floors directly above doorway, retain a ground-floor opening only where photo supports it. Match source central single-pair-single group and neighboring group rhythm; current six-per-row leaves a wide unsupported blank wall.'},
        {'priority':'required','action':'Match source portal width relative to door and window group, align its entablature/rail to the second-story opening, close unsupported blank brick gap above door, center/fit HORTICULTURE lettering inside stone block, and show comparable frontal close view.'},
        {'priority':'uncertainty','action':'Retain conditional feet-height estimate and geographic registration caveat until measured/elevation/street-view evidence is available; do not claim interval a verified bound.'},
        {'priority':'handoff','action':'Tobin/coordinator must verify master link once, massing replacement, placement and neighboring context without source grader saving master.'}
    ]
    report['score'] = round(sum(c['score'] for c in report['criteria']),2)
    report['passed'] = report['score']>=8
    return report


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    result = evaluate()
    (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('INDEPENDENT_GRADE',json.dumps({'score':result['score'],'max_score':10,'passed':result['passed']}),flush=True)
