import json
from pathlib import Path

def evaluate(root=None):
    root=Path(root) if root else Path(__file__).resolve().parents[3]
    audit=root/'audit/delta_gamma'
    probe=json.loads((audit/'independent_grade/blender_probe.json').read_text(encoding='utf8'))
    ev=json.loads((audit/'evidence.json').read_text(encoding='utf8'))
    gis=json.loads((audit/'sources/purdue_gis_fid783_raw.json').read_text(encoding='utf8'))['features'][0]
    attributes=gis['attributes']
    identity_score=2.0 if (attributes['FID']==783 and attributes['BUILDING_N']=='Delta Gamma' and attributes['ADDRESS']=='303 Waldron St' and probe['expected_collection_present'] and probe['collection_objects']==['House_301840872']) else 0.0
    position_score=1.6 if probe['max_footprint_vertex_residual_m']<0.0001 and probe['identity_transform']['location']==[0,0,0] and probe['identity_transform']['scale']==[1,1,1] else 0.5
    height_score=1.25 # facade levels visible; height/roof unsupported, and NUM_LEVELS conflict
    facade_score=1.4 # central arch/bay, brick wings, grouped windows and stairs match photo; decorative detail is schematic
    modular_score=2.0 if (probe['expected_structure_verified'] and probe['external_file_images']==[] and len(probe['collection_objects'])==1 and probe['object_type']=='MESH' and probe['modifiers']==[]) else 1.0
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':identity_score,'max_score':2,'evidence':[f"Purdue GIS FID {attributes['FID']} identifies {attributes['BUILDING_N']} at {attributes['ADDRESS']}.",f"The source has {probe['gis_unique_vertices']} distinct polygon vertices; the rebuilt base includes all vertices."],'findings':['GIS positional accuracy is unpublished; the raw layer is not a certified survey.']},
      {'criterion':'Position, orientation, and scale/dimensions','score':position_score,'max_score':2,'evidence':[f"Maximum residual to the exact transformed GIS ring is {probe['max_footprint_vertex_residual_m']:.8f} m.",'The massing asset retains campus coordinates and identity object transform; plan outline is source-matched.'],'findings':['The photo is not georeferenced, so the selected east-facing frontage/entrance bearing cannot be verified.','Decorative entry stairs extend beyond the GIS wall outline; this is a reasonable projection but not a wall-footprint match.']},
      {'criterion':'Evidence-backed height, floors, and roof form','score':height_score,'max_score':2,'evidence':['The member photo shows at least two facade levels and a raised central bay; the model represents these features.','The model reopens to a 11.255 m total vertical bound.'],'findings':['GIS NUM_LEVELS=1 conflicts with the photo interpretation; field meaning is unknown.','No measured eaves, ridge, or total height source is available; the photo crops the roof, and the flat/low roof cap is an estimate.']},
      {'criterion':'Facade, entrances, and distinctive architecture','score':facade_score,'max_score':2,'evidence':['The photo shows brick wings, a raised central entrance bay with an arched upper panel, Greek-letter signage, grouped windows, and broad approach steps.','The preview includes brick wings, raised central bay, upper and entry arches, stylized ΔΓ marks, windows, and steps.'],'findings':['The symbol/sign and window rhythm are simplified; exact facade dimensions and color details are not measured.','The official chapter page mentions a front porch, but the photo and map do not establish its exact size or compass orientation.']},
      {'criterion':'Modular export, portability, and complete evidence','score':modular_score,'max_score':2,'evidence':['Reopened .blend has exactly the expected one-object mesh collection and identity transform.','No external file images or modifiers; expected asset object is present.','Raw GIS snapshot, member image/page, transform, preview, validation, and source uncertainties are recorded.'],'findings':['Master integration is still pending and is correctly left to the coordinator.']}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    return {'score':score,'max_score':10,'criteria':criteria,'evidence':{'asset_path':probe['asset_path'],'reopened_in_blender':probe['asset_opened'],'collection_objects':probe['collection_objects'],'object_type':probe['object_type'],'identity_transform':probe['identity_transform'],'evaluated_bounds_xyz_m':probe['evaluated_bounds_xyz_m'],'GIS_feature_id':probe['gis_feature_id'],'GIS_vertices':probe['gis_unique_vertices'],'max_base_ring_residual_m':probe['max_footprint_vertex_residual_m'],'external_image_paths':probe['external_file_images'],'rendered_view':'../preview.png','reviewed_source_image':'../sources/delta_gamma_house_exterior_2014.png','official_address_source':'https://purdue.deltagamma.org/the-house'},'findings':['PASS: score meets the 8/10 minimum.' if score>=8 else 'FAIL: score is below the 8/10 minimum.','The exact campus footprint is verified; height, roof form, and facade bearing remain uncertain.']}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[3]
    result=evaluate(root)
    out=root/'audit/delta_gamma/independent_grade/result.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    (root/'audit/delta_gamma/independent_grade/evaluator_output.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    lines=['# Independent Grade — Delta Gamma','',f"**Score: {result['score']:.2f}/10 — {'PASS' if result['score']>=8 else 'FAIL'}**",'', '| Criterion | Score |','|---|---:|']
    lines += [f"| {c['criterion']} | {c['score']:.2f}/{c['max_score']} |" for c in result['criteria']]
    lines += ['', 'The reviewer reopened the Blender asset and compared the 14-point source ring with base-wall vertices, then inspected the chapter member’s exterior photo and official chapter address page. The official GIS identifies the location and footprint. The photo supports the brick wings, central entry bay, arches, window groups, and stairs, but crops the roof and has no camera pose. Height, roof shape, floor count (GIS NUM_LEVELS=1 conflict), and facade bearing remain estimates.', '', f"Maximum base-ring residual: {result['evidence']['max_base_ring_residual_m']:.8f} m. The expected collection contains one mesh object with identity transform; no external file images or modifiers are present."]
    (root/'audit/delta_gamma/independent_grade/independent_grade.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
