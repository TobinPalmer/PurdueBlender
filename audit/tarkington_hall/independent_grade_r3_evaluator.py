"""Independent R3 evaluator for Tarkington Hall (read-only asset grader)."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent
ASSET=ROOT/'modular/buildings/tarkington_hall.blend'
EXPECTED='825d57329797fd45b6eb7784c8a6011f99a575bed6a97c11ed06e098eb618ee1'
THRESHOLD=8.0

def read(name): return json.loads((AUDIT/name).read_text(encoding='utf-8'))

def evaluate():
    reopen=read('independent_reopen_r3.json')
    fp=read('independent_footprint_r3.json')
    sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    assert sha==EXPECTED==reopen['sha256']==fp['sha256']
    m=reopen['membership']
    assert reopen['fresh_process_reopen'] and reopen['root_transform_identity']
    assert m['collection_object_count']==910 and m['mesh_count']==891
    assert m['connector_count']==96 and m['west_connector_count']==48 and m['east_connector_count']==48
    assert m['all_connectors_only_in_asset_collection'] and m['all_connectors_parented_to_root']
    assert not m['connector_meshes_missing_materials'] and not m['duplicate_object_names_in_asset']
    assert not m['nonfinite_mesh_vertices'] and not m['materialless_meshes'] and not m['invalid_material_indices']
    assert not reopen['missing_external_images'] and not m['external_linked_libraries']
    assert fp['feature_id']==662 and fp['building_code']=='TARK'

    criteria=[
      {'name':'Correct identity and source-backed footprint','score':1.5,'max_score':2.0,
       'evidence':f"The official Purdue GIS snapshot is FID 662/code TARK; the 2023 Indiana ortho overlay agrees on the characteristic four-arm residence-hall form. Fresh export-only shell extraction yields IoU {fp['polygon_iou']:.3f}, mean symmetric boundary residual {fp['symmetric_sampled_boundary_mean_m']:.2f} m, P95 {fp['symmetric_sampled_boundary_p95_m']:.2f} m, and Hausdorff {fp['symmetric_boundary_hausdorff_m']:.2f} m. The footprint now includes the two connector shell groups. The central/core perimeter and selected shell proxy still diverge materially. The GIS perimeter is not documented as surveyed wall faces; the orthophoto comparison may represent roof edges."},
      {'name':'Position, orientation, and scale/dimensions','score':1.2,'max_score':2.0,
       'evidence':f"On the same local GIS transform, the export-shell centroid is offset {fp['centroid_delta_m'][0]:.2f} m east-west and {fp['centroid_delta_m'][1]:.2f} m north-south (0.71 m resultant); plan bounds are broadly similar. The independent asset reopen verifies the root transform is identity, but the campus Placement_tarkington_hall marker is outside this building library and was not checked in this pass, so campus position/orientation remain unverified here. GIS-to-local conversion is approximate; no surveyed wall dimensions were found."},
      {'name':'Evidence-backed height, floors, and roof form','score':1.3,'max_score':2.0,
       'evidence':'The model has four occupied floors and a flat-roof, four-wing massing with roof penthouses/equipment. Purdue’s current emergency plan identifies East and West wings with four floors each and central lounge, reception, dining/kitchen, study/recreation, mail, laundry, linen, mechanical, and staff uses. The reopened asset bounds reach 19.1 m, but the public material reviewed provides no measured building elevation; roof/penthouse heights and parts of the core remain modeled estimates. Orthophoto/GIS residuals include outliers above 9 m.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.6,'max_score':2.0,
       'evidence':'The exterior render reads as a brick residence hall with four wings, repetitive window bays, light horizontal bands, roof masses, and a central entrance. R3 connector forms are now included in the actual export, correcting a major omission in R2. The facade treatment remains highly repetitive and simplified, with limited entrance articulation and no detailed representation of the verified central uses. The one available room cutaway has beds/desks but sparse finishes and little room-specific detailing; no representative central lounge/dining or typical full-floor interior is evidenced.'},
      {'name':'Modular export, portability, and complete evidence','score':1.6,'max_score':2.0,
       'evidence':f"Fresh Blender {reopen['blender_version']} reopened the exact canonical SHA. Asset_tarkington_hall contains all 910 expected objects/891 meshes, including all 96 connector meshes (48 each side), all connector objects are linked only to the asset collection and parented to the identity root, and no duplicate names, nonfinite vertices, materialless meshes, invalid material indices, missing external images, or foreign linked libraries were found. Sixteen used materials are present. Source snapshots, exterior/room renders, and footprint overlays exist; evidence remains limited for campus marker transform, measured elevations, and the interior program."},
    ]
    score=round(sum(c['score'] for c in criteria),1)
    findings=[
      {'priority':'high','finding':f"Footprint agreement is improved but still not acceptance-grade for a faithful footprint: IoU {fp['polygon_iou']:.3f}; mean residual {fp['symmetric_sampled_boundary_mean_m']:.2f} m; P95 {fp['symmetric_sampled_boundary_p95_m']:.2f} m; Hausdorff {fp['symmetric_boundary_hausdorff_m']:.2f} m. Inspect the central core and wing endings against the ortho while retaining uncertainty about whether the GIS boundary is a roof or wall edge."},
      {'priority':'high','finding':'Verify the canonical master Placement_tarkington_hall marker, linked asset orientation, and site position in a read-only master check; that transform is not stored in this building asset and is not proven by the local shell-to-GIS centroid comparison.'},
      {'priority':'medium','finding':'Improve façade and interior evidence beyond one simplified dorm-room cutaway. Model recognizable central lounge/dining/reception/common functions and provide a typical room/floor view using the official program as evidence.'},
      {'priority':'medium','finding':'Document reliable height/floor-elevation sources or clearly keep the 19.1 m roof height and roof-top masses labeled as estimates.'},
    ]
    return {'building':'Tarkington Hall','revision':'R3 independent regrade','score':score,'max_score':10.0,'pass_threshold':THRESHOLD,'passed':score>=THRESHOLD,'criteria':criteria,
       'evidence':{'asset':'modular/buildings/tarkington_hall.blend','sha256':sha,'blender_version':reopen['blender_version'],'fresh_reopen':reopen,'export_only_footprint_metrics':fp,'sources':{'Purdue GIS':'audit/tarkington_hall/gis_feature_662.json (FID 662, TARK)','orthophoto':'audit/tarkington_hall/indiana_2023_ortho_r1.png and ortho_footprint_overlay_r2.png','Purdue housing page':'https://www.housing.purdue.edu/my-housing/options/residence-halls/tarkington.html','Purdue emergency plan':'https://www.purdue.edu/operations/emergency-preparedness/tark/','exterior view':'audit/tarkington_hall/exterior_r2.png','interior view':'audit/tarkington_hall/room_r6.png'},'evaluation_limits':['This score checks the canonical building library, not its master scene placement transform.','The GIS feature is not identified as a surveyed wall-face boundary.','Height and central-program details lack complete measured/as-built documentation.']},'findings':findings}

if __name__=='__main__':
    result=evaluate()
    fp=read('independent_footprint_r3.json')
    (AUDIT/'independent_grade_r3.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    md=['# Tarkington Hall independent regrade R3','',f"**Score: {result['score']:.1f}/10 — {'PASS' if result['passed'] else 'below the 8/10 threshold'}**",'',f"Canonical SHA-256: `{result['evidence']['sha256']}`",'','## Criteria','']
    for c in result['criteria']: md += [f"### {c['name']} — {c['score']:.1f}/{c['max_score']:.1f}",'',c['evidence'],'']
    md += ['## Independently recomputed export-only metrics','',f"- Shell objects: {fp['shell_object_count']}",f"- Polygon IoU: {fp['polygon_iou']:.6f}",f"- Mean symmetric boundary residual: {fp['symmetric_sampled_boundary_mean_m']:.3f} m",f"- P95 residual: {fp['symmetric_sampled_boundary_p95_m']:.3f} m",f"- Hausdorff: {fp['symmetric_boundary_hausdorff_m']:.3f} m",f"- Shell centroid offset: {fp['centroid_delta_m'][0]:.3f} m east-west, {fp['centroid_delta_m'][1]:.3f} m north-south",'','## Findings','']
    for x in result['findings']: md.append(f"- **{x['priority'].title()}:** {x['finding']}")
    md += ['','## Evidence inspected','','- `independent_reopen_r3.json` and `independent_reopen_r3.log` (fresh Blender 5.2.3 process).','- `independent_shell_vertices_r3.json` (fresh export-collection-only geometry extraction).','- `independent_footprint_r3.json` (new computation from the saved GIS feature and extracted vertices).','- `ortho_footprint_overlay_r2.png`, `exterior_r2.png`, and `room_r6.png`.','- `refinement_r2.md`, `AGENT.md`, official Purdue housing page, and official emergency plan.','']
    (AUDIT/'independent_grade_r3.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
