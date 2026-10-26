from __future__ import annotations
import json, math
from pathlib import Path

ID='massing_joyful_journeys_abaf5c3'
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
AUDIT=ROOT/'audit'/ID
ASSET=ROOT/'modular'/'buildings'/(ID+'.blend')
MANIFEST=ROOT/'modular'/'manifest.json'
OSM=AUDIT/'sources'/'osm_way_869182111_full.json'
SOURCE=AUDIT/'sources'/'source_record.json'
VALIDATION=AUDIT/'review'/'validation_r1.json'
REOPEN=AUDIT/'review'/'direct_reopen_r1.json'
OVERLAY=AUDIT/'review'/'osm_roof_aerial_overlay.jpg'
RENDERS=[AUDIT/'review'/n for n in ('joyful_journeys_hero_r1.png','joyful_journeys_aerial_r1.png')]

def polygon_area(points):
    return abs(sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))/2)

def evaluate():
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
    entries=manifest if isinstance(manifest,list) else manifest.get('buildings',manifest.get('assets',[]))
    entry=next((x for x in entries if x.get('id')==ID),None)
    doc=json.loads(OSM.read_text(encoding='utf-8-sig'))
    elements=doc['elements']; way=next(e for e in elements if e.get('type')=='way' and e.get('id')==869182111)
    nodes={e['id']:e for e in elements if e.get('type')=='node'}
    coords=[(nodes[n]['lon'],nodes[n]['lat']) for n in way['nodes']]
    if coords and coords[0]==coords[-1]: coords=coords[:-1]
    xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in coords]
    area=polygon_area(xy)
    bounds=[min(p[0] for p in xy),min(p[1] for p in xy),max(p[0] for p in xy),max(p[1] for p in xy)]
    src=json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    val=json.loads(VALIDATION.read_text(encoding='utf-8-sig'))
    reopen=json.loads(REOPEN.read_text(encoding='utf-8-sig'))
    renders={p.name:{'exists':p.is_file(),'bytes':p.stat().st_size if p.is_file() else 0} for p in RENDERS}
    ovr={'exists':OVERLAY.is_file(),'bytes':OVERLAY.stat().st_size if OVERLAY.is_file() else 0}
    direct_open_now=False  # Blender MCP was queried; it reported that Blender is not connected.
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':1.8,'max_score':2,'evidence':f"OSM way 869182111 is named Joyful Journeys, tagged day_care, address 600 Lindberg Road; the official operator page independently identifies Joyful Journey at 600 Lindberg Road / Lindberg-Salisbury corner. The 2014 county Z-2571 report identifies the existing single-family home and adult day-care use. Transformed OSM ring has {len(coords)} vertices, area {area:.2f} m², and the saved aerial overlay traces the visible roof perimeter. OSM/crowd map and roof perimeter are not a surveyed wall footprint."},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.7,'max_score':2,'evidence':f"The OSM ring in documented campus approximation has XY bounds [{bounds[0]:.3f},{bounds[1]:.3f}]–[{bounds[2]:.3f},{bounds[3]:.3f}] m and AABB dimensions {bounds[2]-bounds[0]:.2f}×{bounds[3]-bounds[1]:.2f} m. Saved validation reports that campus-coordinate mesh bounds preserve this ring and visually align with the independent Esri aerial; positional transform is identity. The numeric ring comparison is not independent because the baseline asset inherited the same OSM geometry; transform is approximate and source boundary follows roof edge, not confirmed wall line."},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2,'evidence':f"2014 County report supports that the pre-use-change structure was a single-family home; aerial supports a low multi-facet roof and roof-perimeter outline. Neither source supplies a measured height, story count, pitch, or ridge plan. The 7.35 m overall height is an estimate and one-main-level/attic interpretation is unverified. Current render shows a complex roof mass but the exact ridge breaks and pitches are schematic."},
      {'criterion':'Facade, entrances, and distinctive architecture','score':0.5,'max_score':2,'evidence':'No exterior building photograph, elevation, or facade plan is present in the evidence. Official operator page photos are service/home-style icons rather than views of this structure. Light siding, window rhythm, and the Lindberg-facing canopy in the model are unsupported schematic choices; no facade or entrance detail is verified.'},
      {'criterion':'Modular export, portability, and complete evidence','score':1.6,'max_score':2,'evidence':f"Saved r1 Blender 5.2 direct-reopen report states expected scene/collection, one mesh object (662 vertices/162 faces), identity transform, no modifiers, linked libraries, or unpacked images; r1 source/validation records and both renders plus aerial overlay exist ({renders}; overlay {ovr}). The current .blend exists ({ASSET.stat().st_size if ASSET.exists() else 0} bytes), but I could not freshly open it: Blender MCP reported it was not connected. Thus current saved-file structure is supported only by the builder's earlier r1 reopen artifact. Shared manifest bounds remain at 16.0 m while r1 validation has max Z 7.41 m; this grader does not edit the shared manifest."}
    ]
    score=round(sum(c['score'] for c in criteria),1)
    findings=[
      {'severity':'major','finding':'Facade appearance and entrance location are schematic; no structure-specific facade photo or elevation was found.','action':'Retain explicit unverified labels; seek an exterior street photo, property/permit elevation, or operator image of the actual 600 Lindberg building before adding facade claims.'},
      {'severity':'moderate','finding':'Height, exact floor count, roof pitch, and ridge organization are not measured; the model is a low-rise massing estimate.','action':'Keep the 7.35 m height as an estimate and one-main-level/attic form as unverified unless a dimensioned elevation or suitable oblique source is obtained.'},
      {'severity':'moderate','finding':'Footprint match is to OSM roof perimeter, and the baseline may share the same source geometry; exact numerical agreement is not independent geodetic verification.','action':'Use the aerial overlay as visual corroboration and record the footprint as a roof-edge proxy; seek county parcel/building survey if a wall-line claim is required.'},
      {'severity':'review limitation','finding':'This review could not freshly open the saved .blend because Blender MCP is offline. The existing r1 direct-reopen result is prior validation, not a fresh independent reopen.','action':'Repeat the direct reopen when Blender is available; do not treat this grade as passing or current-file-verified until that check completes.'},
      {'severity':'coordinator note','finding':'Shared manifest still records the pre-rebuild 16.0 m vertical bound while r1 asset validation reports 7.41 m maximum.','action':'Coordinator may update the shared manifest after accepting the building revision.'}
    ]
    return {'score':score,'max_score':10,'status':'incomplete_review_below_pass_threshold','criteria':criteria,'evidence':{'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),'asset_exists':ASSET.is_file(),'asset_bytes':ASSET.stat().st_size if ASSET.exists() else 0,'manifest_entry':entry,'source_record_identity':src['building_name'],'source_records':src['sources'],'osm_way':{'id':way['id'],'tags':way.get('tags',{}),'timestamp':way.get('timestamp'),'unique_vertices':len(coords),'area_m2_local_approx':area,'bounds_xy_m':[round(x,6) for x in bounds]},'previous_r1_reopen_report':reopen,'previous_r1_validation':val,'renders':renders,'aerial_overlay':ovr,'fresh_direct_reopen_this_review':direct_open_now},'findings':findings}

if __name__=='__main__':
    result=evaluate()
    (HERE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
