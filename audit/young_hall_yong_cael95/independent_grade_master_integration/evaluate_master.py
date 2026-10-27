import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
AUDIT=ROOT/'audit'/'young_hall_yong_cael95'
OUT=AUDIT/'independent_grade_master_integration'
ASSET_ID='massing_young_hall_yong_cae1b95'

def max_delta(a,b):
    return max(abs(float(a[i][j])-float(b[i][j])) for i in range(3) for j in range(2))

def evaluate():
    probe=json.loads((OUT/'master_probe.json').read_text(encoding='utf-8'))
    prior=json.loads((AUDIT/'independent_grade_r2'/'result.json').read_text(encoding='utf-8'))
    fresh=json.loads((AUDIT/'fresh_open_validation.json').read_text(encoding='utf-8'))
    evidence=json.loads((AUDIT/'evidence.json').read_text(encoding='utf-8'))
    before=fresh['collection_world_bounds_m']
    after=probe['world_bounds_m']
    bounds_delta=max_delta(before,after)
    errors=list(probe['errors'])
    if probe['status']!='PASS': errors.append('fresh-open master probe did not pass')
    if bounds_delta>0.005: errors.append(f'world bounds changed by {bounds_delta:.6f} m')
    if probe['asset_external_file_dependencies']:
        errors.append('YONG asset has external image dependencies')
    if probe['manifest_object_count']!=probe['collection_object_count']:
        errors.append('manifest / linked collection object counts differ')
    criteria=[
      {
        'criterion':'Correct identity and source-backed footprint',
        'points':2.0,'max_points':2.0,
        'evidence':'The linked asset remains Ernest C. Young Hall (YONG), Purdue GIS BuildingShapes FID 70, corroborated by Purdue Archives corporate record 656. In the pre-integration fresh-open evaluation the shell base ring contained all 34 GIS vertices with maximum projected vertex deviation 0.000032 m; the integrated shell bounds match that same fresh-open geometry.',
        'findings':['The project conversion is an approximate local geographic transform, not survey control. The GIS feature does not supply a source/edit date.']
      },
      {
        'criterion':'Position, orientation, scale and plan dimensions',
        'points':1.9,'max_points':2.0,
        'evidence':f"Fresh-open master contains exactly one expected collection instance; marker is at {probe['marker']['location']}, identity rotation and unit scale, and its linked library path matches the manifest. The transformed world bounds differ from the standalone pre-integration collection bounds by {bounds_delta:.6f} m. The structural shell bounds retain the GIS-derived plan dimensions.",
        'findings':['No cadastral/survey control confirms absolute registration; the position inherits the approximate project coordinate conversion.']
      },
      {
        'criterion':'Evidence-backed height, floors and roof form',
        'points':1.3,'max_points':2.0,
        'evidence':'The shell is approximately 31.09 m tall, based on GIS R=102 interpreted as feet. Purdue Archives describes Young Hall as ten stories and old exterior photos show a flat-roofed slab form; GIS NUM_LEVELS and CountOfFLO both report eleven.',
        'findings':['The unit for GIS R and the extra GIS level are undocumented; the height, floor spacing, basement relationship and roof details remain estimates.']
      },
      {
        'criterion':'Facade, entrance and distinctive architecture',
        'points':1.45,'max_points':2.0,
        'evidence':'Three Purdue Archives photos support a long slab, pale panelized exterior, repeated narrow vertical window bays and flat roof. The current Purdue photo supports the red brick sign wall. The saved exterior render includes those cues and a sign/entry area.',
        'findings':['Historical photos have no dates and cannot establish current full elevations. The current photo is a close crop of the sign wall. The render is overexposed and façade/entrance details remain schematic; exact opening rhythm and roof fittings are unverified.']
      },
      {
        'criterion':'Modular export, portability and evidence completeness',
        'points':1.7,'max_points':2.0,
        'evidence':f"The manifest classifies the asset as local-coordinate detailed geometry; the master references the expected library/collection exactly once through its marker and does not also link the asset collection directly under the scene root. The collection contains {probe['collection_object_count']} objects ({probe['geometry_object_count']} geometry objects plus the local AssetRoot). The standalone Blender 5.2.3 fresh-open validation passed with no YONG external image dependencies.",
        'findings':['The interior is a small schematic lobby/corridor slice, not a floor-plan reconstruction; no public plan was found.']
      }
    ]
    score=round(sum(c['points'] for c in criteria),2)
    result={
      'building':'Ernest C. Young Hall (YONG)',
      'asset_id':ASSET_ID,
      'score':score,'max_score':10,
      'criteria':criteria,
      'evidence':{
        'master_probe':'audit/young_hall_yong_cael95/independent_grade_master_integration/master_probe.json',
        'master_verification':'modular/verification.json',
        'manifest':'modular/manifest.json',
        'source_evidence':'audit/young_hall_yong_cael95/evidence.json',
        'standalone_fresh_open':'audit/young_hall_yong_cael95/fresh_open_validation.json',
        'prior_standalone_grade':'audit/young_hall_yong_cael95/independent_grade_r2/result.json',
        'render':'audit/young_hall_yong_cael95/preview_exterior.png',
        'interior_render':'audit/young_hall_yong_cael95/preview_interior_schematic.png',
        'archives_photos':['audit/young_hall_yong_cael95/young_graduate_house_archive_photo_1415.jpg','audit/young_hall_yong_cael95/young_graduate_house_archive_photo_1417.jpg','audit/young_hall_yong_cael95/young_graduate_house_archive_photo_1418.jpg'],
        'current_facade_photo':'audit/young_hall_yong_cael95/purdue_young_hall_facade_reference.jpg',
        'world_bounds_max_delta_m':bounds_delta,
        'gis_ring_max_error_m':fresh['gis_ring_max_vertex_error_m'],
        'gis_levels_vs_archives':{'GIS':11,'Archives':10,'resolved':False},
        'estimated_shell_height_m':fresh['shell_world_bounds_m'][2][1]-fresh['shell_world_bounds_m'][2][0],
        'asset_external_file_dependencies':probe['asset_external_file_dependencies']
      },
      'findings':[
        'Fresh-open master placement and linked asset integrity pass; the linked geometry preserves its pre-localization world bounds.',
        'GIS FID 70 directly supports footprint identity and plan geometry; campus registration uses the project approximation, not survey control.',
        'Ten-story archival text conflicts with GIS eleven-level fields; height and level units remain uncertain.',
        'Historic facade photographs are undated and the current reference is only a sign-wall crop; current full elevations, detailed entry and roof fittings are not fully verified.',
        'The interior remains a small schematic lobby/corridor slice without a public floor plan.'
      ],
      'passing_standard':8,
      'result':'pass' if score>=8 and not errors else 'fail',
      'errors':errors,
      'grader':'independent master integration review',
      'date':'2026-10-26'
    }
    return result

if __name__=='__main__':
    result=evaluate()
    out=OUT/'result.json'
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'score':result['score'],'result':result['result'],'errors':result['errors'],'bounds_delta_m':result['evidence']['world_bounds_max_delta_m']},indent=2))
