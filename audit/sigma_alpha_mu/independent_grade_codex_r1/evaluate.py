from __future__ import annotations
import json, math, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
AUDIT=ROOT/'audit'/'sigma_alpha_mu'
OUT=Path(__file__).resolve().parent
ASSET=ROOT/'modular'/'buildings'/'massing_sigma_alpha_mu_930_n_grant.blend'
EXPECTED_SHA='B59AB4D2A6B9E33C4F514CB4AE62BCF840AEB1BFA58D6C50D6F0EB3ACF660447'
def area_centroid(poly):
    cr=[]
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)]; cr.append(p[0]*q[1]-q[0]*p[1])
    a=sum(cr)/2
    return sum((poly[i][0]+poly[(i+1)%len(poly)][0])*cr[i] for i in range(len(poly)))/(6*a),sum((poly[i][1]+poly[(i+1)%len(poly)][1])*cr[i] for i in range(len(poly)))/(6*a),a
def evaluate():
    digest=hashlib.sha256(ASSET.read_bytes()).hexdigest().upper()
    if digest != EXPECTED_SHA: raise RuntimeError(f'Frozen asset checksum mismatch: {digest}')
    asset=json.loads((OUT/'asset_inspection.json').read_text(encoding='utf-8-sig'))
    raw=json.loads((AUDIT/'sources'/'indiana_building_footprints_930_n_grant_2026-10-27.json').read_text(encoding='utf-8-sig'))
    feature=next(f for f in raw['features'] if f['attributes']['objectid']==436512)
    ring=feature['geometry']['rings'][0][:-1]; proj=[]
    for lon,lat in ring:
        proj.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
    cx,cy,signed_area=area_centroid(proj); source=[(x-cx,y-cy) for x,y in proj]
    walls=next(o for o in asset['objects'] if 'LiDAR perimeter' in o['name'])
    base=[(x,y) for x,y,z in walls['world_vertices'] if abs(z)<1e-5]
    distances=[min(math.hypot(x-sx,y-sy) for x,y in base) for sx,sy in source]
    reverse=[min(math.hypot(x-sx,y-sy) for sx,sy in source) for x,y in base]
    err=max(distances+reverse)
    src_x=(min(p[0] for p in source),max(p[0] for p in source)); src_y=(min(p[1] for p in source),max(p[1] for p in source))
    wall_x=(min(p[0] for p in base),max(p[0] for p in base)); wall_y=(min(p[1] for p in base),max(p[1] for p in base))
    manifest=json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8-sig'))
    registered=[x for x in manifest.get('assets',[]) if x.get('id')=='massing_sigma_alpha_mu_930_n_grant']
    roof=next(o for o in asset['objects'] if 'primary gable roof' in o['name'])
    dimensions={'source_bbox_m':[src_x[1]-src_x[0],src_y[1]-src_y[0]],'wall_bbox_m':[wall_x[1]-wall_x[0],wall_y[1]-wall_y[0]],'max_bidirectional_vertex_error_m':err,'computed_source_area_m2':abs(signed_area),'service_area_attribute_m2':feature['attributes'].get('SHAPE__Area')}
    criteria=[
      {'criterion':'Identity and source-backed footprint','points':1.2,'max_points':2,'assessment':'Partial: a dated chapter social post associates Sigma Alpha Mu with 930 N Grant, and county parcel/state footprint data identify a plausible residential building at that address. The post is an event location, not an explicit house/property crosswalk; the latest facility recheck says property identity is not established.'},
      {'criterion':'Position, orientation, and scale/dimensions','points':1.2,'max_points':2,'assessment':f'Footprint orientation and scale agree closely with the official ring (max bidirectional vertex error {err:.6f} m). Geometry is centroid-local around (0,0), but there is no matching manifest entry or collection-instance placement, so campus position is not registered.'},
      {'criterion':'Evidence-backed height, floors, and roof form','points':1.0,'max_points':2,'assessment':'The 2018 photo supports a low, one-story-looking house, dark pitched roof, and chimney; the orthophoto supports a broad roof plan. Eave/ridge values are estimates, listing floor counts conflict, and the roof simplifies the stepped footprint.'},
      {'criterion':'Facade, entrances, and distinctive architecture','points':1.2,'max_points':2,'assessment':'Light siding, red-brown shutters, front entry, pitched roof, and chimney are visible in the listing photo and represented. Window count/spacing and entry surround are estimated; the available photo does not establish attached garage door placement.'},
      {'criterion':'Modular export, portability, and evidence completeness','points':1.4,'max_points':2,'assessment':'The exact asset reopens with the expected named collection and scene (62 objects), previews and source/evidence records; inspection found no collection instance, external libraries, or images. Candidate is absent from modular/manifest.json, so it is not registered for campus integration; source records retain identity/area conflicts.'}
    ]
    score=round(sum(c['points'] for c in criteria),1)
    evidence=[
      {'path':'modular/buildings/massing_sigma_alpha_mu_930_n_grant.blend','observation':f'SHA-256 {digest}; reopened read-only in Blender 5.2.3; scene {asset["scene"]}, collection {asset["collection"]}, {asset["collection_objects"]} objects.'},
      {'path':'audit/sigma_alpha_mu/sources/indiana_building_footprints_930_n_grant_2026-10-27.json','observation':f'Indiana GI Office feature 436512, 2018 LiDAR, EPSG:4326. Independent projection and bidirectional nearest-vertex check against the saved wall base gives {err:.6f} m max error; source bbox {dimensions["source_bbox_m"]} m; ring-derived area {abs(signed_area):.2f} m2.'},
      {'path':'audit/sigma_alpha_mu/sources/parcels_930_n_grant_2026-10-27.json','observation':'County GIS returns 930 N GRANT ST; parcel response has no ownership or occupant crosswalk.'},
      {'path':'audit/sigma_alpha_mu/sources/lead_930_n_grant_provenance_2026-10-27.json','observation':'Dated public chapter post visibly gives 930 N Grant as event location; it supports activity at the address, not explicitly a chapter-house property identity.'},
      {'path':'audit/sigma_alpha_mu/sources/tippecanoe_2018_orthophoto_930_n_grant.jpg and audit/sigma_alpha_mu/sources/redfin_2018_listing_exterior_930_n_grant.jpg','observation':'Direct visual review: orthophoto roof partly obscured by trees; listing photo shows a low light-sided house with dark pitched roof, shutters, entry, chimney. No exact heights or all elevations.'},
      {'path':'audit/sigma_alpha_mu/preview.png and audit/sigma_alpha_mu/roof_plan_view.png','observation':'Current previews show a coherent low massing model and simplified gable roof over stepped outline; no campus/site context.'},
      {'path':'modular/manifest.json','observation':f'No stable-ID entry found among {len(manifest.get("assets",[]))} entries; placement/integration is absent.'},
      {'path':'audit/sigma_alpha_mu/current_facility_recheck_2026-10-27.md and audit/sigma_alpha_mu/model_evidence.md','observation':'Reviewed both recheck and model evidence; recheck says exact property identity remains unresolved, while model evidence uses a chapter event location.'}
    ]
    findings=[
      'Score is below the 8/10 passing threshold; deductions reflect incomplete property identity, unregistered campus placement, and estimated height/roof/facade details.',
      'The state footprint does not establish Sigma Alpha Mu occupancy by itself. Chapter post provides an address association as an event location; current facility recheck says no property crosswalk is established.',
      f'The GIS SHAPE__Area field ({feature["attributes"].get("SHAPE__Area"):.2f} m2) conflicts with area computed from returned ring ({abs(signed_area):.2f} m2); the model follows ring geometry.',
      'Model geometry is centroid-local, but there is no manifest entry/instance placement. Campus position is not represented in the modular integration system.',
      'The 2018 exterior image is a single secondary-source view; heights, story count, window rhythm, garage-door location, and exact roof form remain estimates. Listing sources conflict on stories.'
    ]
    return {'score':score,'max_score':10,'criteria':criteria,'evidence':evidence,'findings':findings,'method':{'evaluator':'independent_grader_codex_r1.evaluate','asset_sha256':digest,'asset_checksum_matches_builder':digest==EXPECTED_SHA,'blender_inspection':'Saved .blend opened read-only in Blender 5.2.3; scene, export collection and evaluated mesh vertices inspected. Source footprint projected independently using repository tangent approximation and compared by bidirectional nearest-vertex error. Visual review used current previews and raw image snapshots.','manifest_entry_found':bool(registered),'footprint_metrics':dimensions,'roof_peak_m':round(max(v[2] for v in roof['world_vertices']),3),'external_libraries':asset.get('libraries',[]),'images':asset.get('images',[]),'parcel_address':'930 N GRANT ST'}}
if __name__=='__main__':
    result=evaluate(); (OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2,ensure_ascii=False))

