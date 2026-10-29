"""Independent recomputation of the research order, owners, inputs and artifacts.

Run with Python 3: python -X utf8 research/second_pass/tools/validate_queue.py
Uses only the standard library. Does not edit source/model/placement files.
"""
from pathlib import Path
import json,math,hashlib,re,subprocess,sys
D=Path(__file__).resolve().parents[1];R=D.parents[1]
q=json.loads((D/'queue.json').read_text(encoding='utf-8'))
inputs=json.loads((D/'shared/ranking_input_snapshot.json').read_text(encoding='utf-8'))
old={x['asset']:x for x in inputs['old_queue']}
eligible={x['asset']:x for x in inputs['finished_current']}
rows=q['queue'];excluded=q['excluded_already_second_passed_work'];allrows=rows+excluded
assert len(old)==len(eligible)==len(allrows)==232
assert len(rows)==231 and len(excluded)==1 and excluded[0]['building_id']=='felix_haas_hall'
assert set(old)==set(eligible)=={x['asset'] for x in allrows}
assert len({x['building_id'] for x in allrows})==232
assert sum(x['owner']=='Rossen' for x in allrows)==90
assert q['weights']=={'central_campus_location':70,'campus_prominence':20,'current_grade_shortfall':10}
for row in allrows:
    assert row['owner']==old[row['asset']]['owner']
    assert row['importance']==old[row['asset']]['importance']
    assert row['grade']==eligible[row['asset']]['grade']
    assert math.isfinite(row['grade']) and 0<=row['grade']<=10
    cs=[]
    for a in q['anchors']:
        distance=math.hypot(row['location_xy_m'][0]-a['xy_m'][0],row['location_xy_m'][1]-a['xy_m'][1])
        cs.append(a['maximum_centrality']*(1 if distance<=100 else max(0,(1100-distance)/1000)))
    central=max(cs);grade=max(0,min(1,(9.9-row['grade'])/1.9))
    score=70*central+5*(row['importance']-1)+10*grade
    assert math.isclose(central,row['centrality'],abs_tol=1e-10)
    assert math.isclose(score,row['priority'],abs_tol=1e-9)
expected=sorted(rows,key=lambda x:(-x['priority'],-x['centrality'],-x['importance'],x['grade'],x['name'].casefold(),x['asset']))
assert [x['asset'] for x in rows]==[x['asset'] for x in expected]
assert [x['rank'] for x in rows]==list(range(1,232))
documented=[x for x in rows if x['dossier']]
prepared=[x for x in rows if x['research_status']=='Prepared with gaps']
for x in documented:
    p=D/x['dossier'];assert p.is_file() and p.stat().st_size>3000
    assert x['research_status']!='Queued'
provenance=json.loads((D/'shared/location_source_provenance.json').read_text())
assert hashlib.sha256((D/'shared/official_purdue_buildings_wgs84_snapshot.json').read_bytes()).hexdigest()==provenance['source_sha256']
source_hash_checks=0;clip_checks=0
for folder in (D/'buildings').iterdir():
    if not (folder/'README.md').is_file():continue
    reviewed_path=folder/'sources/reviewed_identity.json'
    if reviewed_path.exists():
        reviewed=json.loads(reviewed_path.read_text(encoding='utf-8'))
        snapshot=D/'shared/official_purdue_buildings_wgs84_snapshot.json'
        assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==reviewed['source_snapshot_sha256']
        official={f['attributes']['FID']:f for f in json.loads(snapshot.read_text(encoding='utf-8'))['features']}
        assert reviewed['building_id']==folder.name and reviewed['status']=='matched'
        assert reviewed.get('review_basis') and reviewed.get('identity_evidence_urls')
        assert reviewed['feature_ids']==[f['attributes']['FID'] for f in reviewed['raw_features']]
        assert all(f==official[f['attributes']['FID']] for f in reviewed['raw_features'])
        queue_row=next(r for r in rows if r['building_id']==folder.name)
        assert queue_row['official_feature_ids']==reviewed['feature_ids']
        assert queue_row['location_xy_m']==reviewed['centroid_xy_m']
    for index in (folder/'sources').glob('*download_index.json'):
        records=json.loads(index.read_text(encoding='utf-8'))
        for row in records:
            if row.get('file') and row.get('sha256'):
                p=index.parent/row['file'];assert p.is_file(),str(p)
                assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],str(p)
                source_hash_checks+=1
    index=folder/'sources/lidar_crop_summary.json'
    if index.exists():
        for row in json.loads(index.read_text()):
            if row.get('clip_repository_path'):
                p=folder/row['clip_repository_path'];assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==row['clip_sha256']
                clip_checks+=1
    for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',(folder/'README.md').read_text(encoding='utf-8')):
        if target.startswith(('https:','http:','#')):continue
        p=folder/target.split('#')[0];assert p.exists(),'Broken dossier link '+str(p)
current=(R/'README.md').read_text(encoding='utf-8')
base=subprocess.check_output(['git','show','67fedb8:README.md'],cwd=R).decode('utf-8')
def outside(text):
    first,rest=text.split('<!-- second-pass-queue:start -->');_,last=rest.split('<!-- second-pass-queue:end -->');return first,last
assert outside(current)==outside(base),'Existing README content outside ranking must be preserved'
for row in rows:
    line=next(x for x in current.splitlines() if x.startswith('| '+str(row['rank'])+' | ') and row['asset'] in x)
    assert f"| {row['priority']:.2f} |" in line and f"| {row['owner']} |" in line
    if row['location_conflict']:assert '[location conflict]' in line
    elif not row['official_feature_ids']:assert '[location proxy]' in line
changed=subprocess.check_output(['git','diff','--name-only','67fedb8'],cwd=R,text=True).splitlines()
assert not any(x.endswith('.blend') or '/build_' in x or x=='modular/manifest.json' for x in changed)
report={'result':'PASS','eligible':232,'queued_for_research':231,'excluded_prior_model':1,'rossen_assignments_preserved':90,'prepared_dossiers':len(prepared),'in_progress_dossiers':len(documented)-len(prepared),'source_hash_checks':source_hash_checks,'point_clip_hash_checks':clip_checks,'unresolved_location_proxies':sum(not x['official_feature_ids'] for x in rows),'location_conflicts':sum(bool(x['location_conflict']) for x in rows),'unavailable_source_assets':sum(not x['asset_available'] for x in rows),'top_five':[x['name'] for x in rows[:5]],'unchanged_models':True,'original_readme_outside_queue_preserved':True}
print(json.dumps(report,indent=2))
if '--write' in sys.argv:
    (D/'validation_latest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
