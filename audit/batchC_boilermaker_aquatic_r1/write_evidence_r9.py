import json
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_boilermaker_aquatic_r1')
e=json.loads((p/'evidence_r8.json').read_text(encoding='utf-8'))
e.update({'revision':9,'review_date':'2026-10-25','starting_grade':7.9,'starting_grade_source':'Independent R8 review at independent_grade_r8.md (7.9/10).','changes':e['changes']+[
 'Added 24 continuous graphite riser plates beneath the existing 24 representative aluminum bench sections to make the two tier banks read as connected bleachers. Their dimensions and structural function are illustrative, not an as-built seating plan.',
 'Added 24 square handrail posts, one aligned to each of 12 aisle treads on both sides, and modestly thickened the two existing sloped rails. The posts visually meet the stair treads and existing handrails; exact rail dimensions and accessibility compliance remain unverified.',
 'Added a saved interior cutaway presentation camera. The R9 render script temporarily hides the full roof surface, standing seams, ridge cap, and one eave fascia for the cutaway images; those objects are restored for render setup and the saved source retains the complete roof. Existing 21 schematic truss meshes remain in the asset and are exposed above the pool and seating in the review view.',
 'Coordinator reported a read-only check of the master marker: (-808.6829834, 80.3369980, 0) translation, unit scale and zero rotation. It agrees with manifest origin (-808.683, 80.337) within 0.000017 m. This report is recorded as coordinator-provided evidence; this revision did not open or save the master.'
 ],'validation_file':'audit/batchC_boilermaker_aquatic_r1/validation_r9.json','validation_status':'passed: Blender 5.2.3 reopened the saved R9 source, preserved the complete roof and 21 existing trusses, validated the GIS outline correspondence, counted the new risers/posts, checked material assignments, and found no external image dependencies. The root coordinator separately reported a direct read-only master-marker comparison against the manifest origin.','validation_summary':json.loads((p/'validation_r9.json').read_text(encoding='utf-8')),'uncertainties':[
 'No measured roof section, roof profile, eave elevation, or ridge elevation was located. Roof and height geometry remain unverified and unchanged.',
 'The existing 21 truss meshes are schematic; the cutaway exposes their placement but does not verify member sizing, spacing, elevation or as-built geometry.',
 'The new 24 risers and 24 rail posts are illustrative supporting details. Exact seating geometry, capacity, stair/aisle details, rail dimensions and accessibility compliance are unverified.',
 'Interior review camera position is for presentation only and is not a surveyed viewpoint.',
 'The cutaway images hide roof surfaces only for review; the reopened saved asset retains the complete roof geometry.',
 'GIS-to-shell outline correspondence does not establish survey accuracy or vertical geometry.'
 ],'renders':['audit/batchC_boilermaker_aquatic_r1/aquatic_r9_interior_truss_cutaway.png','audit/batchC_boilermaker_aquatic_r1/aquatic_r9_bleacher_aisle_detail.png'],'asset_sha256':'136c7c7ee7d9d69f8bd1ac84e6e9269c00297a9c464bdd42ef13009bba66f497','coordinator_master_placement_check':json.loads((p/'validation_r9.json').read_text(encoding='utf-8'))['coordinator_master_placement_check']})
(p/'evidence_r9.json').write_text(json.dumps(e,indent=2)+'\n',encoding='utf-8')
