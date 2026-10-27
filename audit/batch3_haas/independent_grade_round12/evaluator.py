from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'modular/buildings/felix_haas_hall.blend'
VALIDATION = ROOT / 'audit/batch3_haas/round12_validation.json'
EVIDENCE = ROOT / 'audit/batch3_haas/round12_evidence.md'
MANIFEST = ROOT / 'modular/manifest.json'
EXPECTED_SHA = '0de3417c6cc3af247b2100242720d39871bc8ed188dcf06bfbb96d9bead2c067'


def evaluate():
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    v = json.loads(VALIDATION.read_text(encoding='utf-8'))
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    record = next(a for a in m['assets'] if a['id'] == 'felix_haas_hall')
    evidence = EVIDENCE.read_text(encoding='utf-8')
    assert sha == EXPECTED_SHA, f'Asset SHA changed: {sha}'
    assert v['reopened'] and v['status'] == 'PASS' and v['asset_sha256'] == sha
    assert v['checks']['roof_plan_bounds_shell_plus_0_25m']
    assert record['object_count'] == v['object_count'] == len(record['objects'])
    assert '2.30 m' in evidence and 'estimate' in evidence.lower() and 'unverified' in evidence.lower()
    # Independently recompute all four roof eave margins from the saved reopen report.
    roof, shell = v['combined_roof_bounds_m'], v['gis_shell_bounds_m']
    margins = [shell[0][0]-roof[0][0], roof[1][0]-shell[1][0],
               shell[0][1]-roof[0][1], roof[1][1]-shell[1][1]]
    assert all(abs(x-0.25) < 0.00001 for x in margins), margins

    criteria = [
      {'name':'identity and source-backed footprint','score':1.8,'max_score':2.0,
       'evidence':'Official Purdue Events and archival sources identify Felix Haas Hall/former Memorial Gymnasium. The unchanged GIS shell bounds are reused from the documented earlier FID comparison; current asset preserves the shell and placement origin.',
       'findings':'Identity and plan-envelope basis are strong. The official exterior photo is qualitative and the R12 evidence does not repeat a pointwise GIS overlay.'},
      {'name':'position, orientation, and dimensions','score':1.8,'max_score':2.0,
       'evidence':f'R12 validation was recomputed against shell bounds: roof margins X−={margins[0]:.6f}, X+={margins[1]:.6f}, Y−={margins[2]:.6f}, Y+={margins[3]:.6f} m. All equal 0.25 m within 1e-5. Placement origin and GIS shell were not changed.',
       'findings':'This corrects R11: the far-X asset bounds belong to entry stair treads/cheek walls, not the roof. Facade bearing and detailed dimensions remain estimates from uncalibrated perspective photography.'},
      {'name':'height, floors, and roof','score':1.4,'max_score':2.0,
       'evidence':'Reopen report gives main roof eaves Z=11.7 m and ridge Z=14.0 m (2.30 m rise); entry roof peak is Z=13.2 m. Official image and 1922 Purdue publication support a red-tile, broad low-pitched roof, not an absolute elevation. Evidence explicitly labels 2.30 m and eaves as estimates; no scaled elevation was found.',
       'findings':'The R12 roof is materially less exaggerated than R11 and the 2.30 m rise is clearly uncertain. Absolute roof/floor heights and upper-storey/floor interpretation remain unverified.'},
      {'name':'facade, entrance, and distinctive architecture','score':1.6,'max_score':2.0,
       'evidence':'Direct comparison of round-12 exterior/entrance renders with the preserved Purdue photo shows the red tile roof, arched central entry, two arched lower openings, segmented pale stone surrounds, masonry palette, and entrance stair retained after roof correction.',
       'findings':'The main photo-supported architectural cues hold. The facades remain simplified/stylized, with opening dimensions, detailing, and unseen elevations estimated; the interior plan is schematic, not a verified interior.'},
      {'name':'modular export, portability, and evidence','score':1.8,'max_score':2.0,
       'evidence':f'Exact saved SHA matched and reopened in Blender {v["blender_version"]}; stable collection `{v["export_collection"]}` contains {v["object_count"]} objects / {v["mesh_count"]} meshes. No external images or material-image nodes. The current manifest now has {record["object_count"]} object entries with the matching bounds/count. Source URLs, uncertainties, and fresh-open renders are recorded.',
       'findings':'The library is portable and the manifest count/bounds now match. Roof-specific geometry is validated; the schematic interior is deliberately not asserted as factual.'}
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    return {'building':'Felix Haas Hall','round':12,'score':score,'max_score':10.0,
      'threshold_8_met':score>=8.0,'asset_path':'modular/buildings/felix_haas_hall.blend',
      'evaluated_sha256':sha,'criteria':criteria,
      'roof_margin_check_m':{'x_minus':margins[0],'x_plus':margins[1],'y_minus':margins[2],'y_plus':margins[3]},
      'evidence_reviewed':['audit/batch3_haas/round12_evidence.md','audit/batch3_haas/round12_validation.json','audit/batch3_haas/exterior_round12.png','audit/batch3_haas/entrance_round12.png','audit/batch3_haas/exterior_reference.jpg','audit/batch3_haas/independent_grade_round11/grade_report.md','modular/manifest.json'],
      'findings':['R12 corrects the prior roof-bound inference: the roof itself is shell + 0.25 m; far-X extents belong to documented entrance components.','The 2.30 m rise is explicitly an estimate and is visually more consistent with the broad, low-pitched source profile than R11.','Arched facade/entry details remain visible and the export is fresh-open verified.','Unmeasured dimensions, absolute heights, unseen elevations, and interior plan remain estimated/schematic.'],
      'priority_fixes':['No further blocker to the 8/10 threshold identified; retain the roof-height and interior uncertainty in shared documentation.'],
      'master_or_asset_edited':False,'independent_grade':True}

if __name__ == '__main__':
    result=evaluate()
    out=Path(__file__).resolve().parent/'result.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'score':result['score'],'threshold_8_met':result['threshold_8_met'],'evaluated_sha256':result['evaluated_sha256'],'roof_margin_check_m':result['roof_margin_check_m'],'result':str(out)},indent=2))
