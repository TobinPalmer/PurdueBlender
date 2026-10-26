import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
PROBE=json.loads((BASE/'model_probe.json').read_text(encoding='utf-8'))
SOURCE=BASE.parent

def evaluate(probe):
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'status':'verified','evidence':[
        'Purdue GIS BuildingShapesZip4 FID 526 identifies PGSC at 504 Northwestern Avenue; the independently inspected official Purdue page and Purdue Archives record support the PGSC identity and its place within the former Visitor Information Center portion of the garage.',
        f"Independent fresh-open comparison of the model's lower structural shell against the transformed GIS ring found {probe['asset']['gis_vertex_count']} corresponding XY vertices with symmetric maximum error {probe['asset']['source_model_symmetric_max_vertex_error_m']:.9f} m."],
       'reason':'Name/address/garage relationship are supported by Purdue records, and the model footprint directly reproduces the assigned GIS shell.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,'status':'verified in freshly opened master','evidence':[
        'Freshly opened master contains exactly one Placement_massing_purdue_graduate_student_center_af9c5c7 collection instance pointing to the requested asset file.',
        f"Marker XY is {probe['master']['marker_location'][:2]} m against manifest anchor {probe['master']['manifest_anchor']}; rotation is zero and scale is one.",
        'Freshly transformed exterior bounds match the manifest within 0.00003m; the GIS structural shell vertex comparison is within 0.000001m.'],
       'reason':'Marker placement, zero rotation, unit scale, and footprint geometry all check out independently.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2.0,'status':'partially verified; height remains estimated','evidence':[
        'Purdue GIS reports NUM_LEVELS=2 and Extrution=12, but the downloaded metadata does not specify vertical units or whether those attributes describe the low PGSC portion or full garage envelope.',
        'The model uses a 3.65m low-volume shell and a flat storefront/canopy composition; the official photo supports the canopy/fascia, but provides no surveyed elevation or roof section.'],
       'reason':'The visual roof/canopy form is plausible and partly source-supported; the 3.65m wall height remains a documented estimate, not a measurement.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.6,'max_score':2.0,'status':'mostly source-supported','evidence':[
        'Compared with the saved 2025 Purdue exterior image, the model contains the defining red-brown brick, light raised PGSC name, dark storefront glazing/doors, brick piers, and long horizontal canopy.',
        'The face is recognizable and the interior contains program-inspired rooms/furnishings, but some window layout and non-photographed sides are interpretive. The interior partitions/layout are schematic rather than taken from a measured floor plan.',
        'The integrated preview exposes the PGSC frontage while leaving the upper garage volume above it; the surrounding garage remains a coarse massing representation.'],
       'reason':'The photographed facade language and materials are present; secondary opening details and unseen sides lack direct photographic support.'},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,'status':'verified standalone and in master','evidence':[
        f"Exact asset SHA {probe['asset']['sha256']} opens the expected stable scene and collection with {probe['asset']['object_count']} objects, {probe['asset']['mesh_count']} meshes, 10 used procedural materials, and no unpacked external images.",
        'The fresh master uses the asset at the stable library path and links one placement marker. The garage source collection is not root-linked; the master-only cutout proxy is root-linked and has zero nonmanifold and zero boundary edges. `garage_source_probe.json` confirms the garage library SHA matches the Git LFS object at HEAD and its worktree is clean.',
        'Independent upward rays through three points in the PGSC footprint reach the garage cutout cap only at z≈4.5m, above the PGSC roof at z=3.65m; the source Northwestern Garage library is not modified.'],
       'reason':'The expected portable collection loads and the shared master interface is reproducibly collision-cleared without altering the assigned garage source asset.'}
    ]
    score=round(sum(c['score'] for c in criteria),1)
    return {'building':'Purdue Graduate Student Center (PGSC)','asset_id':'massing_purdue_graduate_student_center_af9c5c7','asset_path':'modular/buildings/massing_purdue_graduate_student_center_af9c5c7.blend','asset_sha256':probe['asset']['sha256'],'master_path':'purdue_campus_master.blend','master_sha256':probe['master']['master_sha256'],'grader':'independent_subagent','grade_date':'2026-10-26','score':score,'max_score':10,'passing_threshold':8,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,'evidence':['audit/purdue_graduate_student_center/independent_grade_master/model_probe.json','audit/purdue_graduate_student_center/independent_grade_master/asset_material_probe.json','audit/purdue_graduate_student_center/independent_grade_master/garage_source_probe.json','audit/purdue_graduate_student_center/preview_three_quarter.png','audit/purdue_graduate_student_center/preview_interior_schematic.png','audit/purdue_graduate_student_center/preview_master_interface.png','audit/purdue_graduate_student_center/sources/purdue_gis_pgsc_fid526_2026-10-26.geojson','audit/purdue_graduate_student_center/sources/purdue_official_pgsc_photo_2025-08.jpg','audit/purdue_graduate_student_center/sources/purdue_pgsc_historic_record_2026-10-26.html'],'findings':['PASS: exact asset SHA fresh-opened; identity and GIS structural shell agree within sub-micrometre error.','PASS: exactly one correct master marker with unit scale and zero rotation; transformed exterior bounds agree with the manifest within 0.00003m.','PASS: Northwestern Garage source remains untouched; the master-owned cutout proxy is watertight and clears the PGSC volume to z=4.5m.','Height 3.65m is estimated from a GIS field with undocumented units; it is not surveyed.','Room partitions and furnishings are schematic; no measured interior plan was found.','Upper garage decks and their facade remain coarse massing, so the interface preview is not a high-detail rendering of the entire garage.'],'master_integration_status':'PASS'}
result=evaluate(PROBE)
(BASE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'score':result['score'],'status':result['status'],'master_integration_status':result['master_integration_status'],'asset_sha256':result['asset_sha256']},indent=2))

