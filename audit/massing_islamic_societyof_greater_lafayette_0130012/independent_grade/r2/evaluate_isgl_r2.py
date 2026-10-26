from __future__ import annotations
import json
from pathlib import Path

ID = 'massing_islamic_societyof_greater_lafayette_0130012'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = ROOT / 'audit' / ID
ASSET = ROOT / 'modular' / 'buildings' / f'{ID}.blend'
MANIFEST = json.loads((ROOT / 'modular' / 'manifest.json').read_text(encoding='utf-8'))
ENTRIES = MANIFEST if isinstance(MANIFEST, list) else MANIFEST.get('buildings', MANIFEST.get('assets', []))
REOPEN = json.loads((HERE / 'reopen_validation.json').read_text(encoding='utf-8'))
EVIDENCE = json.loads((AUDIT / 'evidence_record.json').read_text(encoding='utf-8'))
SOURCES = json.loads((AUDIT / 'sources' / 'source_catalog.json').read_text(encoding='utf-8'))

def evaluate():
    entry = next((x for x in ENTRIES if x.get('id') == ID), None)
    gis = json.loads((AUDIT / 'sources' / 'purdue_gis_FID771_SOMSA.json').read_text(encoding='utf-8'))['features'][0]['attributes']
    criteria = [
      {'criterion':'Correct identity and source-backed footprint','score':1.5,'max_score':2,
       'evidence':'The official ISGL page and labeled Visit Lafayette photograph identify the society and 1022 1st St. location. Purdue Engineering’s 2022 event page connects the same venue with Muslim Student Association activity; the county judgments list North American Islamic Trust Inc. ISGL at 1022 First. Purdue GIS FID 771 / SOMSA geometry lands at this First/Russell site and its ring is directly used for the base shell. The GIS record still says Muslim Student Association / 1021 FIRST ST., without a parcel crosswalk; Shape__Area=800.789 m² also conflicts with transformed ring shoelace area 463.267 m². This is a strong physical-site match, not a fully resolved official feature crosswalk.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.9,'max_score':2,
       'evidence':f"Fresh independent Blender reopen confirms all 11 GIS shell ring vertices within {REOPEN['gis_shell_vertex_nearest_error_m']['maximum']:.8f} m using the documented campus conversion. Model bounds are X {REOPEN['bounds_world_m'][0][0]:.3f}..{REOPEN['bounds_world_m'][0][1]:.3f}, Y {REOPEN['bounds_world_m'][1][0]:.3f}..{REOPEN['bounds_world_m'][1][1]:.3f} m; plan dimensions are approximately 22.85 x 23.78 m. The orthophoto corroborates site orientation and multi-wing roof plan. The repository conversion is approximate rather than survey control; no independent wall survey resolves the Shape__Area conflict."},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2,
       'evidence':'The 2022–2025 Indiana orthophoto directly supports a complex intersecting, multi-plane roof silhouette, and r2 replaced the former single-apex roof with west/east roof volumes that better reflect visible plane breaks. The rendered roof remains a simplified, estimated interpretation; roof elevations and pitches are not measurable from this overhead image. Height is 8.15 m, eaves 6.05 m, and ridge heights 7.50/8.15 m by estimate. GIS attributes NUM_LEVELS=1 and CountOfFLO=1 conflict with the two visible facade/window bands in the photo. No measured height or verified occupancy floor count was found.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2,
       'evidence':'The published labeled photo visibly supports red-brown brick, upper and ground-level window bands, pale entrance surround, signage, and a small domed entrance canopy; the model contains these features and avoids an unsupported large mosque dome/minaret. Bay spacing, unseen facades, and entrance compass side remain extrapolated from one oblique, ungeoreferenced image.'},
      {'criterion':'Modular export, portability, and complete evidence','score':1.9,'max_score':2,
       'evidence':f"Fresh Blender 4.5.15 LTS reopen confirms the expected scene and collection, one named mesh (982 vertices, 747 faces), zero modifiers, no external images, and no linked libraries. Independent shell check passes at 0.00001437 m maximum nearest-vertex error. Three renders exist; raw GIS/metadata, official organization pages, labeled exterior photo, orthophoto snapshot/metadata, event page, county PDF, source catalog, and evidence record are present. Minor deduction: manifest bounds and accuracy_status remain stale legacy values, although stable ID/file/collection/scene are correct and this grading task cannot edit shared indexes."}
    ]
    score = round(sum(c['score'] for c in criteria), 1)
    findings = [
      {'severity':'moderate','finding':'Purdue GIS FID 771 is labelled Muslim Student Association / 1021 FIRST ST., while official ISGL records say 1022 1st St.; additional event and county records corroborate the organizations/site but no formal parcel crosswalk was found.','action':'Retain this as a strong physical-site match with explicit crosswalk uncertainty; accept a parcel or address-history source if one is found.'},
      {'severity':'moderate','finding':'ArcGIS Shape__Area (800.789 m²) differs substantially from the transformed ring shoelace area (463.267 m²).','action':'Keep the returned ring unscaled and state area-field provenance as unresolved until authoritative GIS metadata or a survey clarifies it.'},
      {'severity':'major','finding':'The modeled roof form and all vertical dimensions are estimates; GIS reports one level while the photo shows two facade bands, and roof pitch/ridge heights cannot be recovered from the overhead imagery.','action':'Keep heights/floors labeled estimated or unverified. Dimensioned elevations or reliable oblique/roof imagery would be needed for stronger claims.'},
      {'severity':'moderate','finding':'Facade rhythm and entrance orientation are based on a single oblique, ungeoreferenced facade photograph.','action':'Treat window spacing and entrance compass side as inferred unless a second geolocated view becomes available.'},
      {'severity':'minor','finding':'Shared manifest bounds and accuracy_status still describe the legacy fallback massing rather than this updated mesh.','action':'Coordinator should refresh the shared manifest after accepting this grade; shared files were not changed during this independent review.'}
    ]
    return {'score':score,'max_score':10,'pass_threshold':8,'passed':score>=8,'criteria':criteria,
      'evidence':{'asset_path':'modular/buildings/'+ID+'.blend','asset_exists':ASSET.is_file(),'manifest_entry':entry,
        'source_identity_fields':{k:gis.get(k) for k in ('FID','BLDG_ABBR','BUILDING_N','ADDRESS','NUM_LEVELS','CountOfFLO','Extrution','Shape__Area')},
        'direct_reopen':REOPEN,'evidence_record_path':'audit/'+ID+'/evidence_record.json','source_catalog_count':len(SOURCES.get('sources',[])),
        'render_files':{p.name:{'exists':p.is_file(),'bytes':p.stat().st_size if p.is_file() else 0} for p in (AUDIT/'renders').glob('*.png')},
        'independent_visual_inspection':['renders/isgl_exterior_approach.png','renders/isgl_front_elevation.png','renders/isgl_roof_plan.png','sources/indiana_current_imagery_isgl.jpg','sources/isgl_exterior_homeofpurdue.jpg']},
      'findings':findings}

if __name__ == '__main__':
    result=evaluate()
    (HERE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))


