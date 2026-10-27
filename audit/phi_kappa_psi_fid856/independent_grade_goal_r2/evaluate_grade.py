from pathlib import Path
import json, hashlib

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
AUDIT = ROOT / 'audit' / 'phi_kappa_psi_fid856'
OUT = AUDIT / 'independent_grade_goal_r2'
ASSET = ROOT / 'modular' / 'buildings' / 'phi_kappa_psi_fid856.blend'
EXPECTED = '70ebe6333250a2266005ca6d72983a7dbd709ed187ee82a96642099e7e4c5ba9'

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

inspection=json.loads((OUT/'fresh_open_inspection.json').read_text(encoding='utf-8'))
crosswalk=json.loads((AUDIT/'gis_crosswalk.json').read_text(encoding='utf-8'))
source_register=json.loads((AUDIT/'source_register.json').read_text(encoding='utf-8'))
asset_hash_before=sha256(ASSET)
assert asset_hash_before==EXPECTED, f'Unexpected pre-grade SHA-256: {asset_hash_before}'
assert inspection['sha256']==EXPECTED
assert inspection['scene']=='Building_phi_kappa_psi_fid856'
assert inspection['collection']=='Asset_phi_kappa_psi_fid856'
assert inspection['collection_object_count']==969
assert not inspection['external_images']
# Independent grading judgments based on source-record inspection and visual comparison of saved renders/photos.
criteria=[
 {'name':'Identity and source crosswalk','score':9.5,'max_score':10,'weight_percent':5,
  'assessment':'Current Indiana Delta contact and the 2010 national magazine independently identify 1307 Tower Drive; Purdue FID 856 carries the exact address and Greek owner but stale Phi Kappa Tau name.'},
 {'name':'Structural footprint and local placement','score':9.2,'max_score':10,'weight_percent':20,
  'assessment':'The asset includes the FID 856 structural wall ring in its documented local centroid frame. Source outline area is 421.96 m² and dimensions about 34.74 × 28.28 m. The nearby OSM outline is correctly treated as broader roof/eave extent, not substituted as the wall ring.'},
 {'name':'Overall massing and roof silhouette','score':8.3,'max_score':10,'weight_percent':20,
  'assessment':'The front Georgian composition and broad pitched roof read clearly. The rear now has the projecting central bay, raised cross-gable and roof stack seen in contractor photo 3. Exact roof pitch, story count and stack height remain photo-based estimates; model top is about 18.15 m above local datum versus legacy GIS extrusion near 53 ft.'},
 {'name':'Facade composition and architectural detail','score':8.5,'max_score':10,'weight_percent':20,
  'assessment':'Front portico, central pediment and ΦΚΨ mark, balcony, brick wings, repeated window courses, pale trim, projecting rear bay, paired upper openings and lower windows are source-consistent. Fine service features, downspouts and detailed roof intersections remain generalized.'},
 {'name':'Materials and texture','score':8.1,'max_score':10,'weight_percent':15,
  'assessment':'Procedural running-bond brick and varied dark roof material render coherently with pale trim. Contractor references are monochrome, so red-brown brick color remains plausible rather than directly verified.'},
 {'name':'Interior','score':7.4,'max_score':10,'weight_percent':15,
  'assessment':'The cutaway now conveys the photographed lounge/common room and adjacent stair hall: defined walls and arched opening, extended stair/landing/guard, upper schematic room divisions, shelves, seating, and dining/coffee tables. The furniture and circulation broadly match photos 5–6, but the plan, dimensions and upper layout are schematic; the image composition has some clutter/occlusion.'},
 {'name':'Asset integrity and portability','score':10.0,'max_score':10,'weight_percent':5,
  'assessment':'Fresh-open in Blender 5.2.3 succeeded. Expected scene/collection, 969 objects and no external image dependencies were independently confirmed.'}
]
score=sum(c['score']*c['weight_percent']/100 for c in criteria)
asset_hash_after=sha256(ASSET)
assert asset_hash_after==EXPECTED, f'Asset changed during grading: {asset_hash_after}'
assert asset_hash_after==asset_hash_before
result={
 'building':'Phi Kappa Psi / Indiana Delta',
 'asset':'modular/buildings/phi_kappa_psi_fid856.blend',
 'sha256':asset_hash_before,
 'score':round(score,2), 'max_score':10,
 'weighted_score_unrounded':round(score,4),
 'status':'ACCEPT' if score>=8 else 'REVISE',
 'criteria':criteria,
 'evidence':[
  {'type':'fresh_open','path':'independent_grade_goal_r2/fresh_open_inspection.json','summary':'Blender 5.2.3 independently opened the exact SHA; expected scene/collection; 969 objects; bounds X[-17.802,17.774], Y[-14.614,15.169], Z[-0.520,18.150] m; no external images.'},
  {'type':'geospatial','path':'audit/phi_kappa_psi_fid856/gis_crosswalk.json','summary':f"FID 856 polygon: {crosswalk['gis_area_m2']:.2f} m², approx 34.74 × 28.28 m; EPSG:3857 inverse Web Mercator followed by repository local conversion."},
  {'type':'identity_and_sources','path':'audit/phi_kappa_psi_fid856/evidence.md','summary':'Official chapter contact page, national magazine evidence, Purdue GIS FID 856 and preserved contractor gallery record source identity and ambiguities.'},
  {'type':'visual_references','paths':['audit/phi_kappa_psi_fid856/sources/contractor_photos/photo_1.jpg','audit/phi_kappa_psi_fid856/sources/contractor_photos/photo_3.jpg','audit/phi_kappa_psi_fid856/sources/contractor_photos/photo_5.jpg','audit/phi_kappa_psi_fid856/sources/contractor_photos/photo_6.jpg'],'summary':'Compared front, rear, lounge, and stair/lobby against corresponding asset renders in audit/phi_kappa_psi_fid856/renders/.'},
  {'type':'post_grade_integrity','sha256_before':asset_hash_before,'sha256_after':asset_hash_after,'unchanged':True}
 ],
 'findings':[
  {'severity':'positive','finding':'The previously missing rear central projection, window rhythm, cross-gable/shingle infill and roof stack have been modeled and are legible in the rear render.'},
  {'severity':'positive','finding':'The interior revision adds recognizable walls, room boundaries, stair circulation, a landing/guard, and lounge furnishings supported by contractor photos 5–6.'},
  {'severity':'limitation','finding':'Interior plan, room dimensions, furnishing placement, exact vertical story interpretation, and roof/stack heights remain estimated or schematic because no architectural plan or surveyed elevation is available.'},
  {'severity':'limitation','finding':'The GIS identity attribute conflicts with current chapter evidence (FID 856 says Phi Kappa Tau; address and owner agree with Phi Kappa Psi). The model’s top is above the legacy GIS 53 ft extrusion; the height conflict remains unresolved.'},
  {'severity':'limitation','finding':'Contractor photographs establish major forms but do not state capture dates; their grayscale appearance does not verify brick hue.'}
 ],
 'remaining_fixes_if_below_8':[] if score>=8 else [
  'Resolve the 53 ft GIS extrusion versus the modeled 18.15 m top with surveyed or reliable elevation evidence.',
  'Obtain a plan or additional interior photographs to improve and validate the schematic room layout and stair/floor connections.',
  'Refine roof intersections and smaller service details using clearer dated elevation references.'
 ]
}
(OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=[
 '# Independent grade: Phi Kappa Psi / Indiana Delta',
 '',f"**Result: {result['score']:.2f}/{result['max_score']} — {result['status']}.**",
 f'**Asset SHA-256:** `{asset_hash_before}`.',
 '**Method:** Opened the exact `.blend` in a separate Blender 5.2.3 background process, checked its expected scene/collection and evaluated inventory, then visually compared its saved exterior/interior renders with preserved GIS, chapter, and contractor sources. The asset hash was checked before and after grading.',
 '', '## Criteria', '', '| Criterion | Score | Weight |', '| --- | ---: | ---: |'
]
for c in criteria: lines.append(f"| {c['name']} | {c['score']:.1f}/10 | {c['weight_percent']}% |")
lines+=['',f"Weighted result: **{score:.2f}/10**.",'','## Findings','']
for f in result['findings']: lines.append(f"- **{f['severity'].title()}:** {f['finding']}")
lines+=['','## Evidence reviewed','',
 '- Fresh-open inspection: `fresh_open_inspection.json`; expected scene and collection, 969 objects, local bounds, no external image dependencies.',
 '- GIS/source crosswalk: `../gis_crosswalk.json`, `../evidence.md`, and `../source_register.json`.',
 '- Contractor photos 1, 3, 5, 6 and saved front/rear/lounge cutaway renders.',
 '', 'The asset SHA-256 is unchanged by grading. No asset, builder, shared index, master, or commit was modified.']
(OUT/'grade_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'score':result['score'],'max_score':result['max_score'],'status':result['status'],'criteria':criteria,'sha256_before':asset_hash_before,'sha256_after':asset_hash_after,'output':str(OUT/'result.json')},indent=2))
