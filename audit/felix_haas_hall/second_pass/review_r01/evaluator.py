"""Independently assessed visual points plus reproducible saved-asset checks.

The criterion awards below record the reviewer's direct inspection of the cited
photographs and all nine saved render views. They are not automated fidelity claims.
The evaluator verifies inputs, sums the awards and applies the acceptance gates.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json

D=Path(__file__).resolve().parent
P=D.parent
ROOT=D.parents[3]
SHA='445c1499ef1b1c0bb2c5520304cff9784a572e0478abcc17a72157f951ba88f4'
ASSET=ROOT/'modular/buildings/felix_haas_hall.blend'
VIEWS=['east','west','north','south','southeast','northwest','roof','west_windows','entrance']

def evaluate():
    assert hashlib.sha256(ASSET.read_bytes()).hexdigest()==SHA,'Saved asset changed; this review applies only to the recorded revision.'
    baseline=json.loads((D/'baseline_inspection.json').read_text())
    current=json.loads((D/'current_inspection.json').read_text())
    assert current['asset_sha256']==SHA
    renders=json.loads((P/'revision_r01/render_settings.json').read_text())
    assert renders['asset_sha256']==SHA
    for view in VIEWS:assert (P/f'revision_r01/renders/{view}.png').stat().st_size>1000
    old={o['name']:o for o in baseline['objects']}
    new={o['name']:o for o in current['objects']}
    common=set(old)&set(new)
    modified=[n for n in sorted(common) if old[n]!=new[n]]
    assert not modified
    assert len(common)==863 and len(set(old)-set(new))==56 and len(set(new)-set(old))==396
    assert sum(n.startswith('HAAS_SP_West_Upper_') and n.endswith('_Glass') for n in new)==9
    assert sum(n.startswith('HAAS_SP_West_Middle_') and n.endswith('_Glass') for n in new)==9
    source_names=['purdue_events_front.jpg','haas_hall_today_2017.jpg','maps_front_mike_a_2016.png','maps_side_jay_discovery_2016.png','maps_corner_mike_a_2015.png','streetview_university_entry_apr2026.png','streetview_west_upper_apr2026.png']
    for name in source_names:assert (P/'sources'/name).stat().st_size>1000
    criteria=[
      {'criterion':'Windows/openings on all elevations','max_points':3.0,'awarded_points':1.5,
       'evidence':['sources/maps_side_jay_discovery_2016.png','sources/streetview_west_upper_apr2026.png','sources/purdue_events_front.jpg','sources/maps_corner_mike_a_2015.png','revision_r01/renders/west.png','revision_r01/renders/west_windows.png','revision_r01/renders/east.png','revision_r01/renders/north.png','revision_r01/renders/south.png'],
       'findings':'Nine west upper groups and nine narrow middle openings restore a supported three-register rhythm. The front upper glass is hidden/blocked in the rendered asset; north and south remain blank simplified panels. West middle full pale jambs and generic basement windows do not match the photographed sill/keystone and basement register. Exact bay positions and opening dimensions remain estimates.'},
      {'criterion':'Signature architecture','max_points':2.5,'awarded_points':1.25,
       'evidence':['sources/purdue_events_front.jpg','sources/streetview_university_entry_apr2026.png','sources/streetview_west_upper_apr2026.png','revision_r01/renders/entrance.png','revision_r01/renders/west_windows.png','revision_r01/renders/southeast.png'],
       'findings':'The entrance stair, pale surrounds, central pavilion and west upper stepped frame cues are recognizable. Front arches are semicircular instead of the shallow segmental profiles shown in the source. The west door needs its transom, realistic frame division and recessed/downward approach; eave brackets and facade masonry/stone motifs remain simplified.'},
      {'criterion':'Proportions, wings, roof and silhouette','max_points':2.0,'awarded_points':1.5,
       'evidence':['sources/maps_side_jay_discovery_2016.png','sources/maps_corner_mike_a_2015.png','revision_r01/renders/roof.png','revision_r01/renders/northwest.png','revision_r01/renders/southeast.png','review_r01/baseline_inspection.json','review_r01/current_inspection.json'],
       'findings':'The broad hipped red roof and projecting entry pavilion are retained, with exact preservation of the GIS shell and roof geometry in this revision. Eave depth/details, absolute height and facade/roof proportions are not established by calibrated elevation or complete exterior evidence.'},
      {'criterion':'Materials, color, scale, trim and depth','max_points':1.5,'awarded_points':0.65,
       'evidence':['sources/purdue_events_front.jpg','sources/streetview_university_entry_apr2026.png','sources/streetview_west_upper_apr2026.png','revision_r01/renders/west_windows.png','revision_r01/renders/entrance.png','revision_r01/renders/north.png'],
       'findings':'Red-brown masonry, pale stone and dark west glazing are plausible basic materials. The broad pale limestone basement zone remains brick in the model, front pale surfaces suppress photographed brick inlay articulation, upper front glazing appears opaque pale, and some retained masonry mapping is stretched. West glazing is surfaced onto a solid backing rather than having a verified wall opening/recess.'},
      {'criterion':'Whole-building consistency across elevations and obliques','max_points':1.0,'awarded_points':0.3,
       'evidence':['sources/maps_corner_mike_a_2015.png','sources/haas_hall_today_2017.jpg','revision_r01/renders/north.png','revision_r01/renders/south.png','revision_r01/renders/northwest.png','revision_r01/renders/southeast.png'],
       'findings':'The west facade is materially more legible than the baseline. The remaining elevations retain substantially lower detail and large blank areas. No complete current north elevation or calibrated full-building reference set supports whole-building acceptance.'}
    ]
    findings=[
      {'id':'F01','severity':'required revision','facade':'east/front upper windows','finding':'The three pavilion upper windows render as pale blocked panels; glass meshes HAAS_Photo_Glazing_-7.65_7.7, HAAS_Photo_Glazing_0_7.7 and HAAS_Photo_Glazing_7.65_7.7 lie at X=12.76–12.82 behind facade/jamb geometry near X=13.0–13.25.','required_correction':'Create correct openings/recesses and dark visible glazing/mullions, then re-render from a matched front oblique. Do not fix by recoloring the blocking stone.'},
      {'id':'F02','severity':'required revision','facade':'west basement','finding':'The real pale limestone register extends around the basement windows/door with rectangular red-brick insets; the model adds only a thin stripe while retaining a predominantly brick basement.','required_correction':'Rebuild the west basement stone/brick distribution and frame/recess relationships from the current entrance and 2016 elevated views.'},
      {'id':'F03','severity':'required revision','facade':'west middle windows and west entrance','finding':'Full pale window jambs are too heavy relative to the narrow dark openings with sill and keystone in Street View. The door lacks the upper transom and recessed approach.','required_correction':'Use the photographed middle-window trim profile and door/transom proportions; confirm the door bay with a footprint/plan comparison rather than a guessed station.'},
      {'id':'F04','severity':'required revision','facade':'east/front arches and stone/brick articulation','finding':'The model has semicircular arch profiles and broad pale blank wall areas; the reference has shallow segmental openings and more precise alternating masonry/stone inlays.','required_correction':'Match arch rise/profile and surrounding brick panels/quoins against the official exterior photograph. Preserve the entrance silhouette while refining it.'},
      {'id':'F05','severity':'required research and revision','facade':'north and south','finding':'Both rendered elevations remain near-blank grids; the winter oblique shows at least the visible side has upper and basement windows, not a wholly blank wall. The opposite elevation remains insufficiently documented.','required_correction':'Obtain distinct, correctly oriented elevation/corner views and model their actual openings. Do not mirror west windows onto unseen walls as a substitute for evidence.'},
      {'id':'F06','severity':'remaining uncertainty','facade':'roof/eaves and overall proportions','finding':'A broad hipped red roof is supported, but roof/eave dimensions, fine tile/eave details and absolute facade heights remain uncalibrated estimates.','required_correction':'Use additional roof/aerial views or elevations to refine supported details; retain explicit uncertainty where metric evidence is absent.'}
    ]
    gates={
      'correct_identity':{'passed':True,'evidence':'Official Purdue Events place and source image identify Felix Haas Hall; stable asset/collection retained.'},
      'adequate_exterior_reference_coverage':{'passed':False,'evidence':'East/front and west are documented; a partial oblique gives side evidence. No complete current north/south coverage or calibrated roof/elevation set is present.'},
      'no_unresolved_material_exterior_discrepancies':{'passed':False,'evidence':'F01–F05 are visible material discrepancies, not merely dimensional uncertainty.'},
      'saved_file_reopen':{'passed':True,'evidence':'Opened exact SHA independently in Blender 5.2.3; current_inspection.json.'},
      'expected_collection_export':{'passed':current['expected_collection_present'] and current['collection_name']=='Asset_felix_haas_hall','evidence':'Expected named collection contains 1,259 objects; source library successfully opens.'},
      'portable_dependencies':{'passed':not current['libraries'] and not current['images'],'evidence':'No external libraries or images found in the saved library.'},
      'no_regression_to_verified_footprint_orientation_scale':{'passed':not modified,'evidence':'863 retained objects have identical mesh topology/coordinates, matrices, bounds, material names and render flags versus the exact baseline. Only 56 prior west attachments removed and 396 west additions made.'},
      'master_integration':{'passed':None,'evidence':'Not reviewed or edited; separate Tobin/coordinator gate after a source revision passes.'}
    }
    total=round(sum(c['awarded_points'] for c in criteria),10)
    required=[v['passed'] for k,v in gates.items() if k!='master_integration']
    return {'building_id':'felix_haas_hall','revision':'exterior_r01','asset_path':'modular/buildings/felix_haas_hall.blend','asset_sha256':SHA,'reviewer':'Independent second-pass visual review subagent /root/haas_exterior_review','reviewed_at':datetime.now(timezone.utc).isoformat(),'score':total,'max_score':10,'criteria':criteria,'evidence':['review_r01/current_inspection.json','review_r01/baseline_inspection.json']+[f'sources/{n}' for n in source_names],'reviewed_views':[f'revision_r01/renders/{n}.png' for n in VIEWS],'findings':findings,'uncertainties':['Photo capture dates span 2015/2016/2017 and April 2026; only the west has a clearly current dated Street View.','No complete facade-by-facade current reference coverage.','Photo-derived widths, heights, bay positions, roof/eave dimensions and door station are estimates.','Master integration was not inspected.'],'gates':gates,'acceptance_threshold':9.9,'threshold_approval':None,'accepted':total>=9.9 and all(required),'automated_checks':{'retained_objects_identical':len(common),'retained_objects_changed':modified,'removed_old_west_objects':56,'added_west_objects':396,'upper_west_window_groups':9,'middle_west_windows':9},'asset_modified_by_reviewer':False}

if __name__=='__main__':
    result=evaluate()
    (D/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'score':result['score'],'threshold':result['acceptance_threshold'],'accepted':result['accepted'],'saved_asset_hash_verified':True}))
