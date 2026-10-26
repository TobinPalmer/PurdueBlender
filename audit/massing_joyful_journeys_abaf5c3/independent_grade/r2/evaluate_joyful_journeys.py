from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4]
ID='massing_joyful_journeys_abaf5c3'
AUDIT=ROOT/'audit'/ID
ASSET=ROOT/'modular'/'buildings'/(ID+'.blend')

def evaluate():
    reopen=json.loads((AUDIT/'independent_grade'/'r2'/'independent_reopen.json').read_text(encoding='utf-8'))
    source=json.loads((AUDIT/'sources'/'source_record.json').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8'))
    entry=next(x for x in manifest['assets'] if x.get('id')==ID)
    obj=reopen['objects'][0]
    actual_bounds=obj['bounds_world_m']
    manifest_bounds=entry['bounds_world_m']
    renders={p.name:{'exists':p.exists(),'bytes':p.stat().st_size if p.exists() else 0} for p in [AUDIT/'review'/'joyful_journeys_hero_r2.png',AUDIT/'review'/'joyful_journeys_aerial_r2.png',AUDIT/'review'/'osm_roof_aerial_overlay.jpg']}
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':1.8,'max_score':2,
       'evidence':'Identity is independently corroborated by OSM way 869182111 (Joyful Journeys, 600 Lindberg Road), the operator page at that address, the 2014 Tippecanoe County Z-2571 staff report, and the 2019 guide exterior photograph whose visible entry number is 600. The 12-point OSM ring visually tracks the roof outline in the saved Esri World Imagery overlay; its source-record area is about 505.66 m². This is a roof/perimeter proxy, not a surveyed wall footprint, and the OSM source does not provide a stated positional accuracy.',
       'uncertainties':['Footprint is crowd-mapped OSM and follows apparent roof edge rather than verified wall line.']},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.7,'max_score':2,
       'evidence':f'Independent Blender reopen measured world bounds X {actual_bounds[0][0]:.3f}..{actual_bounds[0][1]:.3f} m, Y {actual_bounds[1][0]:.3f}..{actual_bounds[1][1]:.3f} m, Z {actual_bounds[2][0]:.3f}..{actual_bounds[2][1]:.3f} m. XY matches the documented conversion of the OSM ring and the ring overlay visually registers with aerial imagery. The saved mesh is in campus coordinates with zero location/rotation and unit scale. Independent survey/control coordinates are unavailable, so the XY and 38.13 x 21.84 m envelope are only as accurate as the approximate local transform and OSM roof polygon.',
       'uncertainties':['No surveyed position or structural wall dimensions; map transform is an approximation.']},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2,
       'evidence':'The 2019 photo supports visible upper-level gable windows and thus a two-level facade interpretation; the aerial supports a low, multi-facet pitched roof. The model records two levels and 8.7 m peak height as estimates. No measured elevation, verified floor count, roof pitch, ridge plan, or eave height was found. The 8.76 m reopened maximum includes the model ridge cap.',
       'uncertainties':['Height, floor count, eave level, pitch, and ridge geometry remain photo/aerial interpretations, not measured facts.']},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2,
       'evidence':'The saved 2019 exterior photo is address-labeled on its page and visibly supports light trim, siding, dark shutters, upper gable windows, and a covered entry/porch. The r2 render includes these broad cues and a south-side entry canopy. The photo is a cropped view of the entry facade and carries no scale or north orientation; the modeled window count/locations, colors, canopy geometry, and all other elevations are schematic. The render does not reproduce the observed porch railing and fuller column/trim details.',
       'uncertainties':['Only a partial, unscaled facade view is available; detailed dimensions and orientation remain unverified.']},
      {'criterion':'Modular export, portability, and complete evidence','score':1.8,'max_score':2,
       'evidence':'I reopened the saved .blend directly in Blender 4.5.15 LTS. It contains the expected scene Building_massing_joyful_journeys_abaf5c3, expected Asset_massing_joyful_journeys_abaf5c3 collection, one Joyful Journeys mesh (886 vertices/218 faces), identity transform, no modifiers, no linked libraries, and no external images. The source record contains raw source snapshots and coordinate/method/uncertainty fields; r2 hero/aerial renders and aerial overlay are present. Deduction: shared manifest still declares Z max 16.0 m while reopened geometry max is 8.76 m, so the coordinator must correct integration bounds.',
       'uncertainties':['Shared manifest bounds are stale and inconsistent with the reopened asset; coordinator correction is needed before integration.']}
    ]
    score=round(sum(c['score'] for c in criteria),1)
    findings=[
      'The r2 facade photograph and fresh direct reopen address key r1 review gaps; this independent result is based on the current r2 asset and evidence.',
      f"Manifest bounds mismatch: manifest Z max={manifest_bounds[2][1]} m, reopened asset Z max={actual_bounds[2][1]} m. Shared-file owner should update bounds before integration.",
      'Roof outline, heights, floor interpretation, and much of the facade remain approximate. Keep those limits explicit in future integration/review.'
    ]
    return {'score':score,'max_score':10,'status':'pass' if score>=8 else 'incomplete_review_below_pass_threshold','criteria':criteria,
      'evidence':{'asset':'modular/buildings/'+ASSET.name,'asset_exists':ASSET.exists(),'asset_bytes':ASSET.stat().st_size if ASSET.exists() else 0,'blender_reopen':reopen,'manifest_entry':entry,'source_record_identity':source.get('building_name'),'source_records':[{'source_id':s['source_id'],'provider':s['provider'],'source_date':s.get('source_date'),'feature_id':s.get('feature_id'),'source_crs':s.get('source_crs'),'method':s.get('method'),'uncertainty':s.get('uncertainty')} for s in source.get('sources',[])],'r2_render_artifacts':renders},'findings':findings}

if __name__=='__main__':
    result=evaluate()
    out=Path(__file__).with_name('result.json')
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
