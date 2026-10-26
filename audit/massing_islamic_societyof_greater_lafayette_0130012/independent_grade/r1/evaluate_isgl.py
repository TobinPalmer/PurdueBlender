from __future__ import annotations
import json, math
from pathlib import Path

ID = 'massing_islamic_societyof_greater_lafayette_0130012'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = ROOT / 'audit' / ID
ASSET = ROOT / 'modular' / 'buildings' / f'{ID}.blend'
MANIFEST = ROOT / 'modular' / 'manifest.json'
GIS = AUDIT / 'sources' / 'purdue_gis_FID771_SOMSA.json'
CATALOG = AUDIT / 'sources' / 'source_catalog.json'
VALIDATION = AUDIT / 'review' / 'reopen_validation.json'
EVIDENCE = AUDIT / 'evidence_record.json'
RENDERS = [AUDIT / 'renders' / n for n in ('isgl_exterior_approach.png','isgl_front_elevation.png','isgl_roof_plan.png')]

def shoelace(points):
    return abs(sum(points[i][0]*points[(i+1)%len(points)][1] - points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))/2)

def evaluate():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    entries = manifest if isinstance(manifest,list) else manifest.get('buildings',manifest.get('assets',[]))
    entry = next((e for e in entries if e.get('id') == ID), None)
    gis_doc=json.loads(GIS.read_text(encoding='utf-8'))
    feature=gis_doc['features'][0]
    attrs=feature['attributes']
    raw=feature['geometry']['rings'][0]
    ring=raw[:-1] if raw and raw[0]==raw[-1] else raw
    xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)), (lat-40.4274)*111040.0) for lon,lat in ring]
    area=shoelace(xy)
    bounds=[min(p[0] for p in xy), min(p[1] for p in xy), max(p[0] for p in xy), max(p[1] for p in xy)]
    validation=json.loads(VALIDATION.read_text(encoding='utf-8'))
    evidence=json.loads(EVIDENCE.read_text(encoding='utf-8'))
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    vb=validation['bounds_world_m']
    actual_bounds=[vb[0][0],vb[1][0],vb[0][1],vb[1][1]]
    shell_error=validation['gis_shell_vertex_nearest_error_m']['maximum']
    render_status={p.name:{'exists':p.is_file(),'bytes':p.stat().st_size if p.is_file() else 0} for p in RENDERS}
    asset_bytes=ASSET.stat().st_size if ASSET.exists() else 0
    identity_ok=(attrs.get('FID')==771 and attrs.get('BLDG_ABBR')=='SOMSA')
    direct_validation=(validation.get('validation')=='passed' and validation.get('checks',{}).get('gis_shell_vertices_within_0_00002m'))
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':1.3,'max_score':2,'evidence':f"Purdue FID {attrs.get('FID')} / {attrs.get('BLDG_ABBR')} is labeled {attrs.get('BUILDING_N')} at {attrs.get('ADDRESS')}; ISGL official contact page gives 1022 1st St., and the labeled Visit Lafayette photo plus imagery place the society at the same First/Russell corner. GIS ring has {len(ring)} vertices and transformed shoelace area {area:.2f} m², while ArcGIS Shape__Area={attrs.get('Shape__Area')} m²; the substantial field/ring area conflict is unresolved. Saved validator reports maximum ring-to-shell nearest-vertex error {shell_error:.8f} m. Physical match is plausible/high confidence, but GIS name/address do not identify ISGL and discrepancy is unresolved."},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.9,'max_score':2,'evidence':f"GIS ring transformed using repository's documented campus approximation has XY bounds [{bounds[0]:.3f},{bounds[1]:.3f}]–[{bounds[2]:.3f},{bounds[3]:.3f}] m. Reopen record places asset bounds at [{actual_bounds[0]:.3f},{actual_bounds[1]:.3f}]–[{actual_bounds[2]:.3f},{actual_bounds[3]:.3f}] m and reports exact transformed source-ring vertices within {shell_error:.8f} m. Site corner and roof orientation are visually consistent with current orthophoto; local conversion is approximate, not survey control."},
      {'criterion':'Evidence-backed height, floors, and roof form','score':0.8,'max_score':2,'evidence':f"GIS attributes NUM_LEVELS={attrs.get('NUM_LEVELS')}, CountOfFLO={attrs.get('CountOfFLO')}, Extrution={attrs.get('Extrution')} (unit semantics undocumented). Saved model height is {vb[2][1]:.2f} m, with stated estimated eaves 6.05 m and roof peak 8.15 m. Exterior photo supports a two-band facade and a sloped roof, and orthophoto supports a multi-plane roof, but neither establishes floor count, dimensions, or roof geometry. The rendered single-apex hipped/pyramidal roof does not convincingly reproduce the several distinct roof planes/ridges visible in the orthophoto."},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.4,'max_score':2,'evidence':'The published labeled exterior photo visibly supports red-brown brick, two facade/window bands, pale entry surround, and a small domed canopy/sign. Render includes those features and no unsupported large mosque dome/minaret. It uses a generic repeated bay rhythm and inferred entrance orientation; the source photograph is an oblique view without georeferenced camera direction, so exact bay spacing, entry side and hidden facades are not independently established.'},
      {'criterion':'Modular export, portability, and complete evidence','score':1.8,'max_score':2,'evidence':f"Expected asset exists ({asset_bytes} bytes). Saved Blender 4.5.15 reopen report identifies expected scene/collection, exactly one mesh (982 vertices, 750 faces), no modifiers, external images or linked libraries; three renders exist: {render_status}. Evidence folder includes raw GIS, metadata, official ISGL identity pages, labeled facade photo, orthophoto metadata, source catalog, build measurements and validation. This review could not start Blender because the connected Blender addon is offline and no bpy module is installed; geometry checks below therefore independently recalculate source ring metrics and cross-check the saved reopen report, but do not newly reopen the file."}
    ]
    score=round(sum(c['score'] for c in criteria),1)
    findings=[
      {'severity':'major','finding':'The building match relies on location and the labeled ISGL photo: GIS FID 771 is explicitly named Muslim Student Association at 1021 First St., while ISGL currently gives 1022 1st St.','action':'Locate an authoritative address/building history, parcel record, or Purdue/municipal document that links FID 771 or the historical 1021 address to ISGL; otherwise retain this as a probable site match and avoid stating that the GIS identity is confirmed.'},
      {'severity':'moderate','finding':f"The GIS Shape__Area attribute ({attrs.get('Shape__Area')} m²) is substantially larger than the transformed polygon-ring area ({area:.2f} m²); ring geometry is used for shell fit but the area-field discrepancy is unresolved.",'action':'Retain the raw ring and document the transformed coordinate-area calculation; seek the layer’s area-calculation method or an independent parcel/building survey before treating either area as measured ground truth.'},
      {'severity':'major','finding':'Height and roof remain estimates. GIS says one level; the model interprets two facade bands and its rendered roof has one apex, while current aerial shows several roof planes/ridges.','action':'Seek dimensioned elevations, older/current oblique imagery, or roof imagery with clearer ridge detail; revise the roof silhouette and height only if those sources resolve the existing discrepancy. Until then label the geometry illustrative.'},
      {'severity':'moderate','finding':'Facade rhythm and entrance orientation are extrapolated from a single un-georeferenced photo.','action':'Find a second view or georeferenced street photo to confirm which facade is shown and verify window-bay rhythm and entrance side.'},
      {'severity':'review limitation','finding':'A fresh Blender reopen was not possible in this grading environment; the direct reopen JSON predates this review.','action':'Have the coordinator or builder rerun the provided reopen validator when Blender is available; no asset or evidence files were altered by this grader.'}
    ]
    return {'score':score,'max_score':10,'criteria':criteria,'evidence':{'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),'asset_exists':ASSET.is_file(),'manifest_entry':entry,'identity_fields':{k:attrs.get(k) for k in ('FID','BLDG_ABBR','BUILDING_N','ADDRESS','NUM_LEVELS','CountOfFLO','Extrution')},'gis_ring':{'unique_vertices':len(ring),'area_m2_local_approx':area,'bounds_xy_m':[round(v,6) for v in bounds]},'saved_asset_bounds_world_m':vb,'independently_recomputed_footprint_to_shell_error_m_from_saved_validator':shell_error,'saved_reopen_report_status':validation.get('validation'),'saved_reopen_report_checks':validation.get('checks'),'renders':render_status,'source_catalog_count':len(catalog.get('sources',[])),'direct_blender_reopen_this_review':False},'findings':findings}

if __name__=='__main__':
    result=evaluate()
    output=HERE/'result.json'
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
