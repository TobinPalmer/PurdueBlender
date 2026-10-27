import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PROBE=HERE/'fresh_open_probe.json'
EVIDENCE=ROOT/'audit'/'alpha_epsilon_pi'/'evidence.json'
EXPECTED_HASH='de01abd4cb52f856630d11906f7ded9517da6f584a0ea088ce50ebbc1c634763'

def evaluate(probe,evidence):
    score_items={
      'identity_and_source_backed_footprint':{
        'score':1.35,'max_score':2.0,
        'evidence':[
          'The current Purdue BoilerLink chapter profile is cited as listing 1051 David Ross Road.',
          'Purdue GIS FID 754 lists that same address and its polygon overlays a roof in the saved Esri imagery overlay.',
          'The selected footprint is FID 754, whose official GIS BUILDING_N value is Chi Phi, not Alpha Epsilon Pi; current occupancy of this exact roof remains unresolved.',
          'GIS FID 821 is separately labeled Alpha Epsilon Pi at 116 Fowler Ave. and is explicitly not used.'
        ],
        'findings':['Identity crosswalk is supported by address and roof location but not conclusively verified; retain the conflict in all project records.']
      },
      'position_orientation_and_plan_dimensions':{
        'score':2.0,'max_score':2.0,
        'evidence':[
          f"Fresh-open measurement found {probe['foundation_vertex_count']} corresponding GIS/model outline vertices; maximum vertex error is {probe['max_corresponding_vertex_error_m']:.3g} m under the project's documented local tangent transform.",
          f"The exported collection uses the expected local-coordinate frame and centroid placement origin {probe['placement_origin_xy_m']} m.",
          'The measured 60-vertex source ring determines both orientation and plan outline; the GIS-to-model transform preserves that ring rather than fitting an unrelated bounding box.'
        ],
        'findings':['These are high-precision comparisons to the GIS source polygon, not survey-grade verification of GIS accuracy or identity.']
      },
      'evidence_backed_height_floors_and_roof':{
        'score':1.4,'max_score':2.0,
        'evidence':[
          'The saved dated 2009 Purdue AEPi photograph is attributed and depicts the broad three-story brick/mansard-roof character used by the model.',
          'A fresh-open inspection measured walls from Z=0.58 to 9.36 m, lower mansard slope 9.48–11.03 m, upper slope 11.03–12.38 m, plus a chimney to 13.57 m.',
          'The evidence record labels floor heights, roof breaks/cap, chimney and dormer placement as estimates; no measured elevation or current roof survey is supplied.'
        ],
        'findings':['Keep story heights and total building height explicitly estimated. A newer elevation, LiDAR return, or measured roof evidence would improve confidence.']
      },
      'facade_entrances_and_distinctive_architecture':{
        'score':1.15,'max_score':2.0,
        'evidence':[
          'The fresh-open asset contains 30 named facade window fronts, 20 window AC units, 9 dormer glazing objects, an entry portal, and Greek-letter signage.',
          'The 2009 source image supports brick, three visible stories, projecting bay windows, window AC units, Greek letters, and a shingled mansard roof.',
          'In the current exterior preview, the main entrance and broad window rhythm are legible, but the wall shader produces strong vertical streaks that read as siding; the broad roof/multi-wing mass remains weakly checked against current facade imagery.'
        ],
        'findings':['Tune the brick mapping/scale so the facade reads as masonry at the saved render scale; improve the visible bay depth, window AC detail, and facade transitions; verify side/rear roof volumes against newer imagery if available.']
      },
      'modular_export_portability_and_evidence':{
        'score':1.9,'max_score':2.0,
        'evidence':[
          f"A separate Blender 5.2.3 background process opened the exact candidate file (SHA256 {probe['asset_sha256']}) and found the named scene, building ID, named collection, and local-coordinate flag.",
          f"Fresh-open inspection counted {probe['objects']} collection objects, {probe['mesh_objects']} meshes and {probe['material_count']} referenced materials; no meshes lack materials, no mesh misses the asset root parent, and no external file images are unpacked.",
          'Building-specific evidence records source providers/URLs, GIS IDs, coordinate transform, retrieval dates, measurement method, uncertainty, and exterior/interior previews; no public interior plan was found and the interior is clearly labeled representative/estimated.'
        ],
        'findings':['The saved previews demonstrate the asset but do not verify integration into the campus master; that remains a coordinator-side check.']
      }
    }
    score=round(sum(c['score'] for c in score_items.values()),2)
    findings=[]
    for c in score_items.values(): findings.extend(c['findings'])
    return {
      'building_id':'alpha_epsilon_pi',
      'reviewer':'independent subagent; evaluator written and run against fresh-open measurements, source evidence and saved views',
      'candidate_sha256':probe['asset_sha256'],
      'candidate_sha256_matches_builder_report':probe['asset_sha256']==EXPECTED_HASH,
      'score':score,'max_score':10.0,'threshold':8.0,
      'status':'PASS' if score>=8.0 else 'NEEDS_REFINEMENT',
      'criteria':score_items,
      'evidence':[
        'Current project evidence and GIS source snapshots: audit/alpha_epsilon_pi/evidence.json and purdue_gis_features_fid754_821.json.',
        'Independent fresh-open probe: audit/alpha_epsilon_pi/independent_grade_current/fresh_open_probe.json.',
        'Exterior/interior renders inspected: audit/alpha_epsilon_pi/previews/alpha_epsilon_pi_exterior.png and alpha_epsilon_pi_interior.png.',
        'Footprint overlay inspected: audit/alpha_epsilon_pi/satellite_footprint_overlay.png.',
        'Historic photo source page: https://commons.wikimedia.org/wiki/File:PurdueAEPIhouse.jpg (uploader caption identifies Purdue AEPi; dated October 26, 2009).'
      ],
      'findings':findings,
      'limitations':['The review does not certify current occupancy at the GIS footprint or master-blend integration. Interior arrangement is representative and not tied to a measured plan.']
    }

probe=json.loads(PROBE.read_text(encoding='utf-8'))
evidence=json.loads(EVIDENCE.read_text(encoding='utf-8'))
assert probe['building_id']=='alpha_epsilon_pi'
assert probe['asset_sha256']==EXPECTED_HASH, 'Candidate hash differs from the frozen grade-ready revision.'
assert probe['max_corresponding_vertex_error_m']<1e-4
assert probe['objects']>100 and probe['mesh_objects']>100
assert not probe['missing_material_meshes'] and not probe['mesh_parent_errors'] and not probe['unpacked_external_images']
assert evidence['building_id']=='alpha_epsilon_pi'
result=evaluate(probe,evidence)
(HERE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
lines=[
 '# Independent Alpha Epsilon Pi review',
 '',
 f"**Score: {result['score']:.2f}/10 — {result['status'].replace('_',' ').lower()}.** The 8.0 passing threshold is not met.",
 '',
 '| Criterion | Score | Independent assessment |',
 '| --- | ---: | --- |'
]
for key,c in result['criteria'].items():
    assessment=' '.join(c['evidence'][:2])
    lines.append(f"| {key.replace('_',' ')} | {c['score']:.2f}/2 | {assessment} |")
lines += ['', '## Required refinements', '']
for i,f in enumerate(result['findings'],1): lines.append(f'{i}. {f}')
lines += ['', '## Limits', '']
for f in result['limitations']: lines.append(f'- {f}')
(HERE/'result.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'score':result['score'],'status':result['status'],'criteria':{k:v['score'] for k,v in result['criteria'].items()},'result':str(HERE/'result.json'),'report':str(HERE/'result.md')},indent=2))
