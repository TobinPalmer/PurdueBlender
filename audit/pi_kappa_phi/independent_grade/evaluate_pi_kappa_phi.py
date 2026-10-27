import hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'modular/buildings/massing_pi_kappa_phi_50e4645.blend'
COMMIT = 'ec62153bbb1f79c8850e9737892dea2baad51ca3'
REL_ASSET = 'modular/buildings/massing_pi_kappa_phi_50e4645.blend'

def evaluate():
    digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    committed = subprocess.check_output(['git','show',f'{COMMIT}:{REL_ASSET}'], cwd=ROOT).decode('ascii')
    pointer_oid = next(line.split(':',1)[1].strip() for line in committed.splitlines() if line.startswith('oid sha256:'))
    build = json.loads((ROOT/'audit/pi_kappa_phi/build_evidence.json').read_text(encoding='utf-8'))
    lifecycle = json.loads((ROOT/'audit/pi_kappa_phi/build_lifecycle_evidence.json').read_text(encoding='utf-8'))
    gis = json.loads((ROOT/'audit/pi_kappa_phi/sources/purdue_gis_FID799_wgs84.json').read_text(encoding='utf-8'))
    feature = gis['features'][0]
    ring = feature['geometry']['rings'][0]
    log = (ROOT/'audit/pi_kappa_phi/fresh_reopen_validation.log').read_text(encoding='utf-8')
    criteria = [
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2,
       'evidence':['Purdue GIS snapshot feature FID 799 identifies Pi Kappa Phi at 330 N Grant; official chapter history and Purdue BoilerLink corroborate chapter/address.','Build script uses that feature ring directly for the wall perimeter; build evidence reports transformed plan dimensions 16.4906 by 23.2054 m and 341.9657 m2.','Official 2019 and 2023 photos show the same post-fire house at the address.'],'findings':['Footprint confidence is strong for identity/location, but source Shape__Area/Shape__Length conflict with coordinate-derived measures; builder appropriately records and avoids using those attributes.']},
      {'name':'Position, orientation, and scale/dimensions','score':1.9,'max_score':2,
       'evidence':['GIS WGS84 footprint transformed with the documented campus approximation; candidate world XY bounds match transformed polygon extent (300.1518–317.6823 E, -89.3119–-65.6666 N).','West/front orientation is supported by BZA staff report west setback along Grant Street.','Fresh-reopen log records finite evaluated bounds matching the candidate dimensions.'],'findings':['No surveyed control point or explicit independent placement-marker cross-check is in this massing asset review; campus coordinate approximation has small systematic uncertainty.']},
      {'name':'Evidence-backed height, floors, and roof form','score':1.3,'max_score':2,
       'evidence':['2019/2023 photos show two occupied levels, attic/dormer elements, and intersecting gabled roof forms.','Candidate carries the GIS plan to 9.4 m estimated wall height and 14.0 m maximum roof height; evidence labels heights as estimates, not measurements.'],'findings':['No measured elevation or confirmed story count was retrieved. Roof pitches, ridge heights, and dormer proportions are inferred. Aerial render combines broad roof planes and does not establish concealed roof geometry.']},
      {'name':'Facade, entrances, and distinctive architecture','score':1.2,'max_score':2,
       'evidence':['Official chapter photos support pale gray stone cladding, paired round-headed entrance openings, repeated dark windows, gabled wings, and central dormers.','Front preview reproduces paired arches, fenestration rhythm, stone-course motif, gable composition, and four dormers.'],'findings':['Direct image comparison shows the model front is substantially flatter and more regular than the photographed facade: photographed wings and bays have strong depth/setback changes, while most modeled west wall remains one plane. Window positions/proportions and roof transitions are approximate; material is more tan than the source image.']},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2,
       'evidence':['Expected stable asset path, scene, and collection names are present in manifest and build evidence.','Committed fresh-reopen validation log reports Blender 5.2.3, 239 scene/collection mesh objects, expected collection, and finite bounds; the two saved preview renders and structured source/lifecycle registers are present.','Asset is an individual campus-coordinate massing library and the script uses project-relative paths. No external image textures are required by the asset.'],'findings':['The independent grading environment has no Blender executable and the live Blender MCP was unreachable, so I could not personally perform a second fresh reopen. I verified the committed reopen log and exact asset bytes/hash against the target commit.']}
    ]
    score = round(sum(c['score'] for c in criteria), 1)
    result = {'building_id':'massing_pi_kappa_phi_50e4645','candidate_commit':COMMIT,'asset_path':REL_ASSET,'asset_sha256':digest,'commit_lfs_asset_sha256':pointer_oid,'hash_matches_commit':digest==pointer_oid,'score':score,'max_score':10,'pass':score>=8 and digest==pointer_oid,'criteria':criteria,'evidence':{'source_feature_id':feature.get('attributes',{}).get('FID'),'source_ring_vertices':len(ring)-1,'model_object_count':build['model_summary']['object_count'],'model_world_bounds_m':build['model_summary']['world_bounds_m'],'reported_height_status':build['model_summary']['height_status'],'fresh_reopen_log':log.strip(),'rendered_views':['audit/pi_kappa_phi/preview_front.png','audit/pi_kappa_phi/preview_aerial.png'],'independent_inspection':['Compared both rendered views directly with chapter exterior photos from 2019 and 2023.','Verified current .blend SHA256 equals the asset bytes stored in the candidate commit.','Reviewed GIS source snapshot, chapter source register, lifecycle evidence, build script and reopen log.']},'findings':['Passes the 8/10 minimum at the boundary-adjacent score.','Most consequential remaining visual fidelity issue is missing facade depth/bay articulation; height and roof dimensions remain estimates.','Lifecycle decision to model the extant house is appropriately cautious: May 2026 zoning variance approval is not treated as proof of demolition/construction, and August 2026 chapter use is documented.','Independent fresh Blender reopen could not be run in this grader environment; saved candidate validation was reviewed instead.']}
    return result

if __name__ == '__main__':
    result = evaluate()
    out = Path(__file__).with_name('grade_result.json')
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('asset_sha256','commit_lfs_asset_sha256','hash_matches_commit','score','max_score','pass')}, indent=2))

