"""Independent rubric for the frozen Beta Theta Pi revision 4 asset."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
F=json.loads((HERE/'fresh_open_findings.json').read_text(encoding='utf-8'))
EXPECTED='34d0b02c5e76284e3751f1b533d6489074aced3c9eddb7f5bb006ae255957277'
assert F['fresh_open'] and F['blender_version'].startswith('5.2.3')
assert F['asset_sha256']==EXPECTED
assert F['source_feature_id']==826 and F['source_building_name']=='Beta Theta Pi'
assert F['roof_shell_diagnostics']['boundary_edges']==0
assert F['roof_shell_diagnostics']['nonmanifold_edges']==0
assert F['roof_shell_diagnostics']['zero_area_faces']==0
assert F['roof_top_facets_upward']==F['roof_top_facets_expected']==17
criteria=[
 {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
  'evidence':['Purdue BuildingShapesZip4 FID 826 identifies Beta Theta Pi, 150 Littleton St; Beta Mu and BoilerLink directory sources corroborate the address.','The fresh-open wall base has 19 unique vertices matching all 19 transformed GIS ring vertices with maximum nearest-vertex error 0.0000294 m.'],
  'finding':'Identity and building footprint are exceptionally well supported.'},
 {'criterion':'Campus placement and plan scale','score':1.9,'max_score':2.0,
  'evidence':['Fresh-open world bounds are X 805.983–827.110 m, Y -417.268–-375.652 m; these align with the exact campus-transformed feature footprint.','GIS aerial overlay supports the location. Facade photo orientation is not independently georegistered.'],
  'finding':'Placement and plan dimensions are reliable; facade bearing is not survey-verified.'},
 {'criterion':'Evidence-backed roof and vertical massing','score':1.45,'max_score':2.0,
  'evidence':['The r4 roof shell is one continuous closed mesh: 38 vertices, 73 edges, 37 faces, zero boundary edges, zero nonmanifold edges, and zero zero-area faces.','All 17 top roof facets have upward normals; the 19 side faces and one underside face have expected vertical/downward orientation. Every mesh in the file has nonzero face area.','Previews retain dark-looking seams at some gable/roof intersections; the actual roof shell is continuous, but its shallow ridge and exact heights are photographic estimates.'],
  'finding':'The former disconnected roof facets are fixed and topology/normals are sound. Gable intersections still read visually dark/awkward, and no measured roof elevations are available.'},
 {'criterion':'Facade, entrance, and distinctive photo-backed details','score':1.55,'max_score':2.0,
  'evidence':['The six r4 previews show the three-level brick facade, divided sash windows, projecting pale bay with stacked arched openings, central front gable, two dormers, arched entry, and chapter crest; these motifs appear in chapter-house photos.','Facade placement and window spacing are simplified/repetitive. The doorway reads as a pale blank block in the close view, and the arch/crest proportions do not fully capture the photographed entry.'],
  'finding':'The primary architectural identity is recognizable and substantially source-informed, with simplified rhythms and a visibly unresolved door detail.'},
 {'criterion':'Portable materials, modular handoff, and evidence quality','score':1.5,'max_score':2.0,
  'evidence':['Fresh-open scene and collection names match contract; 349 mesh objects load in the expected collection.','Six node-based materials reopen; brick, slate, stone, and painted trim use procedural nodes. No external file images are referenced.','Identity, GIS geometry, official chapter-house photo gallery, university listing, Esri aerial, and limitations are documented.','Materials look mottled rather than coursed brick/slate in renders; there is no interior model because no reliable public floor plan was found.'],
  'finding':'The file is self-contained and source-documented. Surface texture is stylized, and omission of an unsupported interior is appropriate.'}
]
score=round(sum(c['score'] for c in criteria),2)
result={'building':'Beta Theta Pi (Beta Mu Chapter)','building_id':'massing_beta_theta_pi_fid826','revision':4,
 'asset':'modular/buildings/massing_beta_theta_pi_fid826.blend','asset_sha256':F['asset_sha256'],'expected_sha256':EXPECTED,
 'exact_sha_match':F['asset_sha256']==EXPECTED,'review_date':'2026-10-27','reviewer':'independent grader',
 'blender_version':F['blender_version'],'fresh_open':F['fresh_open'],'score':score,'max_score':10.0,
 'threshold':8.0,'accepted':score>=8.0,'criteria':criteria,
 'fresh_open_findings':'audit/beta_theta_pi/independent_grade_revision_4/fresh_open_findings.json',
 'previews':['audit/beta_theta_pi/preview_r4_'+x+'.png' for x in ['aerial','close','east','north','south','west']],
 'actionable_findings':['Adjust the doorway/entry material and proportions so a dark wood door and transom read clearly in the close view.','Reduce dark-looking roof/gable intersection artifacts and review with more even lighting; the closed roof shell itself is watertight and correctly oriented.','Consider a coursed brick and more restrained slate pattern so the native procedural materials read less like mottled noise.','Keep roof heights and the north-south ridge documented as photo-derived estimates; no survey values were found.','No interior revision is required without a reliable public floor plan.']}
(HERE/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'score':score,'accepted':result['accepted'],'sha256':result['asset_sha256']},indent=2))
