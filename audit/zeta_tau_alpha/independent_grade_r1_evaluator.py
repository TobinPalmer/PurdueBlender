import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FOLDER=Path(__file__).resolve().parent
ASSET=ROOT/'modular'/'buildings'/'zeta_tau_alpha.blend'
EXPECTED='795eef2993264674747768df2bd29ff6bdef3ff7ab48d33299c03060691b67d6'

def evaluate():
    sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if sha!=EXPECTED: raise RuntimeError('Frozen candidate changed: '+sha)
    m=json.loads((FOLDER/'independent_grade_r1_metrics.json').read_text(encoding='utf-8'))
    e=json.loads((FOLDER/'independent_grade_r1_extract.json').read_text(encoding='utf-8'))
    v=json.loads((FOLDER/'reopen_validation.json').read_text(encoding='utf-8'))
    master=json.loads((FOLDER/'independent_grade_r1_master_check.json').read_text(encoding='utf-8'))
    fid=m['source_fid']; sname=m['source_name']; addr=m['source_address']
    iou=m['footprint_iou']; srcarea=m['source_polygon_area_m2']; modarea=m['model_shell_base_area_m2']; cerror=m['centroid_error_m']
    origin=e['asset_custom_properties']['placement_origin_xy_m']; msha=master['master_sha256']
    z0=e['shell_z_bounds'][0]; z1=e['shell_z_bounds'][1]; zmax=e['world_bounds_xyz'][2][1]
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'evidence':('Purdue ArcGIS feature FID {} names {} at {} (SOZTA). I independently transformed the raw EPSG:3857 ring and reconstructed the shell base ring from saved mesh side faces. IoU={:.9f}; area {:.3f} vs {:.3f} m2; centroid error {:.8f} m. This establishes exact transfer of the public GIS ring, not surveyed wall accuracy.').format(fid,sname,addr,iou,srcarea,modarea,cerror)},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.5,'max_score':2.0,
       'evidence':('The local shell bounds reproduce the transformed GIS ring within sub-millimeter rounding; the asset records placement origin {} m, independently matching the source-ring centroid. The current master reopen ({}) contains only the old direct massing object named Zeta Tau Alpha; there is no detailed placement marker or instance for this candidate, so its final campus placement/orientation in master has not yet been verified.').format(origin,msha)},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.25,'max_score':2.0,
       'evidence':('Saved shell vertical span is {:.2f}-{:.2f} m and the complete asset maximum is {:.2f} m. GIS Extrution is 12, but GIS NUM_LEVELS and CountOfFLO both read 1 and the field semantics/units are not documented. The build report says about 12.5 m although this exact file reaches 11.91 m. Official 2022 imagery supports a pitched dark roof and roof silhouette, but no measured elevation or floor plan was found; the three interior plates are schematic.').format(z0,z1,zmax)},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.35,'max_score':2.0,
       'evidence':'The model visibly reproduces the red-brick shell, light trim, central white columned portico and pediment, hipped dark roof, dormers, and window rhythm visible in the official ZTA chapter-house photograph. The front review render does not show the distinctive ZTA mark seen on the source pediment. The saved FONT object has body ZTA but its world Y bounds (18.661-18.685 m) sit about 0.6 m behind the pediment outward face at Y about 19.27 m, so it is occluded. Windows are layered over a continuous shell rather than openings; facade proportions/details are approximate.'},
      {'criterion':'Modular export, portability, and evidence','score':1.8,'max_score':2.0,
       'evidence':('Blender 5.2.3 fresh-process reopen passed for exact SHA {}: stable scene/collection present, {} exported objects ({} meshes), {} named materials, all meshes have material assignments, no broken images, and all four brick texture maps are packed. The asset is isolated from the master and its source record documents CRS, feature, sources, transformation, and limitations. The three-floor interior is only schematic and not based on floor plans; windows do not permit normal exterior views into it.').format(sha,v['object_count'],v['mesh_count'],v['material_count'])}
    ]
    total=round(sum(c['score'] for c in criteria),2)
    return {'score':total,'max_score':10,'passing_threshold':8.0,'passes':total>=8.0,
      'building':'Zeta Tau Alpha (Alpha Theta)','asset_file':'modular/buildings/zeta_tau_alpha.blend',
      'asset_id':'massing_zeta_tau_alpha_af8a443','export_collection':v['export_collection'],
      'reviewed_sha256':sha,'review_date':'2026-10-26','blender_version':'5.2.3 LTS',
      'criteria':criteria,'evidence':{
        'fresh_reopen':'audit/zeta_tau_alpha/reopen_validation.json',
        'independent_mesh_extract':'audit/zeta_tau_alpha/independent_grade_r1_extract.json',
        'independent_gis_metrics':'audit/zeta_tau_alpha/independent_grade_r1_metrics.json',
        'read_only_master_check':'audit/zeta_tau_alpha/independent_grade_r1_master_check.json',
        'render':'audit/zeta_tau_alpha/candidate_front_review.png',
        'official_reference_photo':'audit/zeta_tau_alpha/official_2022_centennial_house_photo.jpg',
        'raw_gis':'audit/zeta_tau_alpha/gis_fid773_raw.json','gis_metadata':'audit/zeta_tau_alpha/gis_layer_metadata.json'},
      'sources':[
        {'title':'Purdue ArcGIS BuildingShapesZip4 FID 773','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/773?f=pjson'},
        {'title':'Purdue ArcGIS BuildingShapesZip4 layer metadata','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson'},
        {'title':'Zeta Tau Alpha: Alpha Theta celebrates 101 years at Purdue','url':'https://zetataualpha.org/news/alpha-theta-celebrates-101-years-at-purdue'},
        {'title':'Google Maps: 118 Waldron St, West Lafayette','url':'https://www.google.com/maps/place/118+Waldron+St,+West+Lafayette,+IN+47906'}],
      'findings':[
        'Move the raised ZTA lettering and backing plaque onto the outward-facing side of the pediment; rerender to confirm the mark is legible.',
        'Reconcile the 12.5 m height statement with the exact file maximum of 11.91 m; keep it explicitly estimated unless measured elevation evidence is added.',
        'Before acceptance/integration, have the coordinator replace the old direct massing link with the detailed library and verify its new placement marker against the saved campus origin and facade orientation.',
        'Keep the interior explicitly schematic; if more fidelity is required, add documented room partitions/bathrooms and produce an interior cutaway. No measured floor plan was found.'
      ],
      'limitations':[
        'Purdue GIS polygon is a mapped footprint rather than a surveyed structural wall line; near-perfect IoU only verifies faithful transfer of that ring.',
        'The Google Maps Street View page was not independently accessible through the page reader; the 2026 image date/view direction is taken from the builder record. The facade comparison here uses the archived official 2022 photo.',
        'Master integration is pending; the candidate has not been graded as an installed campus instance.'
      ]}

result=evaluate()
m=json.loads((FOLDER/'independent_grade_r1_metrics.json').read_text(encoding='utf-8'))
e=json.loads((FOLDER/'independent_grade_r1_extract.json').read_text(encoding='utf-8'))
(FOLDER/'independent_grade_r1.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
lines=['# Independent Zeta Tau Alpha R1 Grade','',
 '**Score: {:.2f}/10 -- {} the 8.0 threshold**'.format(result['score'],'passes' if result['passes'] else 'below'),
 '**Exact reviewed SHA-256:** `{}`  '.format(result['reviewed_sha256']),
 '**Fresh reopen:** Blender 5.2.3 LTS','**Review date:** 2026-10-26','','## Scorecard','',
 '| Criterion | Score | Independent evidence |','|---|---:|---|']
for c in result['criteria']:
    lines.append('| {} | {:.2f}/{:.2f} | {} |'.format(c['criterion'],c['score'],c['max_score'],c['evidence']))
lines += ['', '**Total: {:.2f}/10. {} (required 8.0).**'.format(result['score'],'Pass' if result['passes'] else 'Fail'), '', '## Main findings','']
for f in result['findings']: lines.append('- '+f)
lines += ['', '## Independent measurements','',
 '- FID {} is {} at {}; layer metadata confirms Web Mercator WKID 102100/latest 3857.'.format(m['source_fid'],m['source_name'],m['source_address']),
 '- Source/model base area: {:.6f}/{:.6f} m2; independently computed IoU {:.9f}.'.format(m['source_polygon_area_m2'],m['model_shell_base_area_m2'],m['footprint_iou']),
 '- Symmetric mean/P95/Hausdorff boundary residuals: {:.6f}/{:.6f}/{:.6f} m. These tiny values reflect the shell use of the public GIS ring and are not survey evidence.'.format(m['symmetric_boundary_mean_m'],m['symmetric_boundary_p95_m'],m['symmetric_boundary_hausdorff_m']),
 '- Candidate local origin metadata: {} m. No detailed placement marker exists in the current master; it still contains one direct massing object named `Zeta Tau Alpha`.'.format(e['asset_custom_properties']['placement_origin_xy_m']),
 '- Exact file maximum asset Z is {:.3f} m, while its build report says about 12.5 m. GIS Extrution=12 is suggestive but is not documented as a measured elevation.'.format(e['world_bounds_xyz'][2][1]),
 '- Four brick PBR images are packed. Remaining materials are procedural/simple nodes; export opens without external image dependencies.',
 '- Interior contains three schematic floor plates, repeated dining/lounge furniture, bedrooms on upper levels, and stair treads. It has no measured partitions or bathrooms, and windows are overlays, so normal views do not expose the interior.',
 '', '## Sources','']
for s in result['sources']: lines.append('- [{}]({})'.format(s['title'],s['url']))
lines += ['', '## Evidence files','',
 '- `independent_grade_r1_evaluator.py` -- runnable evaluator function returning score, criteria, evidence, and findings.',
 '- `independent_grade_r1.json` -- machine-readable result.',
 '- `independent_grade_r1_extract.json` and `independent_grade_r1_metrics.json` -- fresh Blender extraction and independent GIS comparison.',
 '- `independent_grade_r1_master_check.json` -- read-only master inspection.',
 '- `candidate_front_review.png` and `official_2022_centennial_house_photo.jpg` -- compared views.',
 '', '## Limitations','']
for x in result['limitations']: lines.append('- '+x)
(FOLDER/'independent_grade_r1.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'score':result['score'],'passes':result['passes'],'sha':result['reviewed_sha256'],'criteria':[(c['criterion'],c['score']) for c in result['criteria']]},indent=2))



